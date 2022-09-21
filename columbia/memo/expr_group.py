from enum import Enum, auto
from typing import Any, List, Optional, Tuple
import unittest

from columbia.memo.memo import Context
from columbia.rule import Rule


class ExprType(Enum):
    # Any, it's just used in pattern children
    AnyExpr = auto()
    # logical
    LogicalInnerJoin = auto()
    LogicalTable = auto()
    # physical
    NSLJoin = auto()
    PhysicalScan = auto()


def is_logical_leaf(e_type: ExprType) -> bool:
    return e_type == ExprType.LogicalInnerJoin


class Expr:
    def __init__(
        self,
        type: ExprType,
        expr_children: "Tuple[()] | Tuple[Expr | Group] | Tuple[Expr | Group, Expr | Group]",
        group: Optional["Group"],
        name: Optional[str],
        row_cnt: int,
    ) -> None:
        self.children = expr_children
        self.type = type
        self.name = name
        self.rule_mask = 0
        self.group = group
        self.row_cnt = row_cnt

    def set_applied(self, rule: Rule) -> None:
        self.rule_mask |= rule.id

    def applied(self, rule: Rule) -> bool:
        return (self.rule_mask & rule.id) != 0

    def is_logical(self) -> bool:
        return self.type in {ExprType.LogicalInnerJoin, ExprType.LogicalTable}

    def set_group(self, group: "Group") -> "Expr":
        self.group = group
        return self

    def set_children(
        self, children: Tuple["Group"] | Tuple["Group", "Group"]
    ) -> "Expr":
        self.children = children
        return self

    def child_at(self, i: int) -> "Group":
        group = self.children[i]
        assert isinstance(group, "Group")
        return group

    def is_leaf(self) -> bool:
        return self.children == ()

    def __str__(self) -> str:
        if self.name is None:
            return str(self.type).split(".")[-1]
        return self.name

    def __hash__(self) -> int:
        return hash((self.type, self.name, self.children))

    def __eq__(self, __o: object) -> bool:
        return hash(self) == hash(__o)


class Group:
    def __init__(self, gid: int) -> None:
        self.gid = gid
        self.logical_exprs: List[Expr] = []
        self.physical_exprs: List[Expr] = []

        self.explored = False
        # the winner matain the idx of the expr with the lowest cost
        self.winner = None

        self.row_cnt = None

        self.cost_lower_bound = -1  # useless?

    def set_explored(self) -> None:
        self.explored = True

    def record_expr(self, expr: Expr) -> None:
        if expr.is_logical():
            self.logical_exprs.append(expr)
        else:
            self.physical_exprs.append(expr)

    def has_winner(self, context: Context) -> bool:
        # The properties has not been supported yet
        return self.winner != None

    def __hash__(self) -> int:
        return self.gid

    def __eq__(self, __o: object) -> bool:
        return self.gid == hash(__o)

    def all_trees(self) -> list[Any]:
        trees: List[Any] = []
        for expr in self.logical_exprs + self.physical_exprs:
            if expr.is_leaf():
                trees.append(str(expr))
                continue

            if len(expr.children) == 2:
                assert isinstance(expr.children[0], Group)
                assert isinstance(expr.children[1], Group)
                l_tree_group = expr.children[0].all_trees()
                r_tree_group = expr.children[1].all_trees()
                for l_tree in l_tree_group:
                    for r_tree in r_tree_group:
                        trees.append({str(expr): [l_tree, r_tree]})
        return trees


class Test(unittest.TestCase):
    def test_hash(self) -> None:
        g1 = Group(0)
        e1 = Expr(ExprType.LogicalTable, (), g1, "t1", 1)
        g2 = Group(1)
        e2 = Expr(ExprType.LogicalTable, (), g2, "t2", 1)
        e3 = Expr(ExprType.LogicalInnerJoin, (e1, e2), None, None, 1)
        e4 = Expr(ExprType.LogicalInnerJoin, (e1, e2), None, None, 1)
        assert hash(e3) == hash(e4)
        assert hash(e3) != hash(e2)
        assert hash(e1) != hash(e2)
