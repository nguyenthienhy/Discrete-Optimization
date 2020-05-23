import numpy as np
import math
from fractions import Fraction

np.set_printoptions(suppress=True, formatter={'all':lambda x: str(Fraction(x).limit_denominator())})

# ma trận ràng buộc biến
a_constraint = np.array([[1, 1, -1, 0, 0],
                         [2, -1, 0, -1, 0],
                         [0, 3, 0, 0, 1]])

# hệ số hàm mục tiêu
coeff_optimial = np.array([-6 , -3])
# giá trị cơ sở
base_values = np.array([1 , 1 , 2])

class Simplex_method:
    def __init__(self , a_constraint , coeff_optimial , base_values):
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
            for i , v in enumerate(self.origin_values):
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

    # tạo bảng làm việc
    def initWorkSpace(self):
        eyes = np.eye(self.M_row) # tạo ma trận đơn vị
        for i in range(self.M_row):
            for j in range(self.M_row):
                eyes[i][j] = Fraction(eyes[i][j])
        self.a_constraint = np.concatenate((self.a_constraint , eyes) , axis = 1)
        self.a_constraint = np.concatenate((self.a_constraint , self.base_values.reshape(1 , -1).T) , axis = 1)
        zeros = np.zeros((1 , self.a_constraint.shape[1] - self.ObjectPhaseTwo.shape[0]))[0]
        for i in range(self.a_constraint.shape[1] - self.ObjectPhaseTwo.shape[0]):
            zeros[i] = Fraction(zeros[i])
        self.ObjectPhaseTwo = np.array([np.concatenate((self.ObjectPhaseTwo , zeros) , axis = 0)])
        self.a_constraint = np.concatenate((self.a_constraint , self.ObjectPhaseTwo) , axis = 0)
        for i in range(self.N_col , self.total_valiables):
            self.basic_save.append(Fraction(i))
        self.basic_save = np.asarray(self.basic_save)
        for i in range(self.N_col):
            self.origin_values.append(Fraction(i))
        self.origin_values = np.asarray(self.origin_values)
        self.caculateObjectPhaseOne()
        self.a_constraint = np.concatenate((self.a_constraint , np.array([self.ObjectPhaseOne])) , axis = 0)

    def findMaxNegativeIndexFollowRow(self): # bài toán đối ngẫu , dual simplex
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
                max_index = max(max_index , self.a_constraint[-1][i])
        for i in range(self.a_constraint.shape[1] - 1):
            if max_index == self.a_constraint[-1][i]:
                return i
        return -1

    def findRowToEliminateGauss(self , MaxPositiveIndex):
        minRow = math.inf
        for i in range(self.basic_save.shape[0]):
            if self.a_constraint[i][MaxPositiveIndex] > 0:
                minRow = min(minRow , self.a_constraint[i][-1] / self.a_constraint[i][MaxPositiveIndex])
        for i in range(self.basic_save.shape[0]):
            if self.a_constraint[i][MaxPositiveIndex] > 0:
                if minRow == self.a_constraint[i][-1] / self.a_constraint[i][MaxPositiveIndex]:
                    return i
        return -1

    def findColToEliminateGauss(self , MaxPositiveIndex):
        minRow = math.inf
        for i in range(self.a_constraint.shape[1] - 1):
            if self.a_constraint[MaxPositiveIndex][i] < 0:
                minRow = min(minRow , self.a_constraint[-1][i] / self.a_constraint[MaxPositiveIndex][i])
        for i in range(self.a_constraint.shape[1] - 1):
            if self.a_constraint[MaxPositiveIndex][i] < 0:
                if minRow == self.a_constraint[-1][i] / self.a_constraint[MaxPositiveIndex][i]:
                    return i
        return -1

    def pivot(self):
        max_index = self.findMaxPositiveIndexFollowCol()
        minRow = self.findRowToEliminateGauss(max_index)
        return minRow , max_index

    def dual_pivot(self):
        max_index = self.findMaxNegativeIndexFollowRow()
        minRow = self.findColToEliminateGauss(max_index)
        return max_index , minRow

    def eliminateGauss(self):
        while self.findMaxPositiveIndexFollowCol() != -1:
            p , q = self.pivot()
            if p == -1 or q == -1:
                break
            for i in range(self.a_constraint.shape[0]):
                for j in range(self.a_constraint.shape[1]):
                    if i != p and j != q:
                        self.a_constraint[i][j] -= self.a_constraint[p][j] * self.a_constraint[i][q] / self.a_constraint[p][q]
            for i in range(self.a_constraint.shape[0]):
                if i != p:
                    self.a_constraint[i][q] = Fraction(0)
            for j in range(self.a_constraint.shape[1]):
                if j != q:
                    self.a_constraint[p][j] /= self.a_constraint[p][q]
            self.a_constraint[p][q] = Fraction(1)
            self.basic_save[p] = q
            self.get_pretty_print_tableau()

    def eliminateGaussDual(self):
        while self.findMaxNegativeIndexFollowRow() != -1:
            p , q = self.dual_pivot()
            for i in range(self.a_constraint.shape[0]):
                for j in range(self.a_constraint.shape[1]):
                    if i != p and j != q:
                        self.a_constraint[i][j] -= self.a_constraint[p][j] * self.a_constraint[i][q] / self.a_constraint[p][q]
            for i in range(self.a_constraint.shape[0]):
                if i != p:
                    self.a_constraint[i][q] = Fraction(0)
            for j in range(self.a_constraint.shape[1]):
                if j != q:
                    self.a_constraint[p][j] /= self.a_constraint[p][q]

            self.a_constraint[p][q] = Fraction(1)
            self.basic_save[p] = q


    def solve_phase_two(self):
        self.a_constraint = np.delete(self.a_constraint , -1 , 0)
        self.a_constraint = np.delete(self.a_constraint , list(range(self.N_col , self.a_constraint.shape[1] - 1)) , axis=1)
        self.eliminateGauss()

    def add_gomory_cut(self , row):
        M, N = self.a_constraint.shape
        cur_row = self.a_constraint[row , :]
        gomory_constraint = [Fraction(math.floor(i) - i) if i not in self.basic_save else Fraction(0) for i in cur_row]
        new_varible = np.array([Fraction(0) for i in range(M + 1)]).reshape(1, M + 1)
        new_varible[: , -2] = Fraction(1)
        self.a_constraint = np.insert(self.a_constraint, M - 1, [gomory_constraint], axis=0)
        self.a_constraint = np.insert(self.a_constraint, N - 1, new_varible, axis=1)
        self.basic_save = np.concatenate((self.basic_save , np.array([self.a_constraint.shape[1] - 2])) , axis=0)

    def has_Fraction(self): # kiểm tra xem còn có hệ số nào hữu tỉ hay là không
        count = 0
        for i in range(self.a_constraint.shape[0] - 1):
            for j in range(self.a_constraint.shape[1] - 1):
                if int(self.a_constraint[i][j]) - self.a_constraint[i][j] != 0:
                    count += 1
        if count > 0:
            return True
        else:
            return False

    def find_row_has_Fraction(self):
        for i in range(self.a_constraint.shape[0] - 1):
            for j in range(self.a_constraint.shape[1] - 1):
                if int(self.a_constraint[i][j]) - self.a_constraint[i][j] != 0:
                    return i
        return -1

    def solve_simplex(self):
        self.initWorkSpace()
        print("=============================Begin Phase 1==================================")
        self.eliminateGauss()
        print("=============================Begin Phase 2==================================")
        self.solve_phase_two()
        row = self.find_row_has_Fraction()
        self.add_gomory_cut(row)
        self.eliminateGaussDual()
        self.get_pretty_print_tableau()

    def get_pretty_print_tableau(self):
        a1 = self.a_constraint.copy()
        b1 = ['X' + str(x + 1) + '  |' for x in self.basic_save]
        b1 = np.append(b1, [' ' for i in range(a1.shape[0] - len(self.basic_save))])
        b1 = np.reshape(b1, (a1.shape[0], 1))
        a1 = np.append(b1, a1, axis=1)
        s = [[str(e) if type(e) is str or ((type(e) is Fraction or type(e) is int) and e < 0) else ' ' + str(e) for e in
              row] for row in a1]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        print('\n'.join(table))

app = Simplex_method(a_constraint , coeff_optimial , base_values)
app.solve_simplex()

