from columbia.memo.memo import Context, Memo
from columbia.rule.rule import RuleSet
from columbia.task import *
from plan.plan import Plan


def optimize(plan: Plan) -> None:
    memo = Memo()
    memo.record_plan(plan, None)
    rule_set = RuleSet()
    context = Context(float("inf"), rule_set)
    context.push_task(O_Group(memo.root(), context))
    # while not task_stack.empty():
    #     task  = task_stack.pop()
    #     task.execute(context, task_stack)
