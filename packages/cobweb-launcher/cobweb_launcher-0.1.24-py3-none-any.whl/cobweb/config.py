import json
from collections import namedtuple
from base.utils import struct_table_name

StorerInfo = namedtuple(
    "StorerInfo",
    "DB, table, fields, length, config"
)
SchedulerInfo = namedtuple(
    "SchedulerInfo",
    "DB, table, sql, length, size, config",
)
RedisInfo = namedtuple(
    "RedisInfo",
    "host, port, username, password, db",
    defaults=("localhost", 6379, None, None, 0)
)

# redis_info = dict(
#     host="localhost",
#     port=6379,
#     username=None,
#     password=None,
#     db=0
# )


class SchedulerDB:

    @staticmethod
    def default():
        from db.scheduler.default import Default
        return SchedulerInfo(DB=Default, table="", sql="", length=100, size=500000, config=None)

    @staticmethod
    def textfile(table, sql=None, length=100, size=500000):
        from db.scheduler.textfile import Textfile
        return SchedulerInfo(DB=Textfile, table=table, sql=sql, length=length, size=size, config=None)

    @staticmethod
    def diy(DB, table, sql=None, length=100, size=500000, config=None):
        from base.interface import SchedulerInterface
        if not isinstance(DB, SchedulerInterface):
            raise Exception("DB must be inherit from SchedulerInterface")
        return SchedulerInfo(DB=DB, table=table, sql=sql, length=length, size=size, config=config)

    # @staticmethod
    # def info(scheduler_info):
    #     if not scheduler_info:
    #         return SchedulerDB.default()
    #
    #     if isinstance(scheduler_info, SchedulerInfo):
    #         return scheduler_info
    #
    #     if isinstance(scheduler_info, str):
    #         scheduler = json.loads(scheduler_info)
    #         if isinstance(scheduler, dict):
    #             db_name = scheduler["DB"]
    #             if db_name in dir(SchedulerDB):
    #                 del scheduler["DB"]
    #             else:
    #                 db_name = "diy"
    #             func = getattr(SchedulerDB, db_name)
    #             return func(**scheduler)


class StorerDB:

    @staticmethod
    def console(table, fields, length=200):
        from db.storer.console import Console
        table = struct_table_name(table)
        return StorerInfo(DB=Console, table=table, fields=fields, length=length, config=None)

    @staticmethod
    def textfile(table, fields, length=200):
        from db.storer.textfile import Textfile
        table = struct_table_name(table)
        return StorerInfo(DB=Textfile, table=table, fields=fields, length=length, config=None)

    @staticmethod
    def loghub(table, fields, length=200, config=None):
        from db.storer.loghub import Loghub
        table = struct_table_name(table)
        return StorerInfo(DB=Loghub, table=table, fields=fields, length=length, config=config)

    @staticmethod
    def diy(DB, table, fields, length=200, config=None):
        from base.interface import StorerInterface
        if not isinstance(DB, StorerInterface):
            raise Exception("DB must be inherit from StorerInterface")
        table = struct_table_name(table)
        return StorerInfo(DB=DB, table=table, fields=fields, length=length, config=config)

    # @staticmethod
    # def info(storer_info):
    #     if not storer_info:
    #         return None
    #
    #     if isinstance(storer_info, str):
    #         storer_info = json.loads(storer_info)
    #
    #     if any(isinstance(storer_info, t) for t in (dict, StorerInfo)):
    #         storer_info = [storer_info]
    #
    #     if not isinstance(storer_info, list):
    #         raise Exception("StorerDB.info storer_info")
    #
    #     storer_info_list = []
    #     for storer in storer_info:
    #         if isinstance(storer, StorerInfo):
    #             storer_info_list.append(storer)
    #         else:
    #             db_name = storer["DB"]
    #             if db_name in dir(StorerDB):
    #                 del storer["DB"]
    #             else:
    #                 db_name = "diy"
    #             func = getattr(StorerDB, db_name)
    #             storer_info_list.append(func(**storer))
    #     return storer_info_list



def deal(config, tag):
    if isinstance(config, dict):
        if tag == 0:
            return RedisInfo(**config)
        elif tag == 1:
            db_name = config["DB"]
            if db_name in dir(SchedulerDB):
                del config["DB"]
            else:
                db_name = "diy"
            func = getattr(SchedulerDB, db_name)
            return func(**config)
        elif tag == 2:
            db_name = config["DB"]
            if db_name in dir(StorerDB):
                del config["DB"]
            else:
                db_name = "diy"
            func = getattr(StorerDB, db_name)
            return func(**config)
        raise ValueError("tag must be in [0, 1, 2]")
    elif any(isinstance(config, t) for t in (StorerInfo, SchedulerInfo, RedisInfo)):
        return config
    raise TypeError("config must be in [StorerInfo, SchedulerInfo, RedisInfo]")


def info(configs, tag = 0):
    if configs is None:
        return SchedulerDB.default() if tag == 1 else None

    if isinstance(configs, str):
        configs = json.loads(configs)

    if tag == 0:
        return deal(configs, tag)

    if not isinstance(configs, list):
        configs = [configs]

    return [deal(config, tag) for config in configs]
