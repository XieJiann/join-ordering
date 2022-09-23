from typing import List, Optional, Tuple
from columbia.memo.memo import Context
from columbia.rule.rule import Rule
from plan.plan import LogicalType, OpType, Plan


class Expr:
    def __init__(
        self,
        type: OpType,
        children: Tuple["Group", ...],
        group: Optional["Group"],
        name: Optional[str],
        row_cnt: int,
    ) -> None:
        """
        The Expr is the basic node in optimizer
        """
        self.type = type
        self.children = children
        self.rule_mask = 0
        self.group = group
        self.name = name
        self.row_cnt = row_cnt

    def set_applied(self, rule: Rule) -> None:
        self.rule_mask |= rule.id

    def applied(self, rule: Rule) -> bool:
        return (self.rule_mask & rule.id) != 0

    def is_logical(self) -> bool:
        return self.type.is_logical()

    def set_group(self, group: "Group") -> "Expr":
        self.group = group
        return self

    def set_children(
        self,
        children: "Tuple[Group,...]",
    ) -> "Expr":
        self.children = children
        return self

    def children_size(self) -> int:
        return len(self.children)

    def is_leaf(self) -> bool:
        return self.children == ()

    def copy(self) -> "Expr":
        return Expr(self.type, self.children, self.group, self.name, self.row_cnt)

    def __hash__(self) -> int:
        return hash((self.type, self.name, self.children))

    def __eq__(self, __o: object) -> bool:
        return hash(self) == hash(__o)


class Group:
    def __init__(self, gid: int) -> None:
        self.gid = gid
        self.logical_exprs: List[Expr] = []
        self.physical_exprs: List[Expr] = []

        self.explored = False
        # the winner matain the idx of the expr with the lowest cost
        self.winner = None

        self.row_cnt = None

        self.cost_lower_bound = -1  # useless?

    def set_explored(self) -> None:
        self.explored = True

    def record_expr(self, expr: Expr) -> None:
        if expr.is_logical():
            self.logical_exprs.append(expr)
        else:
            self.physical_exprs.append(expr)

    def has_winner(self, context: Context) -> bool:
        # The properties has not been supported yet
        assert context.properties is None
        return self.winner != None

    def __hash__(self) -> int:
        return self.gid

    def __eq__(self, __o: object) -> bool:
        return self.gid == hash(__o)


class LeafGroup(Plan):
    def __init__(self, group: Group) -> None:
        super().__init__((), LogicalType.Leaf, -1, None)
        self.group = group

    def __hash__(self) -> int:
        return hash(self.group)

    def __eq__(self, __o: object) -> bool:
        assert isinstance(__o, Group)
        return self.group == __o
