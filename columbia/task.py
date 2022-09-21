from columbia.memo.expr_group import Expr, Group, is_logical_leaf
from columbia.memo.memo import Context
from columbia.rule import Rule


class Task:
    def __init__(self) -> None:
        pass

    def execute(self) -> None:
        pass


class O_Group(Task):
    def __init__(self, group: Group, context: Context) -> None:
        self.context = context
        self.group = group

    def execute(self) -> None:
        if self.group.cost_lower_bound > self.context.cost_upper_bound:
            # TODO[xj]: 看起来毫无用处，应该删去
            return

        if self.group.has_winner(self.context):
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
        valid_rules = filter(
            lambda r: r.match_root(self.expr)
            and not self.expr.applied(r)
            and (self.exploring and r.is_logical()),
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
             Table Join
             We don't need explore Table, beacause it's a leaf
            """
            for (i, child_pattern) in enumerate(rule.children_pattern()):
                if is_logical_leaf(child_pattern[0]):
                    self.context.push_task(E_Group(self.expr.child_at(i), self.context))


class O_Inputs(Task):
    def __init__(self, expr: Expr, context: Context) -> None:
        self.context = context
        self.expr = expr

    def execute(self) -> None:
        pass


class ApplyRule(Task):
    def __init__(
        self, expr: Expr, rule: Rule, context: Context, exploring: bool
    ) -> None:
        self.context = context
        self.expr = expr
        self.rule = rule
        self.exploring = exploring

    def execute(self) -> None:
        return super().execute()
