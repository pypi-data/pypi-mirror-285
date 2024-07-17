import time
from hashlib import md5
from inspect import isgenerator

from .. import log, ici
from .. import DealModel, Queue, Seed, Setting
# from pympler import asizeof


class Scheduler:

    def schedule_seed(self, ready_seed_length, get_scheduler_lock, add_seed):

        inf_name = "SchedulerInterface"
        if not ici(self.__class__, inf_name):
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
                time.sleep(5)
                continue

            if self.queue.length >= self.length:
                time.sleep(3)
                continue

            seeds = get_seed(self.length)
            self.queue.push(seeds)
        log.info(f"close thread: schedule_task")


class Spider:

    def __init__(self, queue, storage, max_retries=5):
        self.spider_in_progress = Queue()
        self.max_retries = max_retries
        self.storage = storage
        self.queue = queue

    def spider_task(self, stop, func, item, del_seed):
        while not stop.is_set():
            seed = self.queue.pop()
            if not seed:
                time.sleep(3)
                continue
            elif seed._retry >= self.max_retries:
                del_seed(seed, spider_status=False)
                continue
            try:
                self.spider_in_progress.push(1, direct_insertion=True)
                # log.info("spider seed: " + str(seed))

                store_queue = None
                store_data = list()

                iterators = func(item, seed)

                if not isgenerator(iterators):
                    if not self.storage:
                        del_seed(seed, spider_status=True)
                        continue
                    raise TypeError(f"{func.__name__} isn't a generator")

                for it in iterators:
                    if getattr(it, "table_name", None):
                        if not store_queue:
                            store_queue = it.queue()
                        store_data.append(it.struct_data)
                    elif isinstance(it, Seed):
                        self.queue.push(it)

                    elif isinstance(it, str) and it == DealModel.polling:
                        self.queue.push(seed)
                        break
                    elif isinstance(it, str) and it == DealModel.success:
                        del_seed(seed, spider_status=True)
                        break
                    elif isinstance(it, str) and it == DealModel.failure:
                        del_seed(seed, spider_status=False)
                        break
                    else:
                        raise TypeError("yield value type error!")

                if store_queue and store_data:
                    store_data.append(seed)
                    store_queue.push(store_data)

            except Exception as e:
                seed._retry += 1
                self.queue.push(seed)
                log.info(f"{str(seed)} -> {str(e)}")
            finally:
                self.spider_in_progress.pop()
                time.sleep(Setting.SPIDER_RUN_TIME)
        log.info(f"close thread: spider")


class Storer:

    def store_task(self, stop, last, reset_seed, set_storer):

        inf_name = "StorerInterface"
        if not ici(self.__class__, inf_name):
            return None

        if not getattr(self, "store", None):
            raise Exception("not have store function!")

        storer_name = self.__class__.__name__ + self.table
        store_key_id = md5(storer_name.encode()).hexdigest()

        while not stop.is_set():

            storer_length = self.queue.length
            if not storer_length:
                time.sleep(5)
                continue

            if last.is_set() or storer_length >= self.length:
                seeds, data_list = [], []

                while True:
                    data = self.queue.pop()
                    if not data:
                        break
                    if isinstance(data, Seed):
                        seeds.append(data)
                        if len(data_list) >= self.length:
                            break
                        continue
                    data_list.append(data)

                if self.store(data_list):
                    set_storer(store_key_id, seeds)
                else:
                    reset_seed(seeds)

            time.sleep(3)

        log.info(f"close thread: {storer_name}")
