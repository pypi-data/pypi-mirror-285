import time
import threading

from equip.single import Seed, DBItem
from equip.single import struct_queue_name, restore_table_name
from equip.single import Distributor, Scheduler, Spider, Storer


def init_task_seed(seeds):
    if not seeds:
        return None
    if isinstance(seeds, list) or isinstance(seeds, tuple):
        for seed in seeds:
            yield Seed(seed)
    elif isinstance(seeds, str) or isinstance(seeds, dict):
        yield Seed(seeds)


def parse_storer_info(storer_info):
    storer_data = {}
    storer_info_list = []
    if storer_info.__class__.__name__ == 'StorerInfo':
        storer_info_list.append(storer_info)
    elif isinstance(storer_info, tuple) or isinstance(storer_info, list):
        storer_info_list = storer_info
    for info in storer_info_list:
        db_name = info.DB.__name__
        storer_data.setdefault(db_name, {"StorerDB": info.DB, "db_args_list": []})
        storer_data[db_name]["db_args_list"].append(info[1:])
    return storer_data


def check(stop_event, last_event, distributor, scheduler, spider, storer_list):
    while True:
        time.sleep(3)
        if (
                scheduler.stop and
                not distributor.seed_queue.length and
                not spider.spider_in_progress.length
        ):
            last_event.set()
            time.sleep(10)
            storer_queue_empty = True
            for storer in storer_list:
                if storer.queue.length:
                    storer_queue_empty = False
                    break
            if storer_queue_empty:
                break
        last_event.clear()
    stop_event.set()


def cobweb(task):
    """
    任务启动装饰器
    :param task: 任务配置信息
    """
    def decorator(func):
        """
        func(Item, seed)
            Item:
                Item.Textfile()
                Item.Console()
        """
        # project task_name start_seed spider_num queue_length scheduler_info storer_info

        storer_list = []

        # 程序结束事件
        last_event = threading.Event()
        # 暂停采集事件
        stop_event = threading.Event()

        # 创建分发器
        distributor = Distributor()

        # 调度器动态继承
        SchedulerDB, table, sql, length, size = task.SchedulerInfo
        SchedulerTmp = type('Scheduler', (Scheduler, SchedulerDB), {})

        # 初始化调度器
        scheduler = SchedulerTmp(table=table, sql=sql, length=length, size=size, queue=distributor.seed_queue)

        # 初始化采集器
        spider = Spider(queue=distributor.seed_queue)

        # 解析存储器信息
        storer_data = parse_storer_info(task.storer_info)

        # sds
        item = type("item", (object,), {})
        for db_name in storer_data.keys():
            # 存储器动态继承
            StorerDB = storer_data[db_name]["StorerDB"]
            StorerTmp = type('Storer', (Storer, StorerDB), {})
            db_args_list = storer_data[db_name]["db_args_list"]
            for storer_db_args in db_args_list:
                table, fields, length = storer_db_args
                if not getattr(item, db_name, None):
                    instance = type(db_name, (DBItem,), {})
                    setattr(item, db_name, instance)
                # 创建存储xxx
                getattr(item, db_name).init_item(table, fields)
                # 创建存储队列
                storer_queue = struct_queue_name(db_name, table)
                distributor.create_queue(queue_name=storer_queue)
                queue = distributor.get_queue(queue_name=storer_queue)
                # 初始话存储器
                table_name = restore_table_name(table_name=table)
                storer = StorerTmp(table=table_name, fields=fields, length=length, queue=queue)
                storer_list.append(storer)

        # 推送初始种子
        distributor.distribute(init_task_seed, seeds=task.start_seed)

        # 启动调度器
        threading.Thread(
            target=scheduler.schedule_task,
            args=(distributor.distribute,),
            name="single_scheduler_task"
        ).start()

        # 启动采集器
        for index in range(task.spider_num):
            threading.Thread(
                target=spider.spider_task,
                args=(stop_event, distributor.distribute, func, item),
                name=f"single_spider_task:{index}"
            ).start()

        # 启动存储器
        for storer in storer_list:
            threading.Thread(
                target=storer.store_task,
                args=(stop_event, last_event, distributor.distribute),
                name=f"single_store_task:{storer.table}",
            ).start()

        threading.Thread(
            target=check, name="check",
            args=(
                stop_event, last_event, distributor,
                scheduler, spider, storer_list
            )
        ).start()

        # return starter(task, func)
    return decorator




