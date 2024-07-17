import time
import redis
from . import log, decorators, Seed, Setting, DealModel
# from cobweb.decorators import decorators.check_redis_status
# from cobweb.constant import Setting, DealModel


class RedisDB:

    def __init__(
            self,
            project: str,
            task_name: str,
            config: dict,
    ):
        pool = redis.ConnectionPool(**config)
        self.heartbeat_key = f"{project}:{task_name}:heartbeat"  # redis type string
        self.spider_key = f"{project}:{task_name}:seed_info:spider"  # redis type zset, .format(priority)
        self.storer_key = f"{project}:{task_name}:seed_info:storer:%s"  # redis type set,
        self.failed_key = f"{project}:{task_name}:seed_info:failed"  # redis type set, .format(priority)
        self.succeed_key = f"{project}:{task_name}:seed_info:succeed"  # redis type set, .format(priority)
        self.update_lock = f"{project}:{task_name}:update_seed_lock"  # redis type string
        self.check_lock = f"{project}:{task_name}:check_seed_lock"  # redis type string
        self.scheduler_lock = f"{project}:{task_name}:scheduler_lock"  # redis type string
        self.client = redis.Redis(connection_pool=pool)

    @decorators.check_redis_status
    def _get_lock(self, key, t=15, timeout=3, sleep_time=0.1):
        begin_time = int(time.time())
        while True:
            if self.client.setnx(key, ""):
                self.client.expire(key, t)
                return True
            if int(time.time()) - begin_time > timeout:
                break
            time.sleep(sleep_time)

        if self.client.ttl(key) == -1:
            delete_status = True
            for _ in range(3):
                if self.client.ttl(key) != -1:
                    delete_status = False
                    break
                time.sleep(0.5)
            if delete_status:
                self.client.expire(key, t)
            return False
        else:
            ttl = self.client.ttl(key)
            log.info("ttl: " + str(ttl))
            return False

    @decorators.check_redis_status
    def _deal_seed(self, seeds, is_add: bool):
        if not seeds:
            return None

        if not isinstance(seeds, list):
            seeds = [seeds]

        item_info = dict()

        for seed in seeds:
            if not isinstance(seed, Seed):
                seed = Seed(seed)
            item_info[seed.format_seed] = seed._priority

        if item_info:
            self.client.zadd(self.spider_key, mapping=item_info, nx=is_add, xx=not is_add)

    @decorators.check_redis_status
    def add_seed(self, seeds):
        self._deal_seed(seeds, is_add=True)

    @decorators.check_redis_status
    def reset_seed(self, seeds):
        self._deal_seed(seeds, is_add=False)

    @decorators.check_redis_status
    def del_seed(self, seeds, spider_status: bool = True):
        if not seeds:
            return None

        if not isinstance(seeds, list):
            seeds = [seeds]

        seeds = [seed if isinstance(seed, Seed) else Seed(seed) for seed in seeds]

        if seeds:
            if spider_status and Setting.DEAL_MODEL in [DealModel.success, DealModel.polling]:
                self.client.sadd(self.succeed_key, *(seed.format_seed for seed in seeds))
            elif not spider_status:
                self.client.sadd(self.failed_key, *(str(seed) for seed in seeds))
            self.client.zrem(self.spider_key, *(seed.format_seed for seed in seeds))

    @decorators.check_redis_status
    def set_storer(self, key, seeds):
        if not seeds:
            return None

        if not isinstance(seeds, list):
            seeds = [seeds]

        item_info = dict()
        score = -int(time.time())
        for seed in seeds:
            if not isinstance(seed, Seed):
                seed = Seed(seed)
            item_info[seed.format_seed] = score

        if item_info:
            self.client.zadd(self.storer_key % key, mapping=item_info)
            log.info(f"zadd storer key: length {len(item_info.keys())}")

    @decorators.check_redis_status
    def get_seed(self, length: int = 200):
        cs = time.time()

        if self._get_lock(key=self.update_lock):

            update_item, result = {}, []

            version = int(time.time())

            items = self.client.zrangebyscore(self.spider_key, min=0, max="+inf", start=0, num=length, withscores=True)

            for value, priority in items:
                score = -(version + int(priority) / 1000)
                seed = Seed(value, priority=priority, version=version)
                update_item[value] = score
                result.append(seed)

            log.info("set seeds into queue time: " + str(time.time() - cs))
            if result:
                self.client.zadd(self.spider_key, mapping=update_item, xx=True)

            self.client.delete(self.update_lock)
            log.info("push seeds into queue time: " + str(time.time() - cs))
            return result

    @decorators.check_redis_status
    def check_spider_queue(self, stop, storer_num):
        while not stop.is_set():
            # 每15s获取check锁,等待600s后仍获取不到锁则重试;获取到锁后，设置锁的存活时间为${cs_lct}s
            if self._get_lock(key=self.check_lock, t=Setting.CHECK_LOCK_TIME, timeout=600, sleep_time=3):
                heartbeat = True if self.client.exists(self.heartbeat_key) else False
                # 重启重制score值，否则获取${rs_time}分钟前的分数值
                score = -int(time.time()) + Setting.RESET_SCORE if heartbeat else "-inf"

                keys = self.client.keys(self.storer_key % "*")

                if keys and len(keys) >= storer_num:
                    intersection_key = self.storer_key % "intersection"
                    self.client.delete(intersection_key)
                    self.client.zinterstore(intersection_key, keys)

                    while True:
                        members = self.client.zrange(intersection_key, 0, 1999)
                        if not members:
                            break
                        for key in keys:
                            self.client.zrem(key, *members)
                        if Setting.DEAL_MODEL in [DealModel.success, DealModel.polling]:
                            self.client.sadd(self.succeed_key, *members)
                        self.client.zrem(self.spider_key, *members)
                        self.client.zrem(intersection_key, *members)
                        log.info("succeed spider data ...")

                for key in keys:
                    self.client.zremrangebyscore(key, min=score, max="(0")

                while True:
                    items = self.client.zrangebyscore(self.spider_key, min=score, max="(0", start=0, num=5000, withscores=True)
                    if not items:
                        break
                    reset_items = {}
                    for value, priority in items:
                        reset_score = "{:.3f}".format(priority).split(".")[1]
                        reset_items[value] = int(reset_score)
                    if reset_items:
                        self.client.zadd(self.spider_key, mapping=reset_items, xx=True)

                if not heartbeat:
                    self.client.setex(self.heartbeat_key, 15, "")

    @decorators.check_redis_status
    def set_heartbeat(self, stop):
        time.sleep(5)
        while not stop.is_set():
            self.client.setex(self.heartbeat_key, 5, "")
            time.sleep(3)

    # @decorators.check_redis_status
    # def heartbeat(self):
    #     """
    #     返回心跳key剩余存活时间
    #     """
    #     return self.client.ttl(self.heartbeat_key)

    @decorators.check_redis_status
    def spider_queue_length(self):
        return self.client.zcard(self.spider_key)

    @decorators.check_redis_status
    def ready_seed_length(self):
        return self.client.zcount(self.spider_key, min=0, max="+inf")

    @decorators.check_redis_status
    def get_scheduler_lock(self):
        return self._get_lock(self.scheduler_lock)
