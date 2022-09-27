from gettext import Catalog
from catalog.catalog import Catalog, DataType
from columbia import optimizer as c_optimizer
from plan.plan import LogicalPlanBuilder, LogicalType, Plan, tree_printer
from loguru import logger
from sys import stdout

from plan.utils import make_column_ref, make_true

logger.remove()
logger.add(stdout, level="INFO")

catalog = Catalog()
t1 = catalog.create_table("t1", {"v": DataType.Int32}, 1)
t2 = catalog.create_table("t2", {"v": DataType.Int32}, 2)
t3 = catalog.create_table("t3", {"v": DataType.Int32}, 3)
t4 = catalog.create_table("t4", {"v": DataType.Int32}, 4)
t5 = catalog.create_table("t5", {"v": DataType.Int32}, 5)
t6 = catalog.create_table("t6", {"v": DataType.Int32}, 6)
t7 = catalog.create_table("t7", {"v": DataType.Int32}, 7)

plan: Plan = (
    LogicalPlanBuilder(Plan((), LogicalType.Get, make_column_ref(t1, "v")))
    .join(Plan((), LogicalType.Get, make_column_ref(t3, "v")), make_true())
    .join(Plan((), LogicalType.Get, make_column_ref(t7, "v")), make_true())
    .join(Plan((), LogicalType.Get, make_column_ref(t2, "v")), make_true())
    .join(Plan((), LogicalType.Get, make_column_ref(t6, "v")), make_true())
    .join(Plan((), LogicalType.Get, make_column_ref(t5, "v")), make_true())
    .join(Plan((), LogicalType.Get, make_column_ref(t4, "v")), make_true())
    .build()
)
if plan is not None:
    winner, cost = c_optimizer.optimize(plan)
print(cost)
print(tree_printer(winner.to_tree()))
