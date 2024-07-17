from . import Inf, log, Seed


class Textfile(Inf):

    index = None

    def schedule(self):
        try:
            seeds = []
            with open(self.table, "r") as fp:
                fp.seek(self.index or 0, 0)
                for _ in range(self.length):
                    data = fp.readline().strip()
                    if not data:
                        log.info("scheduler end!")
                        self.stop = True
                        break
                    seeds.append(Seed(data))
                    self.index = fp.tell()
            return seeds
        except FileNotFoundError:
            log.error("task table not found!")
            return None
        except TypeError:
            log.error("task table type error!")
            return None
