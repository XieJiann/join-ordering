from itertools import chain, product
from typing import Any, Dict, List, Tuple
from plan.properties import PropertySet
from columbia.rule.rule import Rule
from plan.plan import LogicalType, OpType, Plan, PlanContent
from columbia.cost.statistics import LogicalProfile


class GroupExpr:
    def __init__(self, children: Tuple["Group", ...], content: PlanContent) -> None:
        """
        The GroupExpr is the basic node in optimizer
        """
        self.content = content
        self.children = children
        self.rule_mask = 0

    def set_applied(self, rule: Rule) -> None:
        self.rule_mask |= 1 << rule.id

    def applied(self, rule: Rule) -> bool:
        return (self.rule_mask & (1 << rule.id)) != 0

    def is_logical(self) -> bool:
        return self.content.op_type.is_logical()

    def set_group(self, group: "Group") -> "GroupExpr":
        self.group = group
        return self

    def set_children(
        self,
        children: "Tuple[Group,...]",
    ) -> "GroupExpr":
        self.children = children
        return self

    def children_size(self) -> int:
        return len(self.children)

    def get_group(self) -> "Group":
        assert self.group is not None
        return self.group

    def is_leaf(self) -> bool:
        return self.children == ()

    def copy(self) -> "GroupExpr":
        return GroupExpr(self.children, self.content)

    def all_plan(self) -> List[Plan]:
        group_plans = map(lambda g: g.all_plan(self.is_logical()), self.children)
        return [
            Plan.from_content(children, self.content)
            for children in product(*group_plans)
        ]

    def type(self) -> OpType:
        return self.content.op_type

    def __hash__(self) -> int:
        return hash((self.content, self.children))

    def __eq__(self, __o: object) -> bool:
        return hash(self) == hash(__o)

    def __str__(self) -> str:
        return str(self.content)

    def is_derived(self) -> bool:
        return self.group.is_derived()


class Group:
    def __init__(self, gid: int) -> None:
        self.gid = gid
        self.logical_exprs: List[GroupExpr] = []
        self.physical_exprs: List[GroupExpr] = []

        self.explored = False
        # the winner matain the idx of the expr with the lowest cost
        self.winner: Dict[PropertySet, Tuple[GroupExpr, float]] = {}

        self.logical_profile = LogicalProfile()

        self.cost_lower_bound = -1  # useless?

    def set_explored(self) -> None:
        self.explored = True

    def record_expr(self, expr: GroupExpr) -> None:
        if expr.is_logical():
            self.logical_exprs.append(expr)
        else:
            self.physical_exprs.append(expr)

    def has_winner(self, property_set: PropertySet) -> bool:
        return property_set in self.winner

    def winner_cost(self, property_set: PropertySet) -> float:
        assert self.has_winner(property_set)
        return self.winner[property_set][1]

    def set_winner(self, property_set: PropertySet, expr: GroupExpr, cost: float):
        if not self.has_winner(property_set) or self.winner_cost(property_set) > cost:
            self.winner[property_set] = (expr, cost)

    def winner_plan(self, property_set: PropertySet) -> Plan:
        assert property_set in self.winner
        winner_expr = self.winner[property_set][0]
        children = tuple(
            map(lambda g: g.winner_plan(property_set), winner_expr.children)
        )
        return Plan.from_content(children, winner_expr.content)

    def all_exprs(self) -> List[GroupExpr]:
        return self.logical_exprs + self.physical_exprs

    def all_plan(self, logical: bool) -> List[Plan]:
        if logical:
            return list(chain(*map(lambda e: e.all_plan(), self.logical_exprs)))
        return list(chain(*map(lambda e: e.all_plan(), self.physical_exprs)))

    def get_promise_expr(self):
        # This function return the expr with highest promise for stats derived
        # That is with the least expression
        return min(self.logical_exprs, key=lambda e: e.content.cost_promise())

    def __hash__(self) -> int:
        return self.gid

    def __eq__(self, __o: object) -> bool:
        return self.gid == hash(__o)

    def __str__(self) -> str:
        return str(
            tuple(map(lambda expr: str(expr), self.logical_exprs + self.physical_exprs))
        )

    def is_derived(self) -> bool:
        return self.logical_profile.frequency is None


class LeafGroup(Plan):
    def __init__(self, group: Group) -> None:
        super().__init__(
            (), LogicalType.Leaf, group.logical_exprs[0].content.expressions
        )
        self.group = group

    def __str__(self) -> str:
        return str(self.group.logical_exprs[0])

    def to_tree(self) -> Tuple[str, Tuple[Any, ...]]:
        return (str(self.group.logical_exprs[0]), ())

    def __hash__(self) -> int:
        return hash(self.group)

    def __eq__(self, __o: object) -> bool:
        assert isinstance(__o, Group)
        return self.group == __o
