from . import Inf, log


class Console(Inf):

    def store(self, data_list):
        for item in data_list:
            log.info(f"item info: {item}")

