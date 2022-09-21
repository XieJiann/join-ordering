from enum import Enum
from typing import Tuple, List, Union
from columbia.memo.expr_group import Expr, ExprType


class RuleType(Enum):
    Logical = 0
    Physical = 1


"""
(ExprType, ()): Leaf Expr
(ExprType, (PatternType)): Unary Expr
(ExprType, (PatternType, PatternType)): Binary Expr
"""
PatternType = Union[
    Tuple[ExprType, Tuple["()"]],
    Tuple[ExprType, Tuple["PatternType"]],
    Tuple[ExprType, Tuple["PatternType", "PatternType"]],
]


class Rule:
    def __init__(self, promise: int, type: RuleType) -> None:
        self.type: RuleType = type
        self.id = -1
        self.promise = promise
        self.pattern: PatternType = (ExprType.AnyExpr, ())

    def check(self, expr: Expr) -> bool:  # type: ignore
        pass

    def transform(self, input: Expr) -> List[Expr]:  # type: ignore
        pass

    def set_id(self, id: int) -> None:
        self.id = id

    def is_logical(self) -> bool:
        return self.type == RuleType.Logical

    def match_root(self, expr: Expr) -> bool:
        return len(self.pattern) == 0 or self.pattern[0] == expr.type

    def children_pattern(
        self,
    ) -> Tuple[()] | Tuple[PatternType] | Tuple[PatternType, PatternType]:
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
            ExprType.LogicalInnerJoin,
            ((ExprType.AnyExpr, ()), (ExprType.AnyExpr, ())),
        )

    def check(self, expr: Expr) -> bool:
        return True

    def transform(self, input: Expr) -> List[Expr]:
        new_expr = Expr(
            input.type,
            input.children,
            input.group,
            input.name,
            input.row_cnt,
        )
        new_expr.set_children((input.child_at(1), input.child_at(0)))
        return [new_expr]
