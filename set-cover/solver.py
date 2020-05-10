from collections import namedtuple
from psutil import cpu_count
from gurobipy import *

Set = namedtuple("Set", ['index', 'cost', 'items'])


def solve_it(input_data):
    # Modify this code to run your optimization algorithm
    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    item_count = int(parts[0])
    set_count = int(parts[1])

    sets = []
    for i in range(1, set_count+1):
        parts = lines[i].split()
        sets.append(Set(i-1, float(parts[0]), set(map(int, parts[1:]))))
    if set_count == 10000:
        obj, opt, solution = naive(item_count, sets)
        output_data = str(obj) + ' ' + str(opt) + '\n'
        output_data += ' '.join(map(str, solution))
    else:
        if set_count == 157:
            time_limit = 180
        elif set_count == 330:
            time_limit = 600
        elif set_count == 1000:
            time_limit = 600
        elif set_count == 5000:
            time_limit = 300
        obj, opt, solution = mip(item_count, sets, verbose=False, time_limit=3600)
        # prepare the solution in the specified output format
        output_data = str(obj) + ' ' + str(opt) + '\n'
        output_data += ' '.join(map(str, solution))

    return output_data

def naive(item_count, sets):
    sets = sorted(sets, key=lambda s: len(s.items), reverse=True)
    soln = [0] * len(sets)
    covered = set()
    for s in sets:
        soln[s.index] = 1
        covered |= set(s.items)
        if len(covered) >= item_count:
            break

    value = int(sum(map(lambda s: s.cost * soln[s.index], sets)))

    return value, 0, soln


def mip(item_count, sets, verbose=False, num_threads=None, time_limit=None):
    m = Model("set_covering")
    m.setParam('OutputFlag', verbose)
    if num_threads:
        m.setParam("Threads", num_threads)
    else:
        m.setParam("Threads", cpu_count())

    if time_limit:
        m.setParam("TimeLimit", time_limit)

    selections = m.addVars(len(sets), vtype=GRB.BINARY, name="set_selection")

    m.setObjective(LinExpr([s.cost for s in sets], [selections[i] for i in range(len(sets))]), GRB.MINIMIZE)

    m.addConstrs((LinExpr([1 if j in s.items else 0 for s in sets], [selections[i] for i in range(len(sets))]) >= 1
                  for j in range(item_count)),
                 name="ieq1")

    m.update()
    m.optimize()

    soln = [int(var.x) for var in m.getVars()]
    total_cost = int(sum([sets[i].cost * soln[i] for i in range(len(sets))]))

    if m.status == 2:
        opt = 1
    else:
        opt = 0

    return total_cost, opt, soln


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/sc_6_1)')

