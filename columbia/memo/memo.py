from typing import List, Optional
from columbia.memo.expr_group import Expr, Group, LeafGroup
from plan.plan import Plan, tree_printer


class Memo:
    def __init__(self, plan: Plan) -> None:
        # root always in the front
        self.groups: List["Group"] = []
        self.expr_dict: "dict[Expr, Group]" = {}
        self.root = self.record_plan(plan, None)

    def new_group(self) -> Group:
        group = Group(len(self.groups))
        self.groups.append(group)
        return group

    def record_plan(self, plan: Plan, group: Optional[Group]) -> Group:
        if isinstance(plan, LeafGroup):
            return plan.group

        group_children = map(lambda p: self.record_plan(p, None), plan.children)
        expr = Expr(plan.op_type, tuple(group_children), None, plan.name, plan.row_cnt)
        if expr in self.expr_dict:
            return self.expr_dict[expr]

        if group is None:
            group = self.new_group()
        group.record_expr(expr)
        self.expr_dict[expr] = group
        return group

    def __str__(self) -> str:
        res = ""
        for plan in self.root.all_plan():
            res += tree_printer(plan.to_tree())
            res += "\n\n ************************** \n\n"
        return res
