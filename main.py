from base import *
from task import *

def construct_memo():
    #    Join1
    #   |    |
    # Join2  Join3
    # |   |  |   |
    # t1 t2  t3  t4
    memo = Memo()
    t1_expr = Expr("Get", [], "t1_expr")
    t2_expr = Expr("Get", [], "t2_expr")
    t3_expr = Expr("Get", [], "t3_expr")
    t4_expr = Expr("Get", [], "t4_expr")
    t1_group = Group([t1_expr], "t1_group")
    t2_group = Group([t2_expr], "t2_group")
    t3_group = Group([t3_expr], "t3_group")
    t4_group = Group([t4_expr], "t4_group")

    join2_expr = Expr("join", [t1_group, t2_group], "join2_expr")
    join3_expr = Expr("join", [t3_group, t4_group], "join3_expr")
    join2_group = Group([join2_expr], "join2_group")
    join3_group = Group([join3_expr], "join3_group")


    join1_expr = Expr("join", [join2_group, join3_group], "join1_expr")
    join1_group = Group([join1_expr], "join1_group")
    
    memo.add_group(join1_group)
    memo.add_group(join2_group)
    memo.add_group(join3_group)
    memo.add_group(t1_group)
    memo.add_group(t2_group)
    memo.add_group(t3_group)
    memo.add_group(t4_group)

def optimize(memo: Memo):
    task_stack = []
    task_stack.append(O_Group(memo.root()))
    while not task_stack.empty():
        task  = task_stack.pop()
        task.execute()

memo = construct_memo()
optimize(memo)
