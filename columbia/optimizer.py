from columbia.memo.memo import Memo
from columbia.memo.context import Context
from columbia.rule.rule import RuleSet
from columbia.task.task import O_Group
from plan.plan import Plan


def optimize(plan: Plan) -> None:
    memo = Memo(plan)
    rule_set = RuleSet()
    context = Context(float("inf"), rule_set)
    context.push_task(O_Group(memo.root, context))
    print(memo)
    # while not task_stack.empty():
    #     task  = task_stack.pop()
    #     task.execute(context, task_stack)
