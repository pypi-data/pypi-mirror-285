from abc import ABC, abstractmethod

"""
状态机状态类
"""


class State(ABC):
    @abstractmethod
    def run(self, test_case):
        pass

    @abstractmethod
    def next_state(self):
        pass


class StartTest(State):
    def run(self, test_case):
        print("开始测试")
        test_case.run()

    def next_state(self):
        return TaskNormal()


class TaskException(State):
    def run(self, test_case):
        print("测试异常")

    def next_state(self):
        return TaskEnd()


class TaskNormal(State):
    def run(self, test_case):
        print("测试正常")

    def next_state(self):
        return TaskEnd()


class TaskEnd(State):
    def run(self, test_case):
        print("测试结束")

    def next_state(self):
        return self
