
from collections import namedtuple
from modules.tsp_object import *
from modules.tsp_2_opt import *
from modules.tsp_Constraint import tsp_constraint
from modules.tsp_Christofides import tsp_christofides
import numpy as np
import math

Point = namedtuple("Point", ['x', 'y'])

def point_dist(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

def solve_it(input_data):
    lines = input_data.split('\n')
    nodeCount = int(lines[0])
    points = []
    for i in range(1, nodeCount + 1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))

    if nodeCount < 500:
        obj , solution = tsp_constraint(points)
    elif 500 <= nodeCount < 1000:
        solver = tsp_2_opt(points).solve()
        obj , solution = solver.obj , solver.cycle[:-1]
    elif 1000 <= nodeCount < 10000:
        count_run = 0
        saved = []
        optimal_obj = math.inf
        obj , solution = 0 , list(range(0 , nodeCount))
        while count_run <= 20:
            obj_t , solution_t = tsp_christofides(points)
            optimal_obj = min(optimal_obj , obj_t)
            saved.append([obj_t , solution_t])
            count_run += 1
        for save in saved:
            if save[0] == optimal_obj:
                obj = optimal_obj
                solution = save[1]
                break
    else:
        solver = tsp_object(points).greedy()
        obj , solution = solver.obj , solver.cycle[:-1]
    
    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

    print()

