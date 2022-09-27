from typing import Tuple
from columbia.memo.expr_group import GroupExpr
from columbia.rule.rule import PatternType
from plan.plan import OpType


def match_root(pattern: PatternType, expr: GroupExpr) -> bool:
    return pattern[0] == expr.content.op_type


def pattern_root(pattern: PatternType) -> OpType:
    return pattern[0]


def pattern_children(patttern: PatternType) -> Tuple[PatternType, ...]:
    return patttern[1]


def child_at(pattern: PatternType, i: int) -> PatternType:
    return pattern[1][i]
