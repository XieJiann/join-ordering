import itertools
from typing import List
from columbia.memo.expr_group import GroupExpr, Group, LeafGroup
from columbia.rule.pattern import (
    PatternType,
    match_root,
    pattern_children,
    pattern_root,
)
from plan.plan import LogicalType, Plan


class ExprBinder:
    def __init__(self, expr: GroupExpr, pattern: PatternType) -> None:
        self.expr = expr
        self.cur_idx = 0
        self.permutaion = [()]
        self.children_plan = [[]]
        if len(self.expr.children) == 0:
            return
        # collect all valid plan
        self.children_plan: List[List[Plan]] = []
        for group, pattern in zip(expr.children, pattern_children(pattern)):
            self.children_plan.append(GroupBinder(group, pattern).all_plan())
        self.permutaion: list[tuple[int, ...]] = list(
            itertools.product(
                *[range(0, len(indices)) for indices in self.children_plan]
            )
        )

    def __iter__(self):
        return self

    def __next__(self) -> Plan:
        if self.cur_idx < len(self.permutaion):
            children: List[Plan] = []
            for i, j in enumerate(self.permutaion[self.cur_idx]):
                children.append(self.children_plan[i][j])
            self.cur_idx += 1
            return Plan.from_content(tuple(children), self.expr.content)
        else:
            raise StopIteration


class GroupBinder:
    def __init__(self, group: Group, pattern: PatternType) -> None:
        self.plan: List[Plan] = []
        if pattern_root(pattern) == LogicalType.Leaf:
            self.plan = [LeafGroup(group)]
            return
        for expr in group.all_exprs():
            if not match_root(pattern, expr) or (
                len(pattern_children(pattern)) != len(expr.children)
            ):
                continue
            self.plan.extend(list(ExprBinder(expr, pattern)))

    def all_plan(self) -> List[Plan]:
        return self.plan
