from enum import Enum
from typing import Tuple, List, Union
from columbia.memo.expr_group import Expr
from plan.plan import LogicalType, OpType, Plan


class RuleType(Enum):
    Logical = 0
    Physical = 1


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


def match_root(pattern: PatternType, expr: Expr) -> bool:
    return pattern[0] == expr.type


def pattern_root(pattern: PatternType) -> OpType:
    return pattern[0]


def pattern_children(patttern: PatternType) -> Tuple[PatternType, ...]:
    return patttern[1]


def child_at(pattern: PatternType, i: int) -> PatternType:
    return pattern[1][i]


class Rule:
    def __init__(self, promise: int, type: RuleType) -> None:
        self.type: RuleType = type
        self.id = -1
        self.promise = promise
        self.pattern: PatternType = (LogicalType.Leaf, ())

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


class RuleSet:
    def __init__(self) -> None:
        self.rule_list: List[Rule] = []
        self.add_rule(ComRule())
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

    def check(self, expr: Plan) -> bool:
        return True

    def transform(self, input: Plan) -> List[Plan]:
        return [input.set_children((input.children[1], input.children[0]))]
