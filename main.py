from columbia import optimizer as c_optimizer
from plan.plan import LogicalPlanBuilder, LogicalType, Plan, tree_printer
from loguru import logger
from sys import stdout

logger.remove()
logger.add(stdout, level="INFO")

plan: Plan = (
    LogicalPlanBuilder(Plan((), LogicalType.Table, 1, "t1"))
    .join(Plan((), LogicalType.Table, 3, "t3"))
    .join(Plan((), LogicalType.Table, 2, "t2"))
    .join(Plan((), LogicalType.Table, 4, "t4"))
    .join(Plan((), LogicalType.Table, 5, "t5"))
    .join(Plan((), LogicalType.Table, 6, "t6"))
    .build()
)
if plan is not None:
    winner, cost = c_optimizer.optimize(plan)
print(cost)
print(tree_printer(winner.to_tree()))
