from typing import List
from columbia.cost.calculator import StatsCalculator
from columbia.memo.memo import Memo
from columbia.memo.properties import PropertySet
from columbia.rule.rule import RuleSet
from columbia.task.abstract_task import Task


class Context:
    def __init__(
        self,
        memo: Memo,
        cost_upper_bound: "float",
        rule_set: RuleSet,
        property_set: PropertySet,
        task_stack: List[Task],
        stats_calculator: StatsCalculator,
    ) -> None:
        # cost_upper_bound init with the bigest value, e.g., 1e10
        self.cost_upper_bound: float = cost_upper_bound
        self.task_stack: List[Task] = task_stack
        self.rule_set = rule_set
        self.properties = None
        self.memo = memo
        self.property_set = property_set
        self.stats_calculator = stats_calculator

    def push_task(self, task: Task) -> None:
        self.task_stack.append(task)

    def pop_task(self) -> Task:
        return self.task_stack.pop()

    def has_no_task(self) -> bool:
        return len(self.task_stack) == 0

    def copy(self) -> "Context":
        return Context(
            self.memo,
            self.cost_upper_bound,
            self.rule_set,
            self.property_set,
            self.task_stack,
            self.stats_calculator,
        )
