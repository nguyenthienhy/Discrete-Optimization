from gurobipy import *
import numpy as np

E = np.array([[0 , 2 , 1] , [0 , 4 , 2] ,
              [0 , 5 , 3] , [1 , 4 , 3] ,
              [1 , 5 , 5] , [2 , 3 , 2] ,
              [2 , 4 , 1] , [4 , 5 , 4]])

n_points = 6
n_edges = E.shape[0]

n_clusters = 3

model = Model("K Graph Partitioning")

e = model.addVars(n_points , n_points , vtype = GRB.BINARY , name = "e")
x = model.addVars(n_points , n_clusters , vtype = GRB.BINARY , name = "x")

model.addConstrs()

model.update()
model.optimize()

vars = model.getVars()

for i in range(len(vars)):
    print(vars[i].x)


