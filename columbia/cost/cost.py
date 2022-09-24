from columbia.memo.expr_group import Expr


def cost_for_expr(expr: Expr) -> float:
    return expr.row_cnt


def cost_for_plan(expr: Expr) -> float:
    return 0
