from enum import Enum, auto
from typing import Any, List, Optional, Tuple
from catalog.catalog import Column


class ExpressionType(Enum):
    ConstantVal = auto()
    ColumnRef = auto()


class Expression:
    def __init__(
        self,
        e_type: ExpressionType,
        children: Tuple["Expression", ...],
        columns: List[Column],
        constant_val: Optional[Any],
    ) -> None:
        self.columns = columns
        self.type = e_type
        self.children = children
        self.constant_val = constant_val

    def count(self) -> int:
        if self.type == ExpressionType.ColumnRef:
            return 1
        return sum(map(lambda e: e.count(), self.children)) + 1

    def __hash__(self) -> int:
        return hash((self.type, self.constant_val, tuple(self.columns), self.children))
