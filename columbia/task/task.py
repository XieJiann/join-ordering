from loguru import logger
from columbia.cost.cost import cost_for_expr
from columbia.memo.expr_group import Expr, Group
from columbia.memo.context import Context
from columbia.rule.rule import Rule
from columbia.rule.pattern import match_root, pattern_children
from columbia.rule.rule_binder import ExprBinder
from columbia.task.abstract_task import Task


class O_Group(Task):
    def __init__(self, group: Group, context: Context, level: int = 0) -> None:
        self.context = context
        self.group = group
        # The level only used for print trace
        self.level = level

    def execute(self) -> None:
        ident = "\t" * self.level
        logger.debug(
            f"{ident} O_Group {str(self.group)} with winner {self.group.has_winner(self.context.property_set)}"
        )

        if self.group.cost_lower_bound > self.context.cost_upper_bound:
            # TODO[xj]: 看起来毫无用处，应该删去
            return
        if self.group.has_winner(self.context.property_set):
            return
        for expr in self.group.logical_exprs:
            self.context.push_task(O_Expr(expr, self.context, False, self.level + 1))
        for expr in self.group.physical_exprs:
            self.context.push_task(O_Inputs(expr, self.context, self.level + 1))


class E_Group(Task):
    def __init__(self, group: Group, context: Context, level: int) -> None:
        self.context = context
        self.group = group
        self.level = level

    def execute(self) -> None:
        ident = "\t" * self.level
        logger.debug(f"{ident}E_Group {str(self.group)}")
        if self.group.explored:
            return
        for expr in self.group.logical_exprs:
            self.context.push_task(O_Expr(expr, self.context, True, self.level + 1))
        # 因为不存在环，所以可以直接mark explored
        self.group.set_explored()


class O_Expr(Task):
    def __init__(
        self, expr: Expr, context: Context, exploring: bool, level: int
    ) -> None:
        self.context = context
        self.expr = expr
        self.exploring = exploring
        self.level = level

    def execute(self) -> None:
        ident = "\t" * self.level
        logger.debug(f"{ident}O_Expr [exploring={self.exploring}] {self.expr}")
        valid_rules = filter(
            lambda r: match_root(r.pattern, self.expr)
            and not self.expr.applied(r)
            and (not self.exploring or r.is_logical()),
            self.context.rule_set.rule_list,
        )
        for rule in valid_rules:
            self.context.push_task(
                ApplyRule(self.expr, rule, self.context, self.exploring, self.level + 1)
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
                    self.context.push_task(E_Group(group, self.context, self.level + 1))


class O_Inputs(Task):
    def __init__(self, expr: Expr, context: Context, level: int) -> None:
        self.context = context
        self.expr = expr
        self.cur_child_idx = -1
        self.prev_child_idx = -1  # This variable marks the child that is optimizing
        self.cur_total_cost = 0
        self.level = level

    def execute(self) -> None:
        ident = "\t" * self.level
        logger.debug(
            f"{ident}O_Inputs {self.expr} with {self.cur_child_idx+1} children with bound {self.context.cost_upper_bound}"
        )

        if self.cur_child_idx == -1:
            self.cur_total_cost = cost_for_expr(self.expr)
            if self.cur_total_cost > self.context.cost_upper_bound:
                return
            self.cur_child_idx = 0

        last_optimized = self.cur_child_idx
        for child_group in self.expr.children[last_optimized:]:
            if child_group.has_winner(self.context.property_set):
                self.cur_child_idx += 1
                self.cur_total_cost += child_group.winner_cost(
                    self.context.property_set
                )
                if self.cur_total_cost > self.context.cost_upper_bound:
                    return
            elif self.prev_child_idx != self.cur_child_idx:
                """
                Sometimes the O_Group can't get the optimal expr for this group beacause of pruning in loc 110/115
                The O_Input will be called after the invalid O_Group, and to avoid push O_Group repeatly, we need to mark this case.
                That is prev_child_idx == cur_child_idx, so we will break this loop and set the lower cost in follows
                O_INPUTS                  (cur_child_idx == prev_child_idx and group has no winner)
                    =>  O_INPUTS              ⬆
                    =>  O_GROUP               |
                        => O_Expr             |
                        => O_INPUYS (terminated)
                """
                self.prev_child_idx = self.cur_child_idx
                self.context.push_task(self)
                self.context.push_task(
                    O_Group(child_group, self.context.copy(), self.level + 1)
                )
                return
            else:
                # pruning
                break

        if self.cur_child_idx == len(self.expr.children):
            self.expr.get_group().set_winner(
                self.context.property_set, self.expr, self.cur_total_cost
            )
            self.context.cost_upper_bound = min(
                self.cur_total_cost, self.context.cost_upper_bound
            )


class ApplyRule(Task):
    def __init__(
        self, expr: Expr, rule: Rule, context: Context, exploring: bool, level: int
    ) -> None:
        self.context = context
        self.expr = expr
        self.rule = rule
        self.exploring = exploring
        self.level = level

    def execute(self) -> None:
        ident = "\t" * self.level
        logger.debug(f"{ident}ApplyRule {self.rule} for {self.expr}")
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
                            O_Expr(expr, self.context, self.exploring, self.level + 1)
                        )
                    else:
                        self.context.push_task(
                            O_Inputs(expr, self.context, self.level + 1)
                        )
        self.expr.set_applied(self.rule)
