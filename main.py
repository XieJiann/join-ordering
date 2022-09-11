from columbia import optimizer as c_optimizer

# defile join graph by <nodes, edges>
# right now, we only support clique with inner join
tables = {
    "t1": 100,
    "t2": 200,
    "t3": 300
}

c_optimizer.optimize(tables, None)
