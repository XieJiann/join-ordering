from functools import reduce
from itertools import chain, product
from typing import Any, Dict, List, Tuple
from catalog.catalog import Table
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
        """
        This map maps the outputproperty with input property, note it's only valid for physical operator
        It's init in optimize_input task
        It's used when choose the best plan, that is we shound select the best child plan according the input property set
        XJ: 
            Do we need a map, in fact I think a physiacl g_expr can only output one property, therefore a pair maybe enough
        """
        self.property_map: Dict[PropertySet, Tuple[PropertySet, ...]] = {}

    def set_applied(self, rule: Rule) -> None:
        self.rule_mask |= 1 << rule.id

    def get_input_property(self, prop: PropertySet):
        assert prop in self.property_map, f"{str(self)} has no input of {prop}"
        return self.property_map[prop]

    def derive_tables(self):
        tables: set[Table] = self.content.tables()
        return reduce(lambda a, b: a.union(b.tables), self.children, tables)

    def set_property(
        self,
        output_property: PropertySet,
        input_property: Tuple[PropertySet, ...],
    ):
        # print(
        #     f"set property {output_property} <- {tuple(map(lambda k:str(k), input_property))} for {str(self)}"
        # )
        self.property_map[output_property] = input_property

    def applied(self, rule: Rule) -> bool:
        return (self.rule_mask & (1 << rule.id)) != 0

    def is_logical(self) -> bool:
        return self.content.op_type.is_logical()

    def is_enforcer(self) -> bool:
        return self.content.op_type.is_enforcer()

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
        return str(self.content) + "_" + str(self.group.gid)

    def is_derived(self) -> bool:
        return self.group.is_derived()


class Group:
    def __init__(self, gid: int, tables: set[Table]) -> None:
        self.gid = gid
        self.logical_exprs: List[GroupExpr] = []
        self.physical_exprs: List[GroupExpr] = []
        self.enforce_exprs: List[GroupExpr] = []
        self.explored = False
        # the winner matain the idx of the expr with the lowest cost
        self.winner: Dict[PropertySet, Tuple[GroupExpr, float]] = {}
        self.logical_profile = LogicalProfile()
        self.cost_lower_bound = -1  # useless?
        self.tables: set[Table] = tables

    def set_explored(self) -> None:
        self.explored = True

    def record_expr(self, expr: GroupExpr) -> None:
        if len(self.tables) == 0:
            # we init the tables when first record logical expr in this group
            pass
        expr.set_group(self)
        if expr.is_logical():
            self.logical_exprs.append(expr)
        elif expr.is_enforcer():
            self.enforce_exprs.append(expr)
        else:
            self.physical_exprs.append(expr)

    def has_winner(self, property_set: PropertySet) -> bool:
        return property_set in self.winner.keys()

    def winner_cost(self, property_set: PropertySet) -> float:
        assert self.has_winner(property_set)
        return self.winner[property_set][1]

    def set_winner(self, property_set: PropertySet, expr: GroupExpr, cost: float):
        # print(f"set winner {property_set} in {self.gid} is {str(expr)}")
        if not self.has_winner(property_set) or self.winner_cost(property_set) > cost:
            self.winner[property_set] = (expr, cost)

    def winner_plan(self, property_set: PropertySet) -> Plan:
        assert (
            property_set in self.winner
        ), f"{property_set} has not been optimized in {self.gid}"
        winner_expr = self.winner[property_set][0]
        if winner_expr.is_enforcer():
            plan = self.winner_plan(winner_expr.get_input_property(property_set)[0])
            plan = Plan.from_content((plan,), winner_expr.content)
        else:
            children_prop = winner_expr.get_input_property(property_set)
            assert len(children_prop) == len(winner_expr.children)
            children = tuple(
                map(
                    lambda i: winner_expr.children[i].winner_plan(children_prop[i]),
                    range(len(children_prop)),
                )
            )
            plan = Plan.from_content(children, winner_expr.content)
        return plan

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
        return (
            str(
                tuple(
                    map(
                        lambda expr: str(expr),
                        self.logical_exprs + self.physical_exprs + self.enforce_exprs,
                    )
                )
            )
            + "_"
            + str(self.gid)
        )

    def is_derived(self) -> bool:
        return self.logical_profile.frequency is None


class LeafGroup(Plan):
    """
    It's plan that represent a group ranther a expr
    """

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
