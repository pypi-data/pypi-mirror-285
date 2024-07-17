

class LauncherModel:
    task = "launcher model: task"
    resident = "launcher model: resident"


class LogModel:
    simple = "log model: simple"
    common = "log model: common"
    detailed = "log model: detailed"


class DealModel:
    failure = "deal model: failure"
    success = "deal model: success"
    polling = "deal model: polling"


class Setting:
    RESET_SCORE = None
    CHECK_LOCK_TIME = None
    SCHEDULER_LOCK_TIME = None
    DEAL_MODEL = None
    LAUNCHER_MODEL = None
    SCHEDULER_WAIT_TIME = None
    SCHEDULER_BLOCK_TIME = None
    SPIDER_WAIT_TIME = None
    SPIDER_SLEEP_TIME = None
