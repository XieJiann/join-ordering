import itertools
from typing import List
import unittest
from columbia.memo.expr_group import Expr, Group, LeafGroup
from columbia.rule.pattern import (
    PatternType,
    pattern_children,
    match_root,
    pattern_root,
)
from plan.plan import LogicalType, Plan


class ExprBinder:
    def __init__(self, expr: Expr, pattern: PatternType) -> None:
        self.expr = expr
        if not match_root(pattern, expr) or len(pattern_children(pattern)) != len(
            expr.children
        ):
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

        self.cur_idx = 0

    def __iter__(self):
        return self

    def __next__(self) -> Plan:
        if self.cur_idx < len(self.permutaion):
            self.cur_idx += 1
            children: List[Plan] = []
            for i, j in enumerate(self.permutaion[self.cur_idx]):
                children.append(self.children_plan[i][j])
            return Plan(
                tuple(children), self.expr.type, self.expr.row_cnt, self.expr.name
            )
        else:
            raise StopIteration


class GroupBinder:
    def __init__(self, group: Group, pattern: PatternType) -> None:
        self.plan: List[Plan] = []
        if pattern_root(pattern) == LogicalType.Leaf:
            self.plan = [LeafGroup(group)]
            return
        for expr in group.all_exprs():
            self.plan.extend(list(ExprBinder(expr, pattern)))

    def all_plan(self) -> List[Plan]:
        return self.plan


class TestBinder(unittest.TestCase):
    def test_binder(self) -> None:
        pass
