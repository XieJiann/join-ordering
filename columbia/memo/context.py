from typing import List
from columbia.memo.memo import Memo
from columbia.rule.rule import RuleSet
from columbia.task.abstract_task import Task


class Context:
    def __init__(
        self, memo: Memo, cost_upper_bound: "float", rule_set: RuleSet
    ) -> None:
        # cost_upper_bound init with the bigest value, e.g., 1e10
        self.cost_upper_bound = cost_upper_bound
        self.task_stack: List[Task] = []
        self.rule_set = rule_set
        self.properties = None
        self.memo = memo

    def push_task(self, task: Task) -> None:
        self.task_stack.append(task)

    def pop_task(self) -> Task:
        return self.task_stack.pop()

    def empty(self) -> bool:
        return len(self.task_stack) == 0
