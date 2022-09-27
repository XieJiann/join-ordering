from typing import Tuple
from columbia.cost.calculator import StatsCalculator
from columbia.memo.memo import Memo
from columbia.memo.context import Context
from columbia.memo.properties import PropertySet
from columbia.rule.rule import RuleSet
from columbia.task.task import DeriveStats, O_Group
from plan.plan import Plan


def optimize(plan: Plan) -> Tuple[Plan, float]:
    memo = Memo(plan)
    rule_set = RuleSet()
    context = Context(
        memo, float("inf"), rule_set, PropertySet(), [], StatsCalculator()
    )
    context.push_task(O_Group(memo.root, context))
    context.push_task(DeriveStats(memo.root.logical_exprs[0], context))
    while not context.has_no_task():
        task = context.pop_task()
        task.execute()
    return memo.get_winner(context.property_set)
