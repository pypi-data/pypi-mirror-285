from cobweb import log, StorerInterface


class Redis(StorerInterface):

    def store(self, data_list):
        try:
            data_str = "\n".join(str(data) for data in data_list)
            with open(self.table, "a") as fp:
                fp.write(data_str)
            log.info(f"save data, data length: {len(data_list)}")
            return True
        except Exception as e:
            return False

