from columbia.memo.expr_group import GroupExpr
from plan.expr import ExpressionType
from plan.plan import LogicalType


class StatsCalculator:
    def __init__(self) -> None:
        return

    def estimate(self, expr: GroupExpr):
        # Maybe a visitor is better than pattern match
        # However, we don't implenment a type for each expr
        match expr.type():
            case LogicalType.InnerJoin:
                self.estimate_inner_join(expr)
            case LogicalType.Get:
                self.estimate_get(expr)
            case _:
                assert False, f"Unknown expression {expr.type()} when estimate stats"

    def estimate_inner_join(self, expr: GroupExpr):
        assert expr.content.expression.type == ExpressionType.ConstantVal
        for l_col, l_stat in expr.children[0].logical_profile.profile.items():
            for r_col, r_stat in expr.children[1].logical_profile.profile.items():
                expr.group.logical_profile.set_stats(
                    l_col, l_stat.frequency * r_stat.frequency
                )
                expr.group.logical_profile.set_stats(
                    r_col, l_stat.frequency * r_stat.frequency
                )

    def estimate_get(self, expr: GroupExpr):
        columns = expr.content.expression.columns
        assert len(columns) != 0
        for col in columns:
            expr.group.logical_profile.set_stats(col, col.frequency())
