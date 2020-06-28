import numpy as np
from scipy.optimize import linprog
import math

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
    print()
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
    return new_x


def branch_and_bound(c , a , b , node, bestNode):
    print("Current values : " + str(node.x))
    if node.status != 0:
        bestNode.res = round(bestNode.res, 3)
        return bestNode
    # giá trị hàm mục tiêu hiện tại nhỏ hơn giá trị tốt nhất hiện có
    if node.res < bestNode.res:
        node.x = round_x(node.x)
        (isIntegerOrNot, indexSplit) = isInteger(node.x)
        # nếu như tất cả các biến đều nguyên
        if isIntegerOrNot == True:
            bestNode = node
            bestNode.res = round(bestNode.res, 3)
            return bestNode
        else:
            value_to_split = node.x[indexSplit]
            lowbound = np.floor(value_to_split)
            bounds_temp_L = np.array(node.bounds)
            bounds_temp_L[indexSplit] = [0, lowbound]
            print("Split at : " + "x[" + str(indexSplit) + "]" + " = " + str(value_to_split))
            resLeftChild = linprog(c, a, b, None, None, bounds_temp_L)
            resLeftChild.x = round_x(resLeftChild.x)
            nodeLeftChild = Node(resLeftChild.x, resLeftChild.fun, bounds_temp_L, resLeftChild.status)
            print("Obj : " + str(round(nodeLeftChild.res, 3)))
            if nodeLeftChild.res <= bestNode.res:
                bestNode = branch_and_bound(c , a , b , nodeLeftChild, bestNode)
            else:
                upbound = np.ceil(value_to_split)
                bounds_temp_R = np.array(node.bounds)
                bounds_temp_R[indexSplit] = [upbound, None]
                print("Split at : " + "x[" + str(indexSplit) + "]" + " = " + str(value_to_split))
                resRightChild = linprog(c, a, b, None, None, bounds_temp_R)
                resRightChild.x = round_x(resRightChild.x)
                nodeRightChild = Node(resRightChild.x, resRightChild.fun, bounds_temp_R, resRightChild.status)
                print("Obj : " + str(round(nodeRightChild.res, 3)))
                if nodeRightChild.res <= bestNode.res:
                    bestNode = branch_and_bound(c , a , b , nodeRightChild, bestNode)
    else:
        bestNode.res = round(bestNode.res, 3)
        return bestNode
    bestNode.res = round(bestNode.res, 3)
    return bestNode


def readInput():
    print("Input file name : ")
    fileName = input()
    f = open(fileName, 'r' , encoding="utf-8")
    constraint_num = int(f.readline())
    c = [float(ci) for ci in f.readline().split()]
    num_values = len(c)
    a = []
    for i in range(constraint_num):
        a.append([float(aij) for aij in f.readline().split()])
    b = [float(bi) for bi in f.readline().split()]
    return constraint_num , num_values , np.asarray(a), np.asarray(b), -np.asarray(c)

def solve_branch_and_bound(c , a , b):
    node, bestNode = init(c, a, b)
    print()
    print("===========Starting branch and bound==========")
    bestNode = branch_and_bound(c , a , b , node, bestNode)
    print()
    print("===========Result=========")
    print("X : " + str(bestNode.x))
    print("Obj : " + str(-bestNode.res))
    return bestNode.x

constraint_num , num_values , a , b , c = readInput()
solve_branch_and_bound(c , a , b)
