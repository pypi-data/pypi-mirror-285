



class Launcher:

    def __init__(self):
        pass

    def register(self, task_name, func):
        pass

    def launch(self, task_name):

        def decorator(func):
            # 注册爬虫程序
            self.register(task_name, func)
            return func

        return decorator
