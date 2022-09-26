from enum import Enum, auto


class PropertyType(Enum):
    Sort = auto()
    Group = auto()


class PropertySet:
    def __init__(self) -> None:
        return

    def is_empty(self) -> bool:
        return True
