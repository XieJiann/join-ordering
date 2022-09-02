from cmath import exp
from lib2to3.pytree import Node
from rule import Rule
from pptree import *

class Expr:
    def __init__(self, type: str, children: list, name: str) -> None:
        self.children = children
        self.type = type
        self.name = name
        self.explored_rules = set()

    def set_explored(self, rule: Rule):
        self.explored_rules.add(rule)
    
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def __str__(self) -> str:
        return self.name

class Group:
    def __init__(self, expr_list: list, name: str, row_cnt: int) -> None:
        self.expr_list = expr_list
        self.name = name
        # the winner matain the idx of the expr with the lowest cost
        self.winner = -1
        self.row_cnt = row_cnt

        # We use all children to identify the group
        # for example: A Join B Join C, the root group is {A, B, C}
        self.table_set = set()

    # def get_table_set(self):
    #     if not self.table_set.empty():
    #         return hash(self.id)
    #     for expr in self.expr_list:
    #         if expr.is_leaf():
    #             # add leaf nodes
    #             self.table_set.add(expr.name)
    #         for group in expr.children:
    #             self.table_set.add(group.get_table_set())
    #     return self.table_set

    # def __hash__(self):
    #     if not self.table_set.empty():
    #         self.get_table_set()
    #     return hash(self.table_set)

    # def __eq__(self, __o) -> bool:
    #     return hash(self) == hash(__o)

    def all_trees(self):
        trees = []
        for expr in self.expr_list:
            if (expr.is_leaf()):
                trees.append(str(expr))
                continue
            children_trees = []
            for group in expr.children:
                children_trees.append(group.all_trees())
            for l_tree in children_trees[0]:
                for r_tree in children_trees[1]:
                    trees.append({str(expr): [l_tree, r_tree]})
        return trees

class Memo:
    def __init__(self) -> None:
        # root always in the front
        self.groups = []

    def add_group(self, group: Group):
        self.groups.append(group)
    
    def root(self) -> Group:
        return self.groups[0]
    
    def __str__(self) -> str:
        return str(self.root().all_trees())    
class Context:
    def __init__(self) -> None:
        pass