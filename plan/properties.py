from enum import Enum, auto
from typing import Tuple
from plan.expr import Expression


class PropertyType(Enum):
    # Mpp
    Gather = auto()
    Replica = auto()
    Redistribute = auto()

    # SingleTon
    ASCSort = auto()
    DESCSort = auto()


class Property:
    def __init__(self, type: PropertyType, expressions: Tuple[Expression, ...]) -> None:
        self.type = type
        self.expressions = expressions

    def __hash__(self) -> int:
        return hash((self.type, self.expressions))


class PropertySet:
    def __init__(self) -> None:
        self.properties: set[Property] = set()

    def add_property(self, prop: Property):
        self.properties.add(prop)

    def __hash__(self) -> int:
        return hash(tuple(self.properties))


def make_replica():
    p = PropertySet()
    p.add_property(Property(PropertyType.Replica, ()))
    return p


def make_redistibute(exprs: Tuple[Expression, ...]):
    p = PropertySet()
    p.add_property(Property(PropertyType.Replica, exprs))
    return p
