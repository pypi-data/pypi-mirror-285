# from typing import Iterable
import json
import time
import hashlib
from .log import log
from .utils import struct_queue_name
from collections import deque, namedtuple


class Queue:

    def __init__(self):
        self._queue = deque()

    @property
    def length(self) -> int:
        return len(self._queue)
    #
    # @property
    # def queue_names(self):
    #     return tuple(self.__dict__.keys())
    #
    # @property
    # def used_memory(self):
    #     return asizeof.asizeof(self)

    # def create_queue(self, queue_name: str):
    #     self.__setattr__(queue_name, deque())

    # def push_seed(self, seed):
    #     self.push("_seed_queue", seed)

    # def pop_seed(self):
    #     return self.pop("_seed_queue")

    def push(self, data, left: bool = False, direct_insertion: bool = False):
        try:
            if not data:
                return None
            if direct_insertion or isinstance(data, Seed):
                self._queue.appendleft(data) if left else self._queue.append(data)
            elif any(isinstance(data, t) for t in (list, tuple)):
                self._queue.extendleft(data) if left else self._queue.extend(data)
        except AttributeError as e:
            log.exception(e)

    def pop(self, left: bool = True):
        try:
            return self._queue.popleft() if left else self._queue.pop()
        except IndexError:
            return None
        except AttributeError as e:
            log.exception(e)
            return None


class Seed:

    def __init__(
            self,
            seed_info=None,
            priority=300,
            version=0,
            retry=0,
            **kwargs
    ):
        if seed_info:
            if any(isinstance(seed_info, t) for t in (str, bytes)):
                try:
                    item = json.loads(seed_info)
                    for k, v in item.items():
                        self.__setattr__(k, v)
                except json.JSONDecodeError:
                    self.__setattr__("url", seed_info)
            elif isinstance(seed_info, dict):
                for k, v in seed_info.items():
                    self.__setattr__(k, v)
            else:
                raise TypeError(Exception(
                    f"seed type error, "
                    f"must be str or dict! "
                    f"seed_info: {seed_info}"
                ))
        for k, v in kwargs.items():
            self.__setattr__(k, v)
        if not getattr(self, "_priority"):
            self._priority = min(max(1, int(priority)), 999)
        if not getattr(self, "_version"):
            self._version = int(version) or int(time.time())
        if not getattr(self, "_retry"):
            self._retry = retry
        if not getattr(self, "sid"):
            self.init_id()

    def init_id(self):
        item_string = self.format_seed
        seed_id = hashlib.md5(item_string.encode()).hexdigest()
        self.__setattr__("sid", seed_id)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, item):
        return getattr(self, item)

    def __getattr__(self, name):
        return None

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    def __repr__(self):
        chars = [f"{k}={v}" for k, v in self.__dict__.items()]
        return f'{self.__class__.__name__}({", ".join(chars)})'

    @property
    def dict_seed(self):
        seed = self.__dict__.copy()
        del seed["_priority"]
        del seed["_version"]
        del seed["_retry"]
        return seed

    @property
    def format_seed(self):
        return json.dumps(self.dict_seed, ensure_ascii=False, separators=(",", ":"))


class DBItem:

    def __init__(self, **kwargs):
        self.__setattr__("_index", 0, True)
        for table in self.__class__.__table__:
            if set(kwargs.keys()) == set(table._fields):
                break
            self._index += 1

        if self._index > len(self.__class__.__table__):
            raise Exception()

        table = self.__class__.__table__[self._index]
        self.__setattr__("struct_data", table(**kwargs), True)
        self.__setattr__("db_name", self.__class__.__name__, True)
        self.__setattr__("table_name", self.struct_data.__class__.__name__, True)

    @classmethod
    def init_item(cls, table_name, fields):
        queue_name = struct_queue_name(cls.__name__, table_name)
        if getattr(cls, queue_name, None) is None:
            setattr(cls, queue_name, Queue())

        if getattr(cls, "__table__", None) is None:
            cls.__table__ = []

        table = namedtuple(table_name, fields)

        if table in getattr(cls, "__table__"):
            raise Exception()
        getattr(cls, "__table__").append(table)

    def queue(self):
        queue_name = struct_queue_name(self.db_name, self.table_name)
        return getattr(self.__class__, queue_name)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __getitem__(self, item):
        return self.struct_data[item]

    def __getattr__(self, name):
        return None

    def __setattr__(self, key, value, init=None):
        if init:
            super().__setattr__(key, value)
        elif not getattr(self, "struct_data"):
            raise Exception(f"no struct_data")
        else:
            self.__setattr__(
                "struct_data",
                self.struct_data._replace(**{key: value}),
                init=True
            )

    def __str__(self):
        return json.dumps(self.struct_data._asdict(), ensure_ascii=False)

    def __repr__(self):
        return f'{self.__class__.__name__}:{self.struct_data}'

