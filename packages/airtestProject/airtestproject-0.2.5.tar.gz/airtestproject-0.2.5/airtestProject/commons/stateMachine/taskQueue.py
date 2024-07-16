from asyncio import Queue, LifoQueue


class TaskQueue:
    """
    状态队列
    TODO:配合状态机控制任务轮换
    """

    def __init__(self, num=50, lifo=False):
        self.queue = Queue(num) if not lifo else LifoQueue(num)

    def put_queue(self, key):
        """存测试方法"""
        try:
            if not self.check_queue(key):
                self.queue.put(key)
        except Exception as e:
            print(f"{key}队列异常{e}")

    def check_queue(self, key):
        """检查存入数据"""
        for i in range(self.queue.qsize()):
            task_key = self.queue.get()
            if task_key == key:
                self.queue.put(task_key)
                return True
            else:
                self.queue.put(task_key)
        return False

    def task_over(self, over_key):
        """销毁任务"""
        for i in range(self.queue.qsize()):
            task_key = self.queue.get()
            if task_key == over_key:
                return True
            else:
                self.queue.put(task_key)
        return False

    def get_task(self):
        """按照队列取数据"""
        if self.queue.empty():
            return False
        else:
            task = self.queue.get()
            self.queue.put(task)
            return task

    def clear(self):
        for i in range(self.queue.qsize()):
            self.queue.get()


class Task(object):
    """
    Task包装类
    """
    def __init__(self, func):
        self.func = func

    def run(self):
        self.func()
