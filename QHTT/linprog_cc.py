from LinearProgram import simplex
import numpy as np
from ConvertData import Convert
from fractions import Fraction
from ortools.algorithms import pywrapknapsack_solver
import collections

class BranchAndBound:
    
    def solve1(self, A, A_sub, b, c, c_sub):
        sim = simplex(A, A_sub, b, c, c_sub)
        table = sim.createtable()
        table = sim.phrase1(table)
        if table is None:
            print("No solution Phrase 1")
            return None, None, None
        for i in range(len(table)):
            table[i][1] = c[int(table[i][0])]
        print("Phase 2:")
        table = sim.phrase2(table)
        if table is None:
            print("No solution Phrase 2")
            return None, None, None
        obj = np.sum(table[:, 1]*table[:, 2])
        print("Obj = ", Fraction(obj).limit_denominator(100))
        result = np.zeros((len(table)))
        for i in range (len(table)):
            result[i] = table[i][2]
        if table is None:
            print("None")
        else:
            for i in range (len(result)):
                print("X[" + str(int(i)), "] = ", Fraction(result[i]).limit_denominator(100) , end = ", ")
            for i in range(len(table)):
                for j in range (1, len(table[i])):
                    table[i][j] = Fraction(table[i][j]).limit_denominator(100)

        return result, table, obj
    def solve2(self, A, A_sub, b, c, c_sub):
        sim = simplex(A, A_sub, b, c, c_sub)
        table = sim.createtable()
        table = sim.phrase1(table)
        if table is None:
            print("No solution Phrase 1")
            return None, None, None
        for i in range(len(table)):
            table[i][1] = c[int(table[i][0])]

        table = sim.phrase2Min(table)
        if table is None:
            print("No solution Phrase 2")
            return None, None, None

        obj = np.sum(table[:, 1]*table[:, 2])
        print("Obj = ", Fraction(obj).limit_denominator(100))
        result = np.zeros((len(table)))
        for i in range (len(table)):
            result[i] = table[i][2]
        if table is None:
            print("None")
        else:
            for i in range (len(result)):
                print("X[" + str(int(i)), "] = ", Fraction(result[i]).limit_denominator(100) , end = ", ")
            for i in range(len(table)):
                for j in range (1, len(table[i])):
                    table[i][j] = Fraction(table[i][j]).limit_denominator(100)
        return result, table, obj

def isInteger(fraction):
    if (fraction.denominator == 1):
        return True
    else:
        return False

def convert_f(fraction):
    numerator = fraction.numerator
    denominator = fraction.denominator
    return Fraction(numerator%denominator, denominator)

def branchandcut(A, b, c):
    A_sub = np.hstack((A, np.eye(len(A))))
    
    c_sub = np.zeros((len(c)+len(A)))
    for i in range(len(c), len(c) + len(A)):
       c_sub[i] = 1

    sol = BranchAndBound()
    flash = False
    stop = False
    step  = 0
    print("=================Starting solving phase 2===============")
    result, table, obj = sol.solve2(A, A_sub, b, c, c_sub)
    if table is None:
        print("No solution Two Phrase")
        exit()
    print()
    print("Result after phase 2 : " + str(obj))
    print("Tablue : ")
    print(table)
    print()
    print("=================Starting branch and cut================")
    while not flash:
        print()
        print("Iteration : " + str(step))
        step += 1
        flash = True
        list_val = []   
        for i in range(len(result)):
            if (not isInteger(Fraction(result[i]).limit_denominator(100))):
                flash = False
                list_val.append(convert_f(Fraction(result[i]).limit_denominator(100)))
            else:
                list_val.append(0)
        stop = True
        for i in list_val:
            if i > 0:
                stop = False
        if stop:
            obj = np.sum(table[:, 1]*table[:, 2])
            for i in range(len(result)):
                print("X[" + str(int(table[i, 0])) , "] = " , Fraction(result[i]).limit_denominator(100) , end = ", ")
            print("Obj = ", obj)
            result = np.zeros((len(table)))
            for i in range (len(table)):
                result[i] = table[i][2]
            break
        X = {}
        for i in range(len(A)):
            X[i] = 0
        for i in range(len(table)):
            X[table[i, 0]] = 1 - table[i, 2]

        values = []
        for i in X.keys():
            values.append(-X[i])
        flash_opt = False

        for i in range(len(A)):
            solver = pywrapknapsack_solver.KnapsackSolver(
                pywrapknapsack_solver.KnapsackSolver.
                KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'KnapsackExample')

            weights = []
            tem = []
            for j in range(len(A[0])):
                tem.append(-A[i][j])
            weights.append(tem)
            capacites = [-b[i]]

            solver.Init(values, weights, capacites)
            computed_value = solver.Solve()
            x_idx = []
            for k in range(len(values)):
                if solver.BestSolutionContains(k):
                    x_idx.append(k)
                    flash_opt = True
            
            if flash_opt:
                print("Has cover cut at constraint : " + str(i) + ", Continue Phase 2.....")
                break

        if flash_opt:
            A_cut = np.copy(A)
            b_cut = np.copy(b)
            c_cut = np.copy(c)
            constraint = []
            sum = 0
            for i in range(len(A_cut[0])):
                if i in x_idx:
                    constraint.append(1)
                    sum += 1
                else:
                    constraint.append(0)  
            constraint.append(1)
            a_coff = []
            for i in range(len(A_cut)):
                a_coff.append([0])
            A_cut = np.hstack((A_cut, a_coff))
            A_cut = np.vstack((A_cut, constraint))
            b_cut = np.hstack((b_cut, np.array(sum - 1)))
            c_cut = np.hstack((c_cut, 0))
            
            A_sub = np.hstack((A_cut, np.eye(len(A_cut))))
            
            c_sub = np.zeros((len(c_cut)+len(A_cut)))
            for i in range(len(c_cut), len(c_cut) + len(A_cut)):
                c_sub[i] = 1
            result_cut, table_cut, obj_cut = sol.solve2(A_cut, A_sub, b_cut, c_cut, c_sub)
        
        if table_cut is None:
            index = list_val.index(max(list_val))
            value = result[index]
            value_up = int(result[index]) + 1
            value_low = int(result[index])
            obj_up_global = np.sum(table[:, 1]*table[:, 2])
            table_old = []
            for i in table[:, 2]:
                table_old.append(i)
            
            for i in range(len(table)):
                if list_val[i] != 0:
                    table[i, 2] = int(result[i])
            obj_low_golbal = np.sum(table[:, 1]*table[:, 2])
            for i in range(len(table)):
                table[i, 2] = table_old[i]

            
            A1 = np.copy(A)
            A2 = np.copy(A)
            c1 = np.copy(c)
            c2 = np.copy(c)
            b1 = np.copy(b)
            b2 = np.copy(b)

            temA1 = []
            a1 = []
            for i in range(len(A1)):
                a1.append([0])
            A1 = np.hstack((A1, a1))
            idx_A1 = table[index, 0]
            for i in range(len(A1[0]) - 1):
                if i == idx_A1:
                    temA1.append(1)
                else:
                    temA1.append(0)
            temA1.append(-1)  
            A1 = np.vstack((A1, temA1))
            b1 = np.hstack((b1, np.array(value_up)))
            A_sub = np.hstack((A1, np.eye(len(A1))))
            c1 = np.hstack((c1, np.array(0)))
            c_sub = np.zeros((len(c1)+len(A1)))
            for i in range(len(c1), len(c1) + len(A1)):
                c_sub[i] = 1
            result1, table1, obj1 = sol.solve2(A1, A_sub, b1, c1, c_sub)
            if table1 is None:
                print("No solution fesible")
            else:
                for row in table1: 
                    for el in row: 
                        print(Fraction(str(el)).limit_denominator(100), end ='\t') 
                    print()
            temA2 = []
            a2 = []
            for i in range(len(A2)):
                a2.append([0])
            A2 = np.hstack((A2, a2))

            idx_A2 = table[index, 0]
            for i in range(len(A2[0]) - 1):
                if i == idx_A2:
                    temA2.append(1)
                else:
                    temA2.append(0)
            temA2.append(1)  
            A2 = np.vstack((A2, temA2))
            b2 = np.hstack((b2, np.array(value_low)))
            A_sub = np.hstack((A2, np.eye(len(A2))))
            c2 = np.hstack((c2, np.array(0)))
            c_sub = np.zeros((len(c2)+len(A2)))
            for i in range(len(c2), len(c2) + len(A2)):
                c_sub[i] = 1
            result2, table2, obj2 = sol.solve2(A2, A_sub, b2, c2, c_sub)
            if table2 is None:
                print("No solution Fesible")
            else:
                for row in table2: 
                    for el in row: 
                        print(Fraction(str(el)).limit_denominator(100), end ='\t') 
                    print()
            if ((obj1 is None) and (obj2 is None)):
                print("No solution of problem")
                exit()
            if obj1 is None:
                A = np.copy(A2)
                b = np.copy(b2)
                c = np.copy(c2)
                table = np.copy(table2)
                result = np.copy(result2)
                del A1, b1, c1, A2, b2, c2
            elif obj2 is None:
                A = np.copy(A1)
                b = np.copy(b1)
                c = np.copy(c1)
                table = np.copy(table1)
                result = np.copy(result1)
                del A1, b1, c1, A2, b2, c2
            elif obj1 > obj2:
                A = np.copy(A1)
                b = np.copy(b1)
                c = np.copy(c1)
                table = np.copy(table1)
                result = np.copy(result1)
                del A1, b1, c1, A2, b2, c2
            else:
                A = np.copy(A2)
                b = np.copy(b2)
                c = np.copy(c2)
                table = np.copy(table2)
                result = np.copy(result2)
                del A1, b1, c1, A2, b2, c2
        else:
            A = np.copy(A_cut)
            b = np.copy(b_cut)
            c = np.copy(c_cut)
            table = np.copy(table_cut)
            result = np.copy(result_cut)
            del A_cut, b_cut, c_cut, table_cut, result_cut

def readInput():
    print("Input file name : ")
    fileName = input()
    converts = Convert(fileName)
    A, b, c = converts.ExportData()
    branchandcut(A, b, c)
    
readInput()
