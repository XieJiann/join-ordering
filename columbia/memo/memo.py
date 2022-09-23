from typing import List, Optional
from columbia.memo.expr_group import Expr, Group, LeafGroup
from columbia.rule.rule import RuleSet
from columbia.task import Task
from plan.plan import Plan


class Memo:
    def __init__(self) -> None:
        # root always in the front
        self.groups: List["Group"] = []
        self.expr_dict: "dict[Expr, Group]" = {}

    def new_group(self) -> Group:
        group = Group(len(self.groups))
        self.groups.append(group)
        return group

    def root(self) -> Group:
        return self.groups[0]

    def record_plan(self, plan: Plan, group: Optional[Group]) -> Group:
        if isinstance(plan, LeafGroup):
            return plan.group

        group_children = map(lambda p: self.record_plan(p, None), plan.children)
        expr = Expr(plan.op_type, tuple(group_children), None, plan.name, plan.row_cnt)
        if expr in self.expr_dict:
            return self.expr_dict[expr]

        if group is None:
            group = self.new_group()
        group.record_expr(expr)
        self.expr_dict[expr] = group
        return group


class Context:
    def __init__(self, cost_upper_bound: "float", rule_set: RuleSet) -> None:
        # cost_upper_bound init with the bigest value, e.g., 1e10
        self.cost_upper_bound = cost_upper_bound
        self.task_stack: List[Task] = []
        self.rule_set = rule_set
        self.properties = None

    def push_task(self, task: Task) -> None:
        self.task_stack.append(task)

    def pop_task(self) -> Task:
        return self.task_stack.pop()

    def empty(self) -> bool:
        return len(self.task_stack) == 0
