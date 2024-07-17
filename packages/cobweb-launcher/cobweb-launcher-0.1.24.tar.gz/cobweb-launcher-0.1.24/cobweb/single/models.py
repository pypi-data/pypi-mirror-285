import time
from cobweb import log, Queue, Seed, Setting
from cobweb.utils import issubclass_cobweb_inf
# from pympler import asizeof


class Scheduler:

    def schedule_seed(self, ready_seed_length, get_scheduler_lock, add_seed):

        inf_name = "SchedulerInterface"
        if not issubclass_cobweb_inf(self.__class__, inf_name):
            raise Exception("not have schedule function!")

        if self.__class__.__name__ == "Default":
            self.stop = True
            return None

        while not self.stop:
            length = ready_seed_length()
            if length > self.size:
                time.sleep(15)

            elif get_scheduler_lock():
                seeds = self.schedule()
                add_seed(seeds)

        log.info(f"close thread: schedule_seed")

    def schedule_task(self, stop, get_seed, ready_seed_length):
        time.sleep(3)
        while not stop.is_set():

            if not ready_seed_length():
                time.sleep(Setting.SCHEDULER_WAIT_TIME)
                continue

            if self.queue.length >= self.length:
                time.sleep(Setting.SCHEDULER_BLOCK_TIME)
                continue

            seeds = get_seed(self.length)
            self.queue.push(seeds)
        log.info(f"close thread: schedule_task")


class Spider:

    def __init__(self, queue, max_retries=5):
        self.spider_in_progress = Queue()
        self.max_retries = max_retries
        self.queue = queue

    def spider_task(self, stop, func, item, del_seed):
        while not stop.is_set():
            seed = self.queue.pop()
            if not seed:
                time.sleep(Setting.SPIDER_WAIT_TIME)
                continue
            elif seed._retry >= self.max_retries:
                del_seed(seed, spider_status=False)
                continue
            try:
                self.spider_in_progress.push(1, direct_insertion=True)
                # log.info("spider seed: " + str(seed))
                ret_count = 0
                status = None
                for it in func(item, seed):
                    ret_count += 1
                    if getattr(it, "table_name", None):
                        store_queue = it.queue()
                        store_queue.push(
                            [seed, it.struct_data],
                            direct_insertion=True
                        )
                    elif isinstance(it, Seed):
                        self.queue.push(it)
                    elif any(isinstance(it, t) for t in (list, tuple)):
                        self.queue.push([s if isinstance(s, Seed) else Seed(s) for s in it])
                    elif isinstance(it, bool):
                        status = it

                if status:
                    del_seed(seed, spider_status=True)
                elif not ret_count or status is False:
                    seed._retry += 1
                    self.queue.push(seed)

            except Exception as e:
                seed._retry += 1
                self.queue.push(seed)
                log.info(f"{str(seed)} -> {str(e)}")
            finally:
                self.spider_in_progress.pop()
        log.info(f"close thread: spider")


class Storer:

    def store_task(self, stop, last, reset_seed, del_seed):

        inf_name = "StorerInterface"
        if not issubclass_cobweb_inf(self.__class__, inf_name):
            return None

        if not getattr(self, "store", None):
            raise Exception("not have store function!")

        storer_name = self.__class__.__name__ + self.table

        while not stop.is_set():

            if last.is_set() or self.queue.length >= self.length:
                seeds, data_list = [], []

                for _ in range(self.length):
                    items = self.queue.pop()
                    if not items:
                        break
                    seed, data = items
                    seeds.append(seed)
                    data_list.append(data)

                if data_list:
                    if self.store(data_list):
                        del_seed(seeds)
                    else:
                        reset_seed(seeds)
                        log.info("reset seeds!")
                    continue

            time.sleep(3)

        log.info(f"close thread: {storer_name}")
