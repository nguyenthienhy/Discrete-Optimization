import numpy as np
import linprog_bb as bb
from scipy.optimize import linprog
import gurobipy as gp
from gurobipy import *

class Node:
    def __init__(self, x, res, bounds, status):
        self.x = x  # nghiệm bài toán hiện tại
        self.res = res  # kết quả tối ưu hàm hiện tại
        self.bounds = bounds  # các cận trên và cận dưới
        self.status = status  # trạng thái của node hiện tại

def isInteger(x):
    x_temp = np.array(x)
    count = 0
    for i in range(x_temp.shape[0]):
        if np.floor(x_temp[i]) - x_temp[i] == 0:
            count += 1
    if count == x_temp.shape[0]:
        return (True, None)
    else:
        minNotInteger = math.inf
        for i in range(x_temp.shape[0]):
            if int(x_temp[i]) - x_temp[i] != 0:
                minNotInteger = min(minNotInteger, x_temp[i])
        for i in range(x_temp.shape[0]):
            if minNotInteger == x_temp[i]:
                return (False, i)

def init(c, a, b):
    n = c.shape[0]
    bounds = [[0, None] for _ in range(n)]
    appSolver = linprog(c, a, b, None, None)
    x = appSolver.x
    x = round_x(x)
    res = appSolver.fun
    res = round(res, 3)
    status = appSolver.status
    print("Initial result : ")
    print("Values : " + str(x))
    print("Obj : " + str(res))
    node = Node(x, res, bounds, status)
    best_node_status = 0
    bestNode = Node([0, 0], 0, bounds, best_node_status)
    return node, bestNode

def round_x(x):
    new_x = []
    for xx in x:
        new_x.append(round(xx, 2))
    return np.array(new_x)

def hasNoneInteger(x):
    for i , xx in enumerate(x):
        if int(xx) - xx != 0:
            return i
    return -1

def hasCoverCut(num_values, z_constr, z_values, base):
    m = gp.Model("knapsack")
    # biến quyết định của bài toán
    x = m.addVars(num_values, vtype=GRB.BINARY, name="decision_values")
    m.setObjective(LinExpr(z_values, [x[i] for i in range(num_values)]), GRB.MINIMIZE)
    m.addConstr(LinExpr(z_constr, [x[i] for i in range(num_values)]), GRB.GREATER_EQUAL, base, name="capacity")
    m.update()
    m.optimize()
    if m.status == 3:
        return False
    return True

def getValues(num_values, z_constr, z_values, base):
    m = gp.Model("knapsack")
    # biến quyết định của bài toán
    x = m.addVars(num_values, vtype=GRB.BINARY, name="decision_values")
    m.setObjective(LinExpr(z_values, [x[i] for i in range(num_values)]), GRB.MINIMIZE)
    m.addConstr(LinExpr(z_constr, [x[i] for i in range(num_values)]), GRB.GREATER_EQUAL, base , name="capacity")
    m.update()
    m.optimize()
    return [int(var.x) for var in m.getVars()]

def isEqual(a , b):
    for i in range(a.shape[1]):
        if a[i] != b[i]:
            return False
    return True

def branch_and_cut(c , a , b , node , bestNode , num_values , num_constr):
    step = 0
    print("Iteration : " + str(step))
    if node.status != 0:
        bestNode.res = round(bestNode.res, 3)
        return bestNode
    # giá trị hàm mục tiêu hiện tại nhỏ hơn giá trị tốt nhất hiện có
    if node.res < bestNode.res:
        node.x = round_x(node.x)
        (isIntegerOrNot, indexSplit) = bb.isInteger(node.x)
        # nếu như tất cả các biến đều nguyên
        if isIntegerOrNot == True:
            bestNode = node
            bestNode.res = round(bestNode.res, 3)
            return bestNode
        else:
            c_new , a_new , b_new , num_values_new , num_constr_new = get_cut_and_constraints(node.x , c , a , b , num_values , num_constr)
            if isEqual(c , c_new) and isEqual(a , a_new) and isEqual(b , b_new): # không tìm được cut
                value_to_split = node.x[indexSplit]
                lowbound = np.floor(value_to_split)
                bounds_temp_L = np.array(node.bounds)
                bounds_temp_L[indexSplit] = [0, lowbound]
                resLeftChild = linprog(c, a, b, None, None, bounds_temp_L)
                resLeftChild.x = round_x(resLeftChild.x)
                nodeLeftChild = bb.Node(resLeftChild.x, resLeftChild.fun, bounds_temp_L, resLeftChild.status)
                if nodeLeftChild.res <= bestNode.res:
                    bestNode = branch_and_cut(c, a, b, nodeLeftChild, bestNode , num_values , num_constr)
                else:
                    upbound = np.ceil(value_to_split)
                    bounds_temp_R = np.array(node.bounds)
                    bounds_temp_R[indexSplit] = [upbound, None]
                    resRightChild = linprog(c, a, b, None, None, bounds_temp_R)
                    resRightChild.x = round_x(resRightChild.x)
                    nodeRightChild = bb.Node(resRightChild.x, resRightChild.fun, bounds_temp_R, resRightChild.status)
                    if nodeRightChild.res <= bestNode.res:
                        bestNode = branch_and_cut(c, a, b, nodeLeftChild, bestNode , num_values , num_constr)
            else: # nếu như tìm được cut thì quay lại bước 1
                step += 1
                bestNode.res = linprog(c_new , a_new , b_new , None, None).fun
                bestNode = branch_and_cut(c_new , a_new , b_new , node , bestNode , num_values_new , num_constr_new)
    else:
        bestNode.res = round(bestNode.res, 3)
        return bestNode
    bestNode.res = round(bestNode.res, 3)
    return bestNode

def get_cut_and_constraints(x , c , a , b , num_values , num_constr):
    count = 0
    for index in range(num_constr):
        z_constr = np.concatenate((a[index] , [-1]) , axis = 0)
        z_values = np.concatenate((1 - x , [0]) , axis = 0)
        base = b[index]
        if hasCoverCut(num_values + 1 , z_constr , z_values , base): # nếu như tìm được cover cut
            print("Has cover cut at constraint : " + str(index) + ", Continue Phase 2......")
            x_temp = getValues(num_values + 1 , z_constr , z_values , base)
            x_temp = np.asarray(x_temp)
            x_minus = x_temp - x
            if np.sum(x_minus) < 1: # tìm được lát cắt hợp lệ
                b = np.concatenate((b, [np.sum(x_temp) - 1 + x_temp[-1]]) , axis = 0)
                x_temp = np.delete(x_temp , -1 , axis = 0)
                a = np.concatenate((a , [x_temp]) , axis = 0)
                num_constr_new = num_constr + 1
                num_values_new = num_values + 1
                return c , a , b , num_values_new , num_constr_new
        else:
            count += 1
    if count == num_constr: # không tìm được cover cut
        return c , a , b , num_values , num_constr

num_constr , num_values , a , b , c = bb.readInput()
node, bestNode = init(c, a, b)
bestNode = branch_and_cut(c , a , b , node , bestNode , num_values , num_constr)
print("Obj : " + str(bestNode.res))
print("X : " + str(bestNode.x))






