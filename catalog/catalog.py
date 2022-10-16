from enum import Enum, auto
from typing import Any, Dict, List, Tuple


class DataType(Enum):
    Int32 = auto()
    Float64 = auto()
    Bool = auto()


class Column:
    def __init__(self, table: "Table", column_idx: int) -> None:
        self.source = table
        self.column_idx = column_idx

    def table(self):
        return self.source

    def upper_bound(self) -> float:
        return 0

    def lower_bound(self) -> float:
        return 0

    def frequency(self) -> float:
        return self.source.cardinality

    def domain(self) -> Tuple[Any, Any]:
        return (0, 0)

    def __hash__(self) -> int:
        return hash((self.column_idx, self.source))

    def __eq__(self, __o: object) -> bool:
        assert isinstance(__o, Column)
        return hash(self) == hash(__o)

    def __str__(self) -> str:
        return f"<{str(self.source)}:{str(self.column_idx)}>"


class Table:
    def __init__(
        self, name: str, schema: Dict[str, DataType], cardinality: int
    ) -> None:
        self.name = name
        self.column: List[Tuple[str, DataType]] = []
        self.column_name: Dict[str, int] = {}
        self.cardinality = cardinality
        for attribute in schema.items():
            self.column_name[attribute[0]] = len(self.column)
            self.column.append(attribute)

    def get(self, name: str) -> Column:
        return Column(self, self.column_name[name])

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.name


class Catalog:
    def __init__(self) -> None:
        self.table_dict: Dict[str, Table] = {}

    def create_table(
        self, name: str, schema: Dict[str, DataType], cardinality: int
    ) -> Table:
        table = Table(name, schema, cardinality)
        self.table_dict[name] = table
        return table
