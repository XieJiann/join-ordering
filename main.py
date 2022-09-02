from ntpath import join
from tokenize import group
from base import *
from task import *

def construct_memo(join_tables):
    group_list = []
    for table, row_cnt in join_tables.items():
        table_expr = Expr("table", [], "table_expr_{}".format(table))
        table_group = Group([table_expr], "table_group_{}".format(table), row_cnt)
        group_list.append(table_group)
    root = group_list[0]
    table_size = len(group_list)
    for idx in range(1, table_size):
        print(root.row_cnt)
        join_expr = Expr("join", [root, group_list[idx]], "join_expr_{}".format(idx))
        join_group = Group([join_expr], "join_group_{}".format(idx), (root.row_cnt)*(group_list[idx].row_cnt))
        group_list.append(join_group)
        root = join_group
    
    memo = Memo()
    for group in group_list[::-1]:
        memo.add_group(group)
    return memo

def optimize(memo: Memo):
    task_stack = []
    task_stack.append(O_Group(memo.root()))
    context = Context()
    while not task_stack.empty():
        task  = task_stack.pop()
        task.execute(context, task_stack)

memo = construct_memo({"t1":100, "t2":10, "t3":50})
print(str(memo))
# optimize(memo)
