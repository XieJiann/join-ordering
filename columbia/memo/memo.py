from typing import Any, List, Optional
from columbia.memo.expr_group import Expr, Group
from columbia.rule import RuleSet
from columbia.task import Task
import utils.pptree as pptree


class Memo:
    def __init__(self) -> None:
        # root always in the front
        self.groups: List["Group"] = []
        self.expr_set: "set[Expr]" = set()

    def new_group(self) -> Group:
        group = Group(len(self.groups))
        self.groups.append(group)
        return group

    def record_plan(self, plan: Expr, target_group: Optional[Group]) -> Group:
        if plan in self.expr_set and plan.group != None:
            return plan.group
        # Make the first group is the root Group of this plan
        if target_group is None:
            target_group = self.new_group()

        group_children: List[Group] = []
        for child in plan.children:
            if not isinstance(child, Group):
                child = self.record_plan(child, None)
            assert child != None
            group_children.append(child)
        plan = plan.set_children(tuple(group_children))

        target_group.record_expr(plan)
        plan.set_group(target_group)
        self.expr_set.add(plan)
        return target_group

    def root(self) -> Group:
        return self.groups[0]

    def __str__(self) -> str:
        def serialize_tree(
            root: dict[str, Any] | str, parent: pptree.Node
        ) -> pptree.Node:
            if isinstance(root, str):
                return pptree.Node(root, parent)
            assert len(root.keys()) == 1
            root_key = list(root.keys())[0]
            root_node = pptree.Node(root_key, parent)
            for child in root[root_key]:
                serialize_tree(child, root_node)
            return root_node

        trees = self.root().all_trees()
        split_line = "\n\n\n**********************************************************************************************************"
        output = ""
        for tree in trees:
            output += pptree.print_tree(serialize_tree(tree, None)) + split_line  # type: ignore
        return output


class Context:
    def __init__(self, cost_upper_bound: "float", rule_set: RuleSet) -> None:
        # cost_upper_bound init with the bigest value, e.g., 1e10
        self.cost_upper_bound = cost_upper_bound
        self.task_stack: List[Task] = []
        self.rule_set = rule_set

    def push_task(self, task: Task) -> None:
        self.task_stack.append(task)

    def pop_task(self) -> Task:
        return self.task_stack.pop()

    def empty(self) -> bool:
        return len(self.task_stack) == 0
