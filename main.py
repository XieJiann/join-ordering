from columbia import optimizer as c_optimizer
from utils.plan import PlanBuilder

# defile join graph by <nodes, edges>
# right now, we only support clique with inner join
plan_builder = PlanBuilder()
plan = plan_builder.join("t1", 1000).join("t2", 2000).join("t3", 3000).build()

if plan is not None:
    c_optimizer.optimize(plan)
