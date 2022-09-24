from typing import List, Optional, Tuple
from columbia.memo.expr_group import Expr, Group, LeafGroup
from plan.plan import Plan, tree_printer


class Memo:
    def __init__(self, plan: Plan) -> None:
        # root always in the front
        self.groups: List["Group"] = []
        self.expr_dict: "dict[Expr, Group]" = {}
        self.root = self.record_plan(plan, None)[0].get_group()

    def new_group(self) -> Group:
        group = Group(len(self.groups))
        self.groups.append(group)
        return group

    def record_plan(self, plan: Plan, group: Optional[Group]) -> Tuple[Expr, bool]:
        """
        args: we should record the plan into this group. if group is None, we need to construct a new group
        return: The first element is the expr of this plan, and the second element represent whether the expr is new
        """
        if isinstance(plan, LeafGroup):
            # when the plan is a leaf group, we can return any expr in this group
            return (plan.group.all_exprs()[0], False)

        group_children = map(
            lambda p: self.record_plan(p, None)[0].get_group(), plan.children
        )
        expr = Expr(plan.op_type, tuple(group_children), None, plan.name, plan.row_cnt)
        if expr in self.expr_dict:
            return (expr, False)

        if group is None:
            group = self.new_group()
        group.record_expr(expr)
        expr = expr.set_group(group)
        self.expr_dict[expr] = group
        return (expr, True)

    def __str__(self) -> str:
        res = ""
        for plan in self.root.all_plan():
            res += tree_printer(plan.to_tree())
            res += "\n\n ************************** \n\n"
        return res
