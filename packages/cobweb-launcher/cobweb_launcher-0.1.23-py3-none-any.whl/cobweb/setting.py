import os


# model: 0, 1, 2
MODEL = int(os.getenv("MODEL", "0"))

# 重制score值的等待时间, 默认10分钟
RESET_SCORE = int(os.getenv("RESET_SCORE", "600"))

# 默认设置检查spider queue队列锁的存活时间为30s
CHECK_LOCK_TIME = int(os.getenv("CHECK_LOCK_TIME", 30))


