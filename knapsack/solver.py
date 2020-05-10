from collections import namedtuple
from psutil import cpu_count
from gurobipy import *

Item = namedtuple("Item", ['index', 'value', 'weight', 'density'])

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

    obj, opt, taken = mip(capacity, items)

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(opt) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


def mip(capacity, items, verbose=False, num_threads=None):
    item_count = len(items)
    values = [item.value for item in items]
    weights = [item.weight for item in items]

    m = Model("knapsack")

    # thiết lập các thông số của mô hình
    m.setParam('OutputFlag', verbose)
    if num_threads:
        m.setParam("Threads", num_threads)
    else:
        m.setParam("Threads", cpu_count())

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

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

