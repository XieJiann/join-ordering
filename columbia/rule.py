from enum import Enum, auto
from typing import Dict, List, Union
from columbia.memo.expr_group import Expr, ExprType


class RuleType(Enum):
    Logical = auto()
    Physical = auto()


PatternType = Union[ExprType, Dict[ExprType, List["PatternType"]]]


class Rule:
    def __init__(self) -> None:
        self.type: RuleType = RuleType.Logical
        self.id = -1

    def check(self, expr: Expr) -> bool:  # type: ignore
        pass

    def transform(self, input: Expr) -> List[Expr]:  # type: ignore
        pass

    def set_id(self, id: int) -> None:
        self.id = id

    def get_type(self) -> RuleType:
        return self.type


class RuleSet:
    def __init__(self) -> None:
        self.logical_set: List[Rule] = []
        self.physical_set: List[Rule] = []
        self.add_rule(ComRule())

    def add_rule(self, rule: Rule):
        rule.set_id(len(self.physical_set) + len(self.logical_set))
        if rule.get_type() == RuleType.Logical:
            self.logical_set.append(rule)
        else:
            self.physical_set.append(rule)


class ComRule(Rule):
    def __init__(self) -> None:
        super().__init__()
        self.pattern: PatternType = ExprType.LogicalInnerJoin
        self.type = RuleType.Logical

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
        return [new_expr]
