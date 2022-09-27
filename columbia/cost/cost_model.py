from columbia.memo.expr_group import GroupExpr


def cost_for_expr(expr: GroupExpr) -> float:
    return expr.group.logical_profile.get_frequency()
