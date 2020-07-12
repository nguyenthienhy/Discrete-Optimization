
import numpy as np

class Convert:
    def __init__(self, path):
        self.path = path

    def readData(self):
        f = open(self.path, 'r')
        input_data = f.read()

        lines = input_data.split('\n')

        firstLine = lines[0].split()
        N = int(firstLine[0])
        M = int(firstLine[1])

        cost = []
        S = {}
        for i in range(M):
            S[i] = []
        for i in range(1, M + 1):
            line = lines[i].split()
            cost.append(int(line[0]))
            for j in range(1, len(line)):
                S[i-1].append(int(line[j]))
        
        return N, M, cost, S
    
    def ExportData(self):
        N, M, cost, S = self.readData()
        A = []
        for i in range(N):
            tem = []
            for j in range(len(S)):
                if i in S[j]:
                    tem.append(1)
                else:
                    tem.append(0)
            A.append(tem)
        A = np.asarray(A)
        A = np.hstack((A, np.eye(len(A))*-1))
        b = []
        for i in range(N):
            b.append(1)
        b = np.asarray(b)
        c = []
        for i in range(M + N):
            if i < M:
                c.append(cost[i])
            else:
                c.append(0)
        c = np.asarray(c)
        return A, b, c