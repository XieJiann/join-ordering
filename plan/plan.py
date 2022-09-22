from enum import Enum, auto
from typing import Any, List, Optional, Tuple
import unittest


def tree_printer(tree: Tuple[str, Tuple[Any, ...]]) -> str:
    def format_subtree(tree: Tuple[str, Tuple[Any, ...]]) -> List[str]:
        children: List[List[str]] = []
        if len(tree[1]) == 0:
            return [tree[0]]
        for child in tree[1]:
            children.append(format_subtree(child))

        res: List[str] = []
        res.append(f"{tree[0]} ──┬─── {children[0][0]}")
        for sub_child in children[0][1:]:
            res.append(f"{' '*len(tree[0])}   |    {sub_child}")
        for child in children[1:]:
            res.append(f"{' '*len(tree[0])}   └─── {child[0]}")
            for sub_child in child[1:]:
                print("sub:", sub_child)
                res.append(f"{' '*len(tree[0])}        {sub_child}")
        return res

    res = format_subtree(tree)
    return "\n".join(res)


class OpType(Enum):
    def is_logical(self) -> bool:
        return False


class LogicalType(OpType):
    InnerJoin = auto()
    Table = auto()
    Leaf = auto()

    def is_logical(self) -> bool:
        return True


class PhyiscalType(OpType):
    NSLJoin = auto()
    Scan = auto()
    Leaf = auto()


class Plan:
    def __init__(
        self,
        children: Tuple["Plan", ...],
        op_type: OpType,
        row_cnt: int,
        name: Optional[str],
    ) -> None:
        self.children: Tuple[Plan, ...] = children
        self.op_type = op_type
        self.name = name
        self.row_cnt = row_cnt

    def copy(self) -> "Plan":
        return Plan(self.children, self.op_type, self.row_cnt, self.name)

    def __str__(self) -> str:
        if self.name is not None:
            return self.name
        return str(self.op_type)

    def to_tree(self) -> Tuple[str, Tuple[Any, ...]]:
        return (str(self), tuple(map(lambda p: p.to_tree(), self.children)))


class LogicalPlanBuilder:
    def __init__(self, table: Plan) -> None:
        self.root = table

    def join(self, plan: Plan) -> "LogicalPlanBuilder":
        self.root = Plan(
            (self.root, plan),
            LogicalType.InnerJoin,
            self.root.row_cnt * plan.row_cnt,
            None,
        )
        return self

    def build(self) -> Plan:
        return self.root


class TestPlan(unittest.TestCase):
    def test_plan(self) -> None:
        left = (
            LogicalPlanBuilder(Plan((), LogicalType.Table, 100, "t1"))
            .join(Plan((), LogicalType.Table, 200, "t2"))
            .build()
        )

        right = (
            LogicalPlanBuilder(Plan((), LogicalType.Table, 300, "t3"))
            .join(Plan((), LogicalType.Table, 400, "t4"))
            .build()
        )

        plan = LogicalPlanBuilder(left).join(right).build()
        print(tree_printer(plan.to_tree()))
