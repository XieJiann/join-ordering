from loguru import logger
from columbia.cost.cost import cost_for_expr
from columbia.memo.expr_group import Expr, Group
from columbia.memo.context import Context
from columbia.rule.rule import Rule
from columbia.rule.pattern import match_root, pattern_children
from columbia.rule.rule_binder import ExprBinder
from columbia.task.abstract_task import Task


class O_Group(Task):
    def __init__(self, group: Group, context: Context) -> None:
        self.context = context
        self.group = group

    def execute(self) -> None:
        logger.info(f"O_Group {str(self.group)}")
        if self.group.cost_lower_bound > self.context.cost_upper_bound:
            # TODO[xj]: 看起来毫无用处，应该删去
            return

        if self.group.has_winner(self.context.property_set):
            return

        for expr in self.group.logical_exprs:
            self.context.push_task(O_Expr(expr, self.context, exploring=False))
        for expr in self.group.physical_exprs:
            self.context.push_task(O_Inputs(expr, self.context))


class E_Group(Task):
    def __init__(self, group: Group, context: Context) -> None:
        self.context = context
        self.group = group

    def execute(self) -> None:
        logger.info(f"E_Group {str(self.group)}")
        if self.group.explored:
            return
        for expr in self.group.logical_exprs:
            self.context.push_task(O_Expr(expr, self.context, exploring=True))
        # 因为不存在环，所以可以直接mark explored
        self.group.set_explored()


class O_Expr(Task):
    def __init__(self, expr: Expr, context: Context, exploring: bool) -> None:
        self.context = context
        self.expr = expr
        self.exploring = exploring

    def execute(self) -> None:
        logger.info(f"E_Expr {self.expr}")
        valid_rules = filter(
            lambda r: match_root(r.pattern, self.expr)
            and not self.expr.applied(r)
            and (not self.exploring or r.is_logical()),
            self.context.rule_set.rule_list,
        )
        for rule in valid_rules:
            self.context.push_task(
                ApplyRule(self.expr, rule, self.context, self.exploring)
            )
            """
            Before applying the rule, we should explore the children group for full macthing
               1.Explore children group should be excuted before applying rule
               2.Only the children group of this rule should be explored
               3.The Leaf node isn't needed explored because there is no valid tranformation rule for them

            e.g. For a Pattern:
                Join
               |    |
              Any  Any
             We don't need explore Any Expr, beacause it's a leaf group in plan
            """
            for (group, child_pattern) in zip(
                self.expr.children, pattern_children(rule.pattern)
            ):
                if len(pattern_children(child_pattern)) == 0:
                    self.context.push_task(E_Group(group, self.context))


class O_Inputs(Task):
    def __init__(self, expr: Expr, context: Context) -> None:
        self.context = context
        self.expr = expr
        self.cur_child_idx = -1
        self.cur_total_cost = 0

    def execute(self) -> None:
        logger.info(f"O_Inputs {self.expr}")
        if self.cur_child_idx == -1:
            self.cur_total_cost = cost_for_expr(self.expr)
            self.cur_child_idx = 0

        last_optimized = self.cur_child_idx
        for child_group in self.expr.children[last_optimized:]:
            self.cur_child_idx += 1
            if child_group.has_winner(self.context.property_set):
                self.cur_total_cost += child_group.winner_cost()
                if self.cur_total_cost > self.context.cost_upper_bound:
                    return
            else:
                self.context.push_task(self)
                self.context.push_task(O_Group(child_group, self.context))
                return
        assert self.cur_child_idx == len(self.expr.children)
        self.expr.get_group().set_winner(
            self.context.property_set, self.expr, self.cur_total_cost
        )


class ApplyRule(Task):
    def __init__(
        self, expr: Expr, rule: Rule, context: Context, exploring: bool
    ) -> None:
        self.context = context
        self.expr = expr
        self.rule = rule
        self.exploring = exploring

    def execute(self) -> None:
        logger.info(f"ApplyRule {self.expr} {self.rule}")
        if not match_root(self.rule.pattern, self.expr) or (
            len(pattern_children(self.rule.pattern)) != len(self.expr.children)
        ):
            return
        expr_binder = ExprBinder(self.expr, self.rule.pattern)
        for plan in expr_binder:
            if not self.rule.check(plan):
                continue

            transformed_plans = self.rule.transform(plan)
            for new_plan in transformed_plans:
                expr, is_new = self.context.memo.record_plan(new_plan, self.expr.group)
                if is_new:
                    if expr.type.is_logical():
                        self.context.push_task(
                            O_Expr(expr, self.context, self.exploring)
                        )
                    else:
                        self.context.push_task(O_Inputs(expr, self.context))
