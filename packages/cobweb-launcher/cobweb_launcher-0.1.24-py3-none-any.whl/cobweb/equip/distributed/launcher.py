import time
import threading

from .. import log, sqn, rtn, pim
from .. import Queue, DBItem, RedisDB, Setting
from .models import Scheduler, Spider, Storer


def check(stop, last, spider, scheduler, storer_list, ready_seed_length, spider_queue_length):
    log.info("run check thread after 30 seconds...")
    time.sleep(30)
    spider_info = """
------------------- check: {0} ------------------
            running_spider_thread_num: {1}
            redis_ready_seed_length:   {2}
            redis_spider_seed_length:  {3}
            memory_seed_queue_length:  {4}
            storer_upload_queue_length_info: 
                {5}
-----------------------  end  -----------------------"""
    while True:
        status = "running"
        running_spider_thread_num = spider.spider_in_progress.length
        redis_ready_seed_length = ready_seed_length()
        redis_spider_seed_length = spider_queue_length()
        memory_seed_queue_length = scheduler.queue.length
        storer_upload_queue_list = []
        for storer in storer_list:
            storer_upload_queue_list.append(
                f"{storer.__class__.__name__} storer queue length: {storer.queue.length}"
            )
        if (
                scheduler.stop and
                not memory_seed_queue_length and
                not running_spider_thread_num
        ):
            if not Setting.LAUNCHER_MODEL:
                log.info("spider is done?")
            last.set()
            time.sleep(3)
            storer_queue_empty = True
            storer_upload_queue_list = []
            for storer in storer_list:
                if storer.queue.length:
                    storer_queue_empty = False
                storer_upload_queue_list.append(
                    f"{storer.__class__.__name__} storer queue length: {storer.queue.length}"
                )
            if (
                    storer_queue_empty and
                    not redis_ready_seed_length and
                    not redis_spider_seed_length
            ):
                if Setting.LAUNCHER_MODEL:
                    log.info("waiting for push seeds...")
                    status = "waiting"
                    time.sleep(30)
                else:
                    log.info("spider done!")
                    break

            last.clear()

        storer_upload_queue_length_info = "\n            ".join(
            storer_upload_queue_list) if storer_upload_queue_list else "None"
        log.info(spider_info.format(
            status,
            running_spider_thread_num,
            redis_ready_seed_length,
            redis_spider_seed_length,
            memory_seed_queue_length,
            storer_upload_queue_length_info
        ))

        time.sleep(3)
    stop.set()


def launcher(task):
    """
    任务启动装饰器
    :param task: 任务配置信息
    """
    def decorator(func):
        storer_list = []

        # 程序结束事件
        last = threading.Event()
        # 停止采集事件
        stop = threading.Event()

        # 初始化redis信息
        redis_db = RedisDB(task.project, task.task_name, task.redis_info)

        log.info("初始化cobweb!")

        seed_queue = Queue()

        if task.scheduler_info is None:
            task.scheduler_info = dict()

        # 调度器动态继承
        sql = task.scheduler_info.get("sql")
        table = task.scheduler_info.get("table")
        size = task.scheduler_info.get("size")
        scheduler_config = task.scheduler_info.get("config")
        scheduler_db = task.scheduler_info.get("db", "default")
        DB, class_name = pim(scheduler_db, "scheduler")
        # SchedulerDB, table, sql, length, size, config = task.scheduler_info
        SchedulerTmp = type(class_name, (Scheduler, DB), {})

        # 初始化调度器
        scheduler = SchedulerTmp(
            table=table, sql=sql, size=size, queue=seed_queue,
            length=task.scheduler_queue_length, config=scheduler_config
        )

        # 解析存储器信息
        storer_info_list = task.storer_info or []
        if not isinstance(storer_info_list, list):
            storer_info_list = [storer_info_list]

        # new item
        item = type("Item", (object,), {"redis_client": redis_db.client})()

        for storer_info in storer_info_list:
            storer_db = storer_info["db"]
            fields = storer_info["fields"]
            storer_table = storer_info.get("table", "console")
            storer_config = storer_info.get("config")

            StorerDB, class_name = pim(storer_db, "storer")
            StorerTmp = type(class_name, (Storer, StorerDB), {})

            db_name = class_name.lower()
            if not getattr(item, db_name, None):
                instance = type(db_name, (DBItem,), {})
                setattr(item, db_name, instance)

            storer_item_instance = getattr(item, db_name)
            storer_item_instance.init_item(storer_table, fields)

            storer_queue = sqn(db_name, storer_table)
            queue = getattr(storer_item_instance, storer_queue)
            # 初始话存储器
            table_name = rtn(table_name=storer_table)
            storer = StorerTmp(
                table=table_name, fields=fields,
                length=task.storer_queue_length,
                queue=queue, config=storer_config
            )
            storer_list.append(storer)

        # 初始化采集器
        spider = Spider(seed_queue, storer_list and True, task.max_retries)

        threading.Thread(target=redis_db.check_spider_queue, args=(stop, len(storer_list))).start()
        threading.Thread(target=redis_db.set_heartbeat, args=(stop,)).start()

        # 推送初始种子
        # seeds = start_seeds(task.start_seed)
        redis_db.add_seed(task.seeds)
        # 启动调度器, 调度至redis队列
        threading.Thread(
            # name="xxxx_schedule_seeds",
            target=scheduler.schedule_seed,
            args=(
                redis_db.ready_seed_length,
                redis_db.get_scheduler_lock,
                redis_db.add_seed
            )
        ).start()

        # 启动调度器, 调度任务队列
        threading.Thread(
            # name="xxxx_schedule_task",
            target=scheduler.schedule_task,
            args=(
                stop, redis_db.get_seed,
                redis_db.ready_seed_length
            )
        ).start()

        # 启动采集器
        for index in range(task.spider_num):
            threading.Thread(
                # name=f"xxxx_spider_task:{index}",
                target=spider.spider_task,
                args=(
                    stop, func, item,
                    redis_db.del_seed
                )
            ).start()

        # 启动存储器
        for storer in storer_list:
            threading.Thread(
                # name=f"xxxx_store_task:{storer.table}",
                target=storer.store_task,
                args=(
                    stop, last,
                    redis_db.reset_seed,
                    redis_db.set_storer
                )
            ).start()

        threading.Thread(
            # name="check_spider",
            target=check,
            args=(
                stop, last, spider,
                scheduler, storer_list,
                redis_db.ready_seed_length,
                redis_db.spider_queue_length,
            )
        ).start()

    return decorator

