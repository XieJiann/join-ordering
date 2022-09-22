import itertools
from typing import List
import unittest
from columbia.memo.expr_group import Expr, Group
from columbia.rule.rule import PatternType, child_at, match_root


class ExprBinder:
    def __init__(self, expr: Expr, pattern: PatternType) -> None:
        self.expr = expr
        self.children_plan: List[List[Expr]] = []

        # collect all valid plan
        if not match_root(pattern, expr):
            return

        for i in range(0, expr.children_size()):
            group_binder = GroupBinder(expr.group_child_at(i), child_at(pattern, i))
            self.children_plan.append(list(group_binder.__iter__()))

        self.permutaion: list[tuple[int, ...]] = list(
            itertools.product(
                *[range(0, len(indices)) for indices in self.children_plan]
            )
        )

        self.cur_idx = 0

    def __iter__(self):
        return self

    def __next__(self) -> Expr:
        if self.cur_idx == 0 and len(self.children_plan) == 0:
            # The empty children means that there is no children for the pattern
            # Maybe it's AnyType or Leaf Node
            return self.expr
        elif self.cur_idx < len(self.permutaion):
            self.cur_idx += 1
            children: List[Expr] = []
            for i, j in enumerate(self.permutaion[self.cur_idx]):
                children.append(self.children_plan[i][j])
            return self.expr.copy().set_children((tuple(children)))
        else:
            raise StopIteration


class GroupBinder:
    def __init__(self, group: Group, pattern: PatternType) -> None:
        self.plan: List[Expr] = []
        for expr in group.logical_exprs + group.physical_exprs:
            self.plan.extend(list(ExprBinder(expr, pattern)))

    def __iter__(self):
        return self.plan


class TestBinder(unittest.TestCase):
    def test_binder(self) -> None:
        pass
