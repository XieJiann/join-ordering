from columbia.memo.expr_group import Expr
from columbia.memo.memo import Memo
from columbia.rule import RuleSet
from columbia.task import *


def optimize(plan: Expr) -> None:
    rule_set = RuleSet()
    memo = Memo(rule_set)
    memo.record_plan(plan, None)
    print(memo)
    # task_stack = []
    # task_stack.append(O_Group(memo.root()))
    # context = Context()
    # while not task_stack.empty():
    #     task  = task_stack.pop()
    #     task.execute(context, task_stack)
