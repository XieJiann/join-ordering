from columbia import optimizer as c_optimizer
from plan.plan import LogicalPlanBuilder, LogicalType, Plan

plan: Plan = (
    LogicalPlanBuilder(Plan((), LogicalType.Table, 2, "t1"))
    .join(Plan((), LogicalType.Table, 1, "t2"))
    .join(Plan((), LogicalType.Table, 3, "t3"))
    .build()
)
if plan is not None:
    c_optimizer.optimize(plan)
