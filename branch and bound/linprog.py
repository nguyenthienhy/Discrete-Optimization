import numpy as np
import math
from fractions import Fraction

np.set_printoptions(suppress=True, formatter={'all': lambda x: str(Fraction(x).limit_denominator())})

class Simplex_method:

    # Khởi tạo các thông số cho không gian làm việc
    def __init__(self, coeff_optimial, a_constraint, base_values):
        self.a_constraint = a_constraint
        for i in range(self.a_constraint.shape[0]):
            for j in range(self.a_constraint.shape[1]):
                self.a_constraint[i][j] = Fraction(self.a_constraint[i][j])
        self.coeff_optimal = coeff_optimial
        for i in range(self.coeff_optimal.shape[0]):
            self.coeff_optimal[i] = Fraction(self.coeff_optimal[i])
        self.base_values = base_values
        for i in range(self.base_values.shape[0]):
            self.base_values[i] = Fraction(self.base_values[i])
        self.M_row = self.a_constraint.shape[0]
        self.N_col = self.a_constraint.shape[1]
        self.ObjectPhaseTwo = coeff_optimial
        self.total_valiables = self.N_col + self.M_row
        self.ObjectPhaseOne = np.zeros((1, self.total_valiables + 1))[0]
        for i in range(self.total_valiables + 1):
            self.ObjectPhaseOne[i] = Fraction(self.ObjectPhaseOne[i])
        self.basic_save = []
        self.origin_values = []

    # Tạo hàm mục tiêu ban đầu cho pha thứ nhất
    def caculateObjectPhaseOne(self):
        num_indexs = []
        for b in self.basic_save:
            for i, v in enumerate(self.origin_values):
                if b == v:
                    num_indexs.append(i)
        if len(num_indexs) != 0:
            for j in range(self.N_col):
                for i in range(self.a_constraint.shape[0] - 1):
                    for index in num_indexs:
                        if i == index:
                            self.ObjectPhaseOne[j] += self.a_constraint[i][j]
        else:
            for j in range(self.N_col):
                for i in range(self.a_constraint.shape[0] - 1):
                    self.ObjectPhaseOne[j] += self.a_constraint[i][j]
        for i in range(self.a_constraint.shape[0] - 1):
            self.ObjectPhaseOne[-1] += self.a_constraint[i][-1]

    # khởi tạo bảng làm việc
    def initWorkSpace(self):
        eyes = np.eye(self.M_row)  # tạo ma trận đơn vị
        for i in range(self.M_row):
            for j in range(self.M_row):
                eyes[i][j] = Fraction(eyes[i][j])
        self.a_constraint = np.concatenate((self.a_constraint, eyes), axis=1)
        self.a_constraint = np.concatenate((self.a_constraint, self.base_values.reshape(1, -1).T), axis=1)
        zeros = np.zeros((1, self.a_constraint.shape[1] - self.ObjectPhaseTwo.shape[0]))[0]
        for i in range(self.a_constraint.shape[1] - self.ObjectPhaseTwo.shape[0]):
            zeros[i] = Fraction(zeros[i])
        self.ObjectPhaseTwo = np.array([np.concatenate((self.ObjectPhaseTwo, zeros), axis=0)])
        self.a_constraint = np.concatenate((self.a_constraint, self.ObjectPhaseTwo), axis=0)
        for i in range(self.N_col, self.total_valiables):
            self.basic_save.append(Fraction(i))
        self.basic_save = np.asarray(self.basic_save)
        for i in range(self.N_col):
            self.origin_values.append(Fraction(i))
        self.origin_values = np.asarray(self.origin_values)
        self.caculateObjectPhaseOne()
        self.a_constraint = np.concatenate((self.a_constraint, np.array([self.ObjectPhaseOne])), axis=0)

    def findMaxNegativeIndexFollowRow(self):  # bài toán đối ngẫu , dual simplex
        max_index = -math.inf
        for i in range(self.a_constraint.shape[0] - 1):
            if self.a_constraint[i][-1] < 0:
                max_index = max(max_index, self.a_constraint[i][-1])
        for i in range(self.a_constraint.shape[0] - 1):
            if max_index == self.a_constraint[i][-1]:
                return i
        return -1

    def findMaxPositiveIndexFollowCol(self):
        max_index = -math.inf
        for i in range(self.a_constraint.shape[1] - 1):
            if self.a_constraint[-1][i] > 0:
                max_index = max(max_index, self.a_constraint[-1][i])
        for i in range(self.a_constraint.shape[1] - 1):
            if max_index == self.a_constraint[-1][i]:
                return i
        return -1

    def findRowToEliminateGauss(self, MaxPositiveIndex):
        minRow = math.inf
        for i in range(self.basic_save.shape[0]):
            if self.a_constraint[i][MaxPositiveIndex] > 0:
                minRow = min(minRow, self.a_constraint[i][-1] / self.a_constraint[i][MaxPositiveIndex])
        for i in range(self.basic_save.shape[0]):
            if self.a_constraint[i][MaxPositiveIndex] > 0:
                if minRow == self.a_constraint[i][-1] / self.a_constraint[i][MaxPositiveIndex]:
                    return i
        return -1

    def findColToEliminateGauss(self, MaxPositiveIndex):
        minRow = math.inf
        for i in range(self.a_constraint.shape[1] - 1):
            if self.a_constraint[MaxPositiveIndex][i] < 0:
                minRow = min(minRow, self.a_constraint[-1][i] / self.a_constraint[MaxPositiveIndex][i])
        for i in range(self.a_constraint.shape[1] - 1):
            if self.a_constraint[MaxPositiveIndex][i] < 0:
                if minRow == self.a_constraint[-1][i] / self.a_constraint[MaxPositiveIndex][i]:
                    return i
        return -1

    def pivot(self):
        max_index = self.findMaxPositiveIndexFollowCol()
        minRow = self.findRowToEliminateGauss(max_index)
        return minRow, max_index

    def dual_pivot(self):
        max_index = self.findMaxNegativeIndexFollowRow()
        minRow = self.findColToEliminateGauss(max_index)
        return max_index, minRow

    def eliminateGauss(self):
        while self.findMaxPositiveIndexFollowCol() != -1:
            p, q = self.pivot()
            if p == -1 or q == -1:
                break
            for i in range(self.a_constraint.shape[0]):
                for j in range(self.a_constraint.shape[1]):
                    if i != p and j != q:
                        self.a_constraint[i][j] -= self.a_constraint[p][j] * self.a_constraint[i][q] / \
                                                   self.a_constraint[p][q]
            for i in range(self.a_constraint.shape[0]):
                if i != p:
                    self.a_constraint[i][q] = Fraction(0)
            for j in range(self.a_constraint.shape[1]):
                if j != q:
                    self.a_constraint[p][j] /= self.a_constraint[p][q]
            self.a_constraint[p][q] = Fraction(1)
            self.basic_save[p] = q

    def eliminateGaussDual(self):
        while self.findMaxNegativeIndexFollowRow() != -1:
            p, q = self.dual_pivot()
            for i in range(self.a_constraint.shape[0]):
                for j in range(self.a_constraint.shape[1]):
                    if i != p and j != q:
                        self.a_constraint[i][j] -= self.a_constraint[p][j] * self.a_constraint[i][q] / \
                                                   self.a_constraint[p][q]
            for i in range(self.a_constraint.shape[0]):
                if i != p:
                    self.a_constraint[i][q] = Fraction(0)
            for j in range(self.a_constraint.shape[1]):
                if j != q:
                    self.a_constraint[p][j] /= self.a_constraint[p][q]

            self.a_constraint[p][q] = Fraction(1)
            self.basic_save[p] = q

    def solve_phase_two(self):
        self.a_constraint = np.delete(self.a_constraint, -1, 0)
        self.a_constraint = np.delete(self.a_constraint, list(range(self.N_col, self.a_constraint.shape[1] - 1)),axis=1)
        self.eliminateGauss()

    def add_gomory_cut(self, row):
        M, N = self.a_constraint.shape
        cur_row = self.a_constraint[row, :]
        gomory_constraint = [Fraction(math.floor(i) - i) if i not in self.basic_save else Fraction(0) for i in cur_row]
        new_varible = np.array([Fraction(0) for i in range(M + 1)]).reshape(1, M + 1)
        new_varible[:, -2] = Fraction(1)
        self.a_constraint = np.insert(self.a_constraint, M - 1, [gomory_constraint], axis=0)
        self.a_constraint = np.insert(self.a_constraint, N - 1, new_varible, axis=1)
        self.basic_save = np.concatenate((self.basic_save, np.array([self.a_constraint.shape[1] - 2])), axis=0)

    def find_row_has_Fraction(self):
        for i in range(self.a_constraint.shape[0] - 1):
            for j in range(self.a_constraint.shape[1]):
                if int(round(self.a_constraint[i][j] , 2)) - round(self.a_constraint[i][j] , 2) != 0:
                    return i
        return -1

    def solve_LP(self, force_print): # giải bài toán tuyến tính
        self.initWorkSpace()
        self.eliminateGauss()
        self.solve_phase_two()
        if force_print == "True":
            print("Result tablue : ")
            self.printWorkSpace()

    def solve_mix_integer(self, force_print="True"): # giải bài toán quy hoạch nguyên
        self.initWorkSpace()
        if force_print == "True":
            print("==========Begin Phase 1=========")
            print("Init tablue : ")
            self.printWorkSpace()
        self.eliminateGauss()
        if force_print == "True":
            print("Finish Phase 1")
            print("Result tablue : ")
            self.printWorkSpace()
        if force_print == "True":
            print("==========Begin Phase 2=========")
        self.solve_phase_two()
        if force_print == "True":
            print("Finish Phase 2")
            print("Result tablue : ")
            self.printWorkSpace()
        if force_print == "True":
            print("==========Add Gomory cut and dual_simplex=========")
        row_first_fraction = self.find_row_has_Fraction()
        self.add_gomory_cut(row_first_fraction)
        while self.find_row_has_Fraction() != -1:
            self.eliminateGaussDual()
            row_fraction = self.find_row_has_Fraction()
            self.add_gomory_cut(row_fraction)
        if force_print == "True":
            print("Finish Add Gomory Cut")
            print("Result tablue : ")
            self.printWorkSpace()
            print("Obj : " + str(-self.a_constraint[-1][-1]))
            print("Values : " + str(self.getValuesSolveMiP()))

    def printWorkSpace(self):
        print(self.a_constraint)

    def printBasicValues(self):
        print("Basic Values : ")
        for b in self.basic_save:
            print("X[" + str(b + 1) + "] ", end=" ")

    def printResLP(self):
        print("\nMax : " + str(-self.a_constraint[-1][-1]))

    def getResLP(self):
        return -self.a_constraint[-1][-1]

    def getValuesSolveLP(self):
        n_v = len(self.coeff_optimal)
        x = []
        a_temp = self.a_constraint
        a_temp = np.delete(a_temp, -1, 0)
        a_temp = np.delete(a_temp, -1, 0)
        for _ in range(n_v):
            x.append(0)
        for b in self.basic_save:
            if b < len(self.coeff_optimal):
                x[b] = round(a_temp[b - 1][-1] , 2)
        return x

    def getValuesSolveMiP(self):
        a_temp = self.a_constraint
        a_temp = np.delete(a_temp, -1, 0)
        a_temp = np.delete(a_temp, -1, 0)
        return a_temp[: , -1]

    def getStatusIntegerLP(self):
        x = self.getValuesSolveLP()
        for xx in x:
            if int(xx) - xx != 0:
                return 0  # còn nghiệm chưa nguyên
        return 1  # tất cả các nghiệm đều nguyên

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
    return constraint_num , num_values , np.asarray(a), np.asarray(b), np.asarray(c)

constraint_num , num_values , a , b , c = readInput()
app = Simplex_method(c , a , b)
app.solve_mix_integer("True")
