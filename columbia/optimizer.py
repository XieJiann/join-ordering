from columbia.memo.memo import Memo
from columbia.memo.context import Context
from columbia.memo.properties import PropertySet
from columbia.rule.rule import RuleSet
from columbia.task.task import O_Group
from plan.plan import Plan


def optimize(plan: Plan) -> Plan:
    memo = Memo(plan)
    rule_set = RuleSet()
    context = Context(memo, float("inf"), rule_set, PropertySet(), [])
    context.push_task(O_Group(memo.root, context))
    while not context.has_no_task():
        task = context.pop_task()
        task.execute()
    return memo.get_winner(context.property_set)
