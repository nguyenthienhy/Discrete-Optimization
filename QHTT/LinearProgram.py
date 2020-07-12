import numpy as np
from fractions import Fraction

class simplex:

    def __init__(self, A, A_sub, b, c, c_sub):
        self.A = A
        self.A_sub = A_sub
        self.b = b
        self.c = c
        self.c_sub = c_sub    

    def createtable(self):
        size = list(self.A_sub.shape)
        cb = np.array(self.c_sub[size[1]-size[0]])
        B = np.array([size[1]-size[0]])

        for i in range(size[1]-size[0]+1,size[1]):
            cb = np.vstack((cb, self.c_sub[i]))
            B = np.vstack((B, i))
            xb = np.transpose([self.b])
        
        table = np.hstack((B, cb))
        table = np.hstack((table, xb))

        table = np.hstack((table, self.A_sub))

        table = np.array(table, dtype = 'float')

        return table

    def phrase1(self, table):

        size = list(self.A_sub.shape)

        reached = 0     
        itr = 1
        unbounded = 0
        alternate = 0
        
        while reached == 0: 
            for row in range(len(table)):
                for cell in range(len(table[0])):
                    if table[row][cell] < 1e-5:
                        table[row][cell] = round(table[row][cell], 5)
            i = 0
            rel_prof = [] 
            while i<(len(table[0])-3): 
                rel_prof.append(self.c_sub[i] - np.sum(table[:, 1]*table[:, 3 + i])) 
                i = i + 1 
            i = 0
            
            b_var = table[:, 0]
            while i<(len(table[0])-3): 
                j = 0
                present = 0
                while j<len(b_var): 
                    if int(b_var[j]) == i: 
                        present = 1
                        break; 
                    j+= 1
                if present == 0: 
                    if rel_prof[i] == 0: 
                        alternate = 1
                i+= 1

            flag = 0
            for profit in rel_prof: 
                if profit < 0: 
                    flag = 1
                    break 
            if flag == 0: 
                reached = 1
                break
           
            flash = False
            while not flash:
                k = rel_prof.index(min(rel_prof))
                minValue = 99999999
                i = 0; 
                r = -1 
                while i<len(table): 
                    if (table[:, 2][i] >= 0 and table[:, 3 + k][i]>0):  
                        val = table[:, 2][i]/table[:, 3 + k][i] 
                        if val<minValue: 
                            minValue = val 
                            r = i 
                    i+= 1
        
                if r ==-1: 
                    unbounded = 1 
                    rel_prof[k] = 10000
                
                    flash = True
                    for i in rel_prof:
                        if i < 0: 
                            flash = False
                else:
                    break  
            if r == -1:
                break 
        
            pivot = table[r][3 + k] 
            table[r, 2:len(table[0])] = table[ 
                    r, 2:len(table[0])] / pivot 

            i = 0
            while i<len(table): 
                if i != r: 
                    table[i, 2:len(table[0])] = table[i, 
                        2:len(table[0])] - table[i][3 + k] * \
                        table[r, 2:len(table[0])]
                i += 1
            
            table[r][0] = k 
            table[r][1] = self.c_sub[k] 
            
            itr+= 1 
    
        i = 0
        while i < len(table):
            if (table[i][0] >= (len(self.A[0]))):
                if table[i][2] != 0:
                    return None
                else:
                    table = np.delete(table, (i), axis = 0)
                    i -= 1
            i += 1 
        
        F = np.array([table[0]])
        i = 1
        while i < len(table):
            F = np.vstack((F, table[i]))
            i += 1
    
        for i in range(size[0]):
            a = len(F[0]) - 1     
            F = np.delete(F, (a), axis = 1)
   
        return F
    
    def phrase2(self, table):


        reached = 0     
        itr = 1
        unbounded = 0
        alternate = 0
        
        while ((reached == 0) & (itr < 4)): 
            
            for row in range(len(table)):
                for cell in range(len(table[0])):
                    if table[row][cell] < 1e-5:
                        table[row][cell] = round(table[row][cell], 5)
            i = 0
            rel_prof = []  
    
            while i<(len(table[0])-3): 
                rel_prof.append(self.c[i] - np.sum(table[:, 1]*table[:, 3 + i])) 
                i = i + 1

            i = 0
            
            b_var = table[:, 0] 
            while i<(len(table[0])-3): 
                j = 0
                present = 0
                while j<len(b_var): 
                    if int(b_var[j]) == i: 
                        present = 1
                        break; 
                    j+= 1
                if present == 0: 
                    if rel_prof[i] == 0: 
                        alternate = 1
                i+= 1

            flag = 0
            for profit in rel_prof: 
                if profit > 0: 
                    flag = 1
                    break 
            if flag == 0: 
                reached = 1
                break
     
            flash = False
            r = -1
            while not flash:
                k = rel_prof.index(max(rel_prof))
                maxValue = -99999999
                i = 0; 
                r = -1
                while i<len(table): 
                    if (table[:, 2][i]>= 0 and table[:, 3 + k][i] > 0):  
                        val = table[:, 2][i]/table[:, 3 + k][i] 
                        if val>maxValue: 
                            maxValue = val 
                            r = i 
                    i+= 1
        
                if r ==-1: 
                    unbounded = 1
                    rel_prof[k] = -10000
                
                    flash = True
                    for i in rel_prof:
                        if i > 0: 
                            flash = False
                else:
                    break   
        
            if r == -1:
                break
        
            pivot = table[r][3 + k] 

            table[r, 2:len(table[0])] = table[ 
                    r, 2:len(table[0])] / pivot  
            i = 0
            while i<len(table): 
                if i != r: 
                    table[i, 2:len(table[0])] = table[i, 
                        2:len(table[0])] - table[i][3 + k] * \
                        table[r, 2:len(table[0])]
                i += 1
        
            table[r][0] = k 
            table[r][1] = self.c[k] 

            itr+= 1
   
        return table

    def phrase2Min(self, table):


        reached = 0     
        itr = 1
        unbounded = 0
        alternate = 0
        
        while ((reached == 0) & (itr < 4)): 
            
            for row in range(len(table)):
                for cell in range(len(table[0])):
                    if table[row][cell] < 1e-5:
                        table[row][cell] = round(table[row][cell], 5)
            i = 0
            rel_prof = []
     
            while i<(len(table[0])-3): 
                rel_prof.append(self.c[i] - np.sum(table[:, 1]*table[:, 3 + i])) 
                i = i + 1

            i = 0
            
            b_var = table[:, 0]  
            while i<(len(table[0])-3): 
                j = 0
                present = 0
                while j<len(b_var): 
                    if int(b_var[j]) == i: 
                        present = 1
                        break; 
                    j+= 1
                if present == 0: 
                    if rel_prof[i] == 0: 
                        alternate = 1
                i+= 1
            flag = 0
            for profit in rel_prof: 
                if profit < 0: 
                    flag = 1
                    break 
            if flag == 0: 
                reached = 1
                break
            flash = False
            r = -1
            while not flash:
                k = rel_prof.index(min(rel_prof))
                minValue = 99999999999
                i = 0; 
                r = -1
                while i<len(table): 
                    if (table[:, 2][i]>= 0 and table[:, 3 + k][i] > 0):  
                        val = table[:, 2][i]/table[:, 3 + k][i] 
                        if val < minValue: 
                            minValue = val 
                            r = i 
                    i+= 1
     
                if r ==-1: 
                    unbounded = 1 
                    rel_prof[k] = -10000
                
                    flash = True
                    for i in rel_prof:
                        if i < 0: 
                            flash = False
                else:
                    break   
        
            if r == -1:
                break
        
            pivot = table[r][3 + k] 

            table[r, 2:len(table[0])] = table[ 
                    r, 2:len(table[0])] / pivot 
                    
            i = 0
            while i<len(table): 
                if i != r: 
                    table[i, 2:len(table[0])] = table[i, 
                        2:len(table[0])] - table[i][3 + k] * \
                        table[r, 2:len(table[0])]
                i += 1
        
            table[r][0] = k 
            table[r][1] = self.c[k] 
 
            itr+= 1
   
        return table