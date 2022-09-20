from typing import Optional
from columbia.memo.expr_group import Expr, ExprType


class PlanBuilder:
    def __init__(self) -> None:
        self.plan: Optional[Expr] = None

    def join(self, name: str, row_cnt: int) -> "PlanBuilder":
        table = Expr(ExprType.LogicalTable, (), None, name, row_cnt)
        if self.plan is None:
            self.plan = table
        else:
            self.plan = Expr(
                ExprType.LogicalInnerJoin,
                (self.plan, table),
                None,
                None,
                row_cnt * self.plan.row_cnt,
            )
        return self

    def build(self) -> Expr:
        assert self.plan != None
        return self.plan
