from collections import namedtuple
from gurobipy import *
from recordclass import recordclass
from collections import deque
import heapq

Item = namedtuple("Item", ['index', 'value', 'weight', 'density'])
Node = namedtuple('Node', ['level' , 'value' ,  'weight' ,  'items'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm
    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        v, w = int(parts[0]), int(parts[1])
        items.append(Item(i-1, v, w, 1.0 * v / w))

    if item_count <= 200:
    	obj, opt, taken = dynamic_programming(capacity, items)
    elif 200 < item_count <= 1000:
    	obj , opt , taken = mip(capacity , items)
    else:
    	obj , opt , taken = branch_and_bound(capacity , items)

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(opt) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


def mip(capacity, items, verbose=False, num_threads=None):
    item_count = len(items)
    values = [item.value for item in items]
    weights = [item.weight for item in items]

    m = Model("knapsack")

    x = m.addVars(item_count, vtype=GRB.BINARY, name="items") # biến quyết định của bài toán

    m.setObjective(LinExpr(values, [x[i] for i in range(item_count)]), GRB.MAXIMIZE) # đối tượng cần tối ưu là tổng giá trị
    																				 # được biểu diễn bằng hàm LinExpr
    m.addConstr(LinExpr(weights, [x[i] for i in range(item_count)]), GRB.LESS_EQUAL, capacity, name="capacity")
    # thêm điều kiện ràng buộc số đồ vật lấy có tổng khối lượng không quá giá trị cho trước
    m.update() # sau khi thêm các ràng buộc thì phải cập nhật mô hình
    m.optimize()

    if m.status == 2:
        opt = 1
    else:
        opt = 0

    return int(m.objVal), opt, [int(var.x) for var in m.getVars()]

def dynamic_programming(capacity , items):
	item_count = len(items)
	T = [[0 for w in range(capacity + 1)] 
            for i in range(item_count + 1)]
    wt = [item.weight for item in items]
    val = [item.value for item in items]
    taken = [0 for i in range(item_count)] 
    for i in range(item_count + 1): 
        for w in range(capacity + 1): 
            if i == 0 or w == 0: 
                T[i][w] = 0
            elif wt[i - 1] <= w: 
                T[i][w] = max(val[i - 1]  
                  + T[i - 1][w - wt[i - 1]], 
                               T[i - 1][w]) 
            else: 
                T[i][w] = T[i - 1][w] 
    res = T[item_count][capacity] 
    obj = res 
    w = capacity 
    for i in range(n, 0, -1): 
        if res <= 0: 
            break
        if res == T[i - 1][w]: 
            continue
        else:  
            taken[i - 1] = 1 
            res = res - val[i - 1] 
            w = w - wt[i - 1]
    return obj , 1 , taken

def bound(u, capacity, item_count, items):
    if(u.weight >= capacity):
        return 0
    else:
        result = u.value
        j = u.level + 1
        totweight = u.weight

        while(j < item_count and totweight + items[j].weight <= capacity):
            totweight += items[j].weight
            result += items[j].value
            j = j + 1
        
        k = j
        if k <= item_count - 1:
            result = result + (capacity - totweight)*items[k].value / items[k].weight

    return result

 def branch_and_bound(capacity , items):
 	item_count = len(items)
 	items = sorted(items, key = lambda item: item.weight / item.value)

    v = Node(level = -1, value = 0, weight = 0, items = [])
    Q = deque([])
    Q.append(v)

    maxValue = 0
    bestItems = []

    while(len(Q) != 0):

        v = Q[0]
        Q.popleft()
        u = Node(level = None, weight = None, value = None, items = [])
        u.level = v.level + 1
        u.weight = v.weight + items[u.level].weight
        u.value = v.value + items[u.level].value
        u.items = list(v.items)
        u.items.append(items[u.level].index)

        if u.weight <= capacity and u.value > maxValue:
            maxValue = u.value
            bestItems = u.items
        
        bound_u = bound(u, capacity, item_count, items)

        if bound_u > maxValue:
            Q.append(u)
        
        u = Node(level = None, weight = None, value = None, items = [])
        u.level = v.level + 1
        u.weight = v.weight
        u.value = v.value
        u.items = list(v.items)

        bound_u = bound(u, capacity, item_count, items)
        if bound_u > maxValue:
            Q.append(u)
    
    taken = [0]*len(items)
    for i in range(len(bestItems)):
        taken[bestItems[i]] = 1
    
    return maxValue, 0 , taken

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

