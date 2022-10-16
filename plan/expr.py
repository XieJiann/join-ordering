from enum import Enum, auto
from typing import Any, Optional, Tuple

from catalog.catalog import Column, Table


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
        The context can be:
            CostanttVal:  constant value
            ColumnRef: Column
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

    def tables(self):
        tables: set[Table] = set()
        # Now we just process columnref
        if self.type == ExpressionType.ColumnRef:
            assert isinstance(self.context, Column)
            tables.add(self.context.table())
        return tables

    def __eq__(self, __o: object) -> bool:
        assert isinstance(__o, Expression)
        return hash(self) == hash(__o)

    def __str__(self) -> str:
        if (
            self.type == ExpressionType.ColumnRef
            or self.type == ExpressionType.ConstantVal
        ):
            return str(self.context)
        return str(ExpressionType)
