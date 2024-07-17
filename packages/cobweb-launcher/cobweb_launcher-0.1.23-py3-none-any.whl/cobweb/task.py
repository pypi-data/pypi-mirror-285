import os
from .constant import *
from .utils import parse_info, struct_start_seeds


def init_task_env():
    Setting.RESET_SCORE = int(os.getenv("RESET_SCORE", 600))
    Setting.CHECK_LOCK_TIME = int(os.getenv("CHECK_LOCK_TIME", 30))
    Setting.DEAL_MODEL = os.getenv("DEAL_MODEL", DealModel.failure)
    Setting.LAUNCHER_MODEL = os.getenv("LAUNCHER_MODEL", LauncherModel.task)
    Setting.SCHEDULER_WAIT_TIME = float(os.getenv("SCHEDULER_WAIT_TIME", 5))
    Setting.SCHEDULER_BLOCK_TIME = float(os.getenv("SCHEDULER_BLOCK_TIME", 3))
    Setting.SPIDER_WAIT_TIME = float(os.getenv("SPIDER_WAIT_TIME", 3))
    Setting.SPIDER_SLEEP_TIME = float(os.getenv("SPIDER_SLEEP_TIME", 0.5))


class Task:

    def __init__(
            self,
            seeds=None,
            project=None,
            task_name=None,
            oss_config=None,
            redis_info=None,
            storer_info=None,
            scheduler_info=None,
            spider_num=None,
            max_retries=None,
            storer_queue_length=None,
            scheduler_queue_length=None,
    ):
        """

        :param seeds:
        :param project:
        :param task_name:
        :param redis_info:
        :param storer_info:
        :param scheduler_info: dict(DB="", table="", size="", config="")
        :param spider_num:
        :param max_retries:
        :param storer_queue_length:
        :param scheduler_queue_length:
        """
        init_task_env()
        self.seeds = struct_start_seeds(seeds)
        self.project = project or "test"
        self.task_name = task_name or "spider"

        self.oss_config = oss_config

        self.redis_info = parse_info(redis_info)
        self.storer_info = parse_info(storer_info)
        self.scheduler_info = parse_info(scheduler_info)

        self.spider_num = spider_num or 1
        self.max_retries = max_retries or 5
        self.storer_queue_length = storer_queue_length or 100
        self.scheduler_queue_length = scheduler_queue_length or 100

