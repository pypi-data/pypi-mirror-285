from abc import ABC, abstractmethod
from .utils import parse_info


class SchedulerInterface(ABC):

    def __init__(self, table, sql, length, size, queue, config=None):
        self.sql = sql
        self.table = table
        self.length = length
        self.size = size
        self.queue = queue
        self.config = parse_info(config)
        self.stop = False

    @abstractmethod
    def schedule(self, *args, **kwargs):
        pass


class StorerInterface(ABC):

    def __init__(self, table, fields, length, queue, config=None):
        self.table = table
        self.fields = fields
        self.length = length
        self.queue = queue
        self.config = parse_info(config)
        # self.redis_db = redis_db

    @abstractmethod
    def store(self, *args, **kwargs):
        pass

