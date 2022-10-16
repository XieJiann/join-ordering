from enum import Enum, auto
from typing import Tuple
from plan.expr import Expression


class PropertyType(Enum):
    Sort = auto()
    Group = auto()


class Property:
    def __init__(self, type: PropertyType, expressions: Tuple[Expression, ...]) -> None:
        self.type = type
        self.expressions = expressions

    def __hash__(self) -> int:
        return hash((self.type, self.expressions))

    def __eq__(self, __o: object) -> bool:
        assert isinstance(__o, Property)
        return hash(__o) == hash(self)

    def compat(self, prop: "Property"):
        # TODO: add automata
        return prop.type == self.type and prop.expressions == self.expressions

    def __str__(self) -> str:
        return str(self.type)


class PropertySet:
    def __init__(self) -> None:
        self.properties: set[Property] = set()

    def diff(self, prop_set: "PropertySet"):
        new_prop_set = PropertySet()
        new_prop_set.properties |= self.properties.difference(prop_set.properties)
        return new_prop_set

    def add_property(self, prop: Property):
        self.properties.add(prop)

    def pop_property(self):
        return self.properties.pop()

    def compat(self, request_prop: Property):
        for prop in self.properties:
            if prop.compat(request_prop):
                return True
        return False

    def add_property_set(self, prop_set: "PropertySet"):
        self.properties |= prop_set.properties
        return self

    def clone(self):
        cloned = PropertySet()
        cloned.properties = self.properties.copy()
        return cloned

    def empty(self):
        return len(self.properties) == 0

    def __hash__(self) -> int:
        return hash(tuple(self.properties))

    def __iter__(self):
        return self.properties.__iter__()

    def __str__(self) -> str:
        return "(" + ",".join(map(lambda p: str(p), tuple(self.properties))) + ")"

    def __eq__(self, __o: object) -> bool:
        assert isinstance(__o, PropertySet)
        return hash(__o) == hash(self)
