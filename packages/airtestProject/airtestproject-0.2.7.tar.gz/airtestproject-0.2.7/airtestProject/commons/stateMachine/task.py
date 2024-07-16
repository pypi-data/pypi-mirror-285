from airtestProject.commons.stateMachine.taskState import TaskEnd


class TaskMachine:
    def __init__(self, state_classes):
        self.states = {state_class.__name__: state_class() for state_class in state_classes}

    def run(self, test_cases):
        while not test_cases.empty():
            self.state = self.states['StartTest']  # 将状态设置为StartTest
            test_case = test_cases.get()
            try:
                while not isinstance(self.state, TaskEnd):  # 当状态不是TestEnd时，继续运行

                    self.state.run(test_case)
                    self.state = self.state.next_state()
            except Exception:
                self.state = self.states['TaskException']
                self.state.run(test_case)
