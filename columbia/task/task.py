from cgitb import reset
from typing import List, Tuple
from loguru import logger
from columbia.cost.calculator import CostCalculator
from columbia.cost.cost_model import cost_for_expr
from columbia.memo.expr_group import GroupExpr, Group
from columbia.memo.context import Context
from columbia.property.enforcer import Enforcer
from columbia.property.property_deriver import PropertyDeriver
from columbia.rule.rule import Rule
from columbia.rule.pattern import match_root, pattern_children
from columbia.rule.rule_binder import ExprBinder
from columbia.task.abstract_task import Task
from plan.properties import PropertySet


class O_Group(Task):
    def __init__(self, group: Group, context: Context, level: int = 0) -> None:
        self.context = context
        self.group = group
        # The level only used for print trace
        self.level = level

    def execute(self) -> None:
        ident = "\t" * self.level
        logger.debug(
            f"{ident} O_Group {str(self.group)} with property {self.context.property_set} .winner: {self.group.has_winner(self.context.property_set)}"
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
        self, expr: GroupExpr, context: Context, exploring: bool, level: int
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
    def __init__(self, expr: GroupExpr, context: Context, level: int) -> None:
        self.context = context
        self.expr = expr
        self.cur_child_idx = -1
        self.prev_child_idx = -1  # This variable marks the child that is optimizing
        self.cur_total_cost = 0
        self.cur_prop_idx = 0
        self.level = level
        self.out_in_prop: List[Tuple[PropertySet, Tuple[PropertySet, ...]]] = []

    def execute(self) -> None:
        ident = "\t" * self.level
        logger.debug(
            f"{ident}O_Inputs {self.expr} at {self.cur_child_idx+1} children with bound {self.context.cost_upper_bound}"
        )
        if self.cur_child_idx == -1:
            self.cur_total_cost = cost_for_expr(self.expr)
            if self.cur_total_cost > self.context.cost_upper_bound:
                return
            self.cur_child_idx = 0
            self.out_in_prop = PropertyDeriver(
                self.expr, self.context.property_set
            ).derive()

        last_optimized = self.cur_child_idx
        """
        For this group, we need to optimize the task with properties in context.
        Some properties can be passed by children, e.g.
                  | p1 + p2 + p3(enforcer)
                Group
             p1 |   | p2
                G1  G2
        We need to process all combination of properties that can be passed to children, which is calcalated in PropertyDeriver.
        The rest of properties need to enforcer in this group
        """
        for output_prop, children_property in self.out_in_prop[self.cur_prop_idx :]:
            for child_group, child_property in zip(
                self.expr.children[last_optimized:], children_property[last_optimized:]
            ):
                if child_group.has_winner(child_property):
                    self.cur_child_idx += 1
                    self.cur_total_cost += child_group.winner_cost(child_property)
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
                        O_Group(
                            child_group,
                            self.context.copy_with_property(child_property),
                            self.level + 1,
                        )
                    )
                    return
                else:
                    # pruning
                    break

            if self.cur_child_idx == len(self.expr.children):
                # record this expr with output property
                self.expr.set_property(output_prop, children_property)
                self.expr.get_group().set_winner(
                    output_prop, self.expr, self.cur_total_cost
                )
                enforcer = Enforcer(
                    self.context.property_set,
                    output_prop.clone(),
                    self.expr.get_group(),
                )

                enforce_children_property = (output_prop,)
                for enforced_expr, enforce_output_prop in enforcer:
                    # record enforce expr with output property
                    self.expr.get_group().record_expr(enforced_expr)
                    enforced_expr.set_property(
                        enforce_output_prop, enforce_children_property
                    )
                    self.cur_total_cost += CostCalculator().estimate(enforced_expr)
                    enforced_expr.get_group().set_winner(
                        enforcer.output_property(), enforced_expr, self.cur_total_cost
                    )
                    enforce_children_property = (enforce_output_prop,)

                # The cost is responsed to the required property in context
                self.context.cost_upper_bound = min(
                    self.cur_total_cost, self.context.cost_upper_bound
                )

            reset()

    def reset(self):
        self.prev_child_idx = -1
        self.cur_child_idx = 0
        self.cur_total_cost = 0


class ApplyRule(Task):
    def __init__(
        self, expr: GroupExpr, rule: Rule, context: Context, exploring: bool, level: int
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
                    if expr.content.op_type.is_logical():
                        self.context.push_task(
                            O_Expr(expr, self.context, self.exploring, self.level + 1)
                        )
                        self.context.push_task(
                            DeriveStats(expr, self.context, self.level + 1)
                        )
                    else:
                        self.context.push_task(
                            O_Inputs(expr, self.context, self.level + 1)
                        )

        self.expr.set_applied(self.rule)


class DeriveStats(Task):
    def __init__(self, expr: GroupExpr, context: Context, level: int = 0) -> None:
        self.expr = expr
        self.context = context
        self.children_derived = False
        self.level = level

    def execute(self) -> None:
        ident = "\t" * self.level
        logger.debug(f"{ident}DeriveStats {self.expr}")
        if not self.children_derived:
            self.children_derived = True
            self.context.push_task(self)
            for child in self.expr.children:
                self.context.push_task(
                    DeriveStats(child.get_promise_expr(), self.context, self.level + 1)
                )
        else:
            self.context.stats_calculator.estimate(self.expr)
