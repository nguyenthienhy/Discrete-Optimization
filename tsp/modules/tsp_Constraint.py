import math
import random
from itertools import combinations
import gurobipy as gp
from gurobipy import GRB

def tsp_constraint(points):

    def subtourelim(model, where):
        if where == GRB.Callback.MIPSOL:

            # Chọn ra tập các cạnh trong solution hiện tại
            vals = model.cbGetSolution(model._vars)
            selected = gp.tuplelist((i, j) for i, j in model._vars.keys()
                                    if vals[i, j] > 0.5)
            
            # Tìm ra chu trình có trọng số nhỏ nhất dựa trên các tập cạnh đã được chọn
            tour = subtour(selected)

            # Nếu như chu trình này không đi qua n đỉnh
            if len(tour) < n:
                # thêm ràng buộc loai bỏ các subtour
                model.cbLazy(gp.quicksum(model._vars[i, j]
                                         for i, j in combinations(tour, 2))
                             <= len(tour) - 1)
    
    # Từ một tập các cạnh , tìm ra một subtour ngắn nhất
    def subtour(edges):
        unvisited = list(range(n))
        cycle = range(n + 1)
        while unvisited:
            thiscycle = []
            neighbors = unvisited
            while neighbors:
                current = neighbors[0]
                thiscycle.append(current)
                unvisited.remove(current)
                neighbors = [j for i, j in edges.select(current, '*')
                             if j in unvisited]
            if len(cycle) > len(thiscycle):
                cycle = thiscycle
        return cycle

    n = len(points) # số đỉnh

    # Tạo một tập từ điển với key là cặp giá trị các đỉnh được nối với nhau , values là tập giá trị khoảng cách
    dist = {(i, j):
                math.sqrt(sum((points[i][k] - points[j][k]) ** 2 for k in range(2)))
            for i in range(n) for j in range(i)}

    m = gp.Model() # khởi tạo mô hình

    # Tạo biến quyết định
    vars = m.addVars(dist.keys() , obj = dist, vtype=GRB.BINARY, name='e')

    for i, j in vars.keys():
        vars[j, i] = vars[i, j]

    m.addConstrs(vars.sum(i, '*') == 2 for i in range(n)) # mỗi đỉnh chỉ nối với 2 đỉnh

    m._vars = vars

    m.Params.lazyConstraints = 1

    m.optimize(subtourelim)

    vals = m.getAttr('x', vars)

    selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)

    tour = subtour(selected)

    return m.objVal, tour
