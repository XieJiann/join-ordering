from enum import Enum, auto
from typing import Any, Optional, Tuple


class ExpressionType(Enum):
    ConstantVal = auto()
    ColumnRef = auto()


class Expression:
    def __init__(
        self,
        e_type: ExpressionType,
        children: Tuple["Expression", ...],
        context: Optional[Any],
    ) -> None:
        """
        Each expression return a column value with the same type
        The context is for some constant value for
        """
        self.type = e_type
        self.children = children
        self.context = context

    def count_exprs(self) -> int:
        """
        This function is used to calculated the number of expression
        And more expression brings lower promise due to the deviation
        """
        if self.type == ExpressionType.ColumnRef:
            return 1
        return sum(map(lambda e: e.count_exprs(), self.children)) + 1

    def __hash__(self) -> int:
        return hash((self.type, self.context, self.children))

    def __eq__(self, __o: object) -> bool:
        assert isinstance(__o, Expression)
        return hash(self) == hash(__o)
