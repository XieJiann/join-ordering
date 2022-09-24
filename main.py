from columbia import optimizer as c_optimizer
from plan.plan import LogicalPlanBuilder, LogicalType, Plan

plan = (
    LogicalPlanBuilder(Plan((), LogicalType.Table, 100, "t1"))
    .join(Plan((), LogicalType.Table, 200, "t2"))
    .join(Plan((), LogicalType.Table, 300, "t3"))
    .build()
)
if plan is not None:
    c_optimizer.optimize(plan)
