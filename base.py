class Expr:
    def __init__(self, type: str, children: list, name: str) -> None:
        self.children = children
        self.type = type
        self.name = name

    def __hash__(self) -> int:
        name = self.name
        for child in self.children:
            name += child.name()
        return hash(name)

    def __eq__(self, __o) -> bool:
        if isinstance(__o, self.__class__):
            return hash(self) == hash(o)
        return False

class Group:
    def __init__(self, expr_list: list, name: str) -> None:
        self.expr_list = expr_list
        self.name = name
        # the winner matain the idx of the expr with the lowest cost
        self.winner = -1

class Memo:
    def __init__(self) -> None:
        # root always in the front
        self.groups = []
        self.expr_set = set()

    def add_group(self, group: Group):
        for expr in group.expr_list:
            self.expr_set.add(expr)
        self.groups.append(group)
    
    def root(self) -> Group:
        return self.groups[0]