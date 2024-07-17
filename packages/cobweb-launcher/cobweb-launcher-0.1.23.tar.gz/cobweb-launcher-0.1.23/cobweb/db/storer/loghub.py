import json
from . import Inf, log
from aliyun.log import LogClient, LogItem, PutLogsRequest


class Loghub(Inf):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = None

    def init_loghub_clint(self):
        try:
            self.client = LogClient(
                self.config['endpoint'],
                self.config['access_key_id'],
                self.config['access_key']
            )
        except Exception as e:
            self.client = None
            return False

    def store(self, data_list):
        try:
            if not self.client:
                self.init_loghub_clint()

            log_items = list()
            for item in data_list:
                temp = item._asdict()
                for key, value in temp.items():
                    if isinstance(value, str):
                        temp[key] = value
                    else:
                        temp[key] = json.dumps(value, ensure_ascii=False)
                log_item = LogItem()
                contents = sorted(temp.items())  # dict to tuple
                log_item.set_contents(contents)
                log_items.append(log_item)
            request = PutLogsRequest(
                project=self.config["project"],
                logstore=self.table,
                topic=self.config["topic"],
                source=self.config.get("source"),
                logitems=log_items,
                compress=True
            )
            self.client.put_logs(request=request)
            log.info(f"save data, data length: {len(data_list)}")
            return True
        except Exception as e:
            log.exception(e)
            return False

