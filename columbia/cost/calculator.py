import math
from catalog.catalog import Column
from columbia.memo.expr_group import GroupExpr
from plan.expr import ExpressionType
from plan.plan import EnforceType, LogicalType, PhyiscalType


class StatsCalculator:
    def __init__(self) -> None:
        return

    def estimate(self, expr: GroupExpr):
        match expr.type():
            case LogicalType.InnerJoin:
                self.estimate_inner_join(expr)
            case LogicalType.Get:
                self.estimate_get(expr)
            case _:
                assert False, f"Unknown expression {expr.type()} when estimate stats"

    def estimate_inner_join(self, expr: GroupExpr):
        assert expr.content.expressions[0].type == ExpressionType.ConstantVal
        for l_col, l_stat in expr.children[0].logical_profile.profile.items():
            for r_col, r_stat in expr.children[1].logical_profile.profile.items():
                expr.group.logical_profile.set_stats(
                    l_col, l_stat.frequency * r_stat.frequency
                )
                expr.group.logical_profile.set_stats(
                    r_col, l_stat.frequency * r_stat.frequency
                )

    def estimate_get(self, group_expr: GroupExpr):
        for expr in group_expr.content.expressions:
            col = expr.context
            assert isinstance(col, Column)
            group_expr.group.logical_profile.set_stats(col, col.frequency())


class CostCalculator:
    def __init__(self) -> None:
        return

    def estimate(self, expr: GroupExpr):
        """
        This function return the cost of this expr
        """
        n = expr.group.logical_profile.get_frequency()
        match expr.type():
            case PhyiscalType.NLJoin:
                return n
            case PhyiscalType.Scan:
                return n
            case EnforceType.Sort:
                return n * max(1, math.log(n))
            case EnforceType.Hash:
                return n
            case _:
                assert False, f"Unknown expression {expr.type()} when estimate cost"
