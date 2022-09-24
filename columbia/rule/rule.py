from enum import Enum
from typing import Tuple, List
from plan.plan import LogicalType, PhyiscalType, Plan
from typing import Tuple, Union
from plan.plan import OpType

"""
(ExprType, ()): Leaf Expr
(ExprType, (PatternType)): Unary Expr
(ExprType, (PatternType, PatternType)): Binary Expr
"""

PatternType = Union[
    Tuple[OpType, Tuple["()"]],
    Tuple[OpType, Tuple["PatternType"]],
    Tuple[OpType, Tuple["PatternType", "PatternType"]],
]


class RuleType(Enum):
    Logical = 0
    Physical = 1


class Rule:
    def __init__(self, promise: int, type: RuleType) -> None:
        self.type: RuleType = type
        self.id = -1
        self.promise = promise
        self.pattern: PatternType = (LogicalType.Leaf, ())
        self.name = "rule"

    def check(self, expr: Plan) -> bool:  # type: ignore
        pass

    def transform(self, input: Plan) -> List[Plan]:  # type: ignore
        pass

    def set_id(self, id: int) -> None:
        self.id = id

    def is_logical(self) -> bool:
        return self.type == RuleType.Logical

    def children_pattern(
        self,
    ) -> Tuple[PatternType, ...]:
        return self.pattern[1]

    def __str__(self) -> str:
        return self.name


class RuleSet:
    def __init__(self) -> None:
        self.rule_list: List[Rule] = []
        self.add_rule(ComRule())
        self.add_rule(NSLRule())
        sorted(self.rule_list, key=lambda v: v.promise)

    def add_rule(self, rule: Rule) -> None:
        rule.set_id(len(self.rule_list))
        self.rule_list.append(rule)


class ComRule(Rule):
    def __init__(self) -> None:
        super().__init__(1, RuleType.Logical)
        self.pattern: PatternType = (
            LogicalType.InnerJoin,
            ((LogicalType.Leaf, ()), (LogicalType.Leaf, ())),
        )
        self.name = "ComRule"

    def check(self, expr: Plan) -> bool:
        return True

    def transform(self, input: Plan) -> List[Plan]:
        return [input.set_children((input.children[1], input.children[0]))]


class NSLRule(Rule):
    def __init__(self) -> None:
        super().__init__(2, RuleType.Logical)
        self.pattern: PatternType = (
            LogicalType.InnerJoin,
            ((LogicalType.Leaf, ()), (LogicalType.Leaf, ())),
        )
        self.name = "NSLRule"

    def check(self, expr: Plan) -> bool:
        return True

    def transform(self, input: Plan) -> List[Plan]:
        return [Plan(input.children, PhyiscalType.NSLJoin, input.row_cnt, input.name)]
