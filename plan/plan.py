from enum import Enum, auto
from typing import Any, List, Tuple
from plan.expr import Expression


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
                res.append(f"{' '*len(tree[0])}        {sub_child}")
        return res

    res = format_subtree(tree)
    return "\n".join(res)


class OpType(Enum):
    def is_logical(self) -> bool:
        return False


class LogicalType(OpType):
    InnerJoin = auto()
    Get = auto()
    Leaf = auto()

    def is_logical(self) -> bool:
        return True


class PhyiscalType(OpType):
    NLJoin = auto()
    HashJoin = auto()
    Scan = auto()


class PlanContent:
    def __init__(self, op_type: OpType, expressions: Tuple[Expression, ...]) -> None:
        self.op_type = op_type
        self.expressions = expressions

    def cost_promise(self) -> float:
        return 1 / sum(map(lambda e: e.count_exprs(), self.expressions))

    def __str__(self) -> str:
        if self.op_type == LogicalType.Get or self.op_type == PhyiscalType.Scan:
            return str(self.expressions[0].context)
        return str(self.op_type).split(".")[-1]

    def __hash__(self) -> int:
        return hash((self.op_type, self.expressions))


class Plan:
    def __init__(
        self,
        children: Tuple["Plan", ...],
        op_type: OpType,
        expression: Tuple[Expression, ...],
    ) -> None:
        self.children: Tuple[Plan, ...] = children
        self.content = PlanContent(op_type, expression)

    @staticmethod
    def from_content(children: Tuple["Plan", ...], content: PlanContent) -> "Plan":
        return Plan(children, content.op_type, content.expressions)

    def copy(self) -> "Plan":
        return Plan.from_content(self.children, self.content)

    def __str__(self) -> str:
        return str(self.content)

    def set_children(self, children: Tuple["Plan", ...]) -> "Plan":
        self.children = children
        return self

    def to_tree(self) -> Tuple[str, Tuple[Any, ...]]:
        return (str(self), tuple(map(lambda p: p.to_tree(), self.children)))


class LogicalPlanBuilder:
    def __init__(self, table: Plan) -> None:
        self.root = table

    def join(
        self, plan: Plan, expressions: Tuple[Expression, ...]
    ) -> "LogicalPlanBuilder":
        self.root = Plan((self.root, plan), LogicalType.InnerJoin, expressions)
        return self

    def build(self) -> Plan:
        return self.root
