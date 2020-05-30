#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math
import numpy as np
from psutil import cpu_count
from collections import namedtuple
from gurobipy import *

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple(
    "Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])


def dist(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])

    facilities = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        facilities.append(Facility(
            i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3]))))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        customers.append(Customer(
            i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))

    if len(customers) == 2000:  # instance 8
        obj, opt, solution = trivial_solve(facilities, customers)
        output_data = '%.2f' % obj + ' ' + str(opt) + '\n'
        output_data += ' '.join(map(str, solution))
    else:
        if len(customers) < 100 or (len(customers) == 100 and len(facilities) == 100):  # instances 1,2,3
            time_limit = 180
        if len(customers) == 1000 and len(facilities) == 100:  # instance 4
            time_limit = 600
        elif len(customers) == 800 and len(facilities) == 200:  # instance 5
            time_limit = 600
        else:
            time_limit = 300

        obj, opt, solution = mip(facilities, customers,
                                    verbose=False,
                                    time_limit=time_limit)
        # prepare the solution in the specified output format
        output_data = '%.2f' % obj + ' ' + str(opt) + '\n'
        output_data += ' '.join(map(str, solution))

    return output_data


def trivial_solve(facilities, customers):
    solution = [-1]*len(customers)
    capacity_remaining = [f.capacity for f in facilities]

    facility_index = 0
    for customer in customers:
        if capacity_remaining[facility_index] >= customer.demand:
            solution[customer.index] = facility_index
            capacity_remaining[facility_index] -= customer.demand
        else:
            facility_index += 1
            assert capacity_remaining[facility_index] >= customer.demand
            solution[customer.index] = facility_index
            capacity_remaining[facility_index] -= customer.demand

    used = [0]*len(facilities)
    for facility_index in solution:
        used[facility_index] = 1

    # calculate the cost of the solution
    obj = sum([f.setup_cost*used[f.index] for f in facilities])
    for customer in customers:
        obj += dist(customer.location, facilities[solution[customer.index]].location)

    return obj , 0 , solution


def mip(facilities, customers, verbose=False, num_threads=None, time_limit=None):

    f_count = len(facilities)
    c_count = len(customers)

    m = Model("facility_location")
    m.setParam('OutputFlag', verbose)

    if num_threads:
        m.setParam("Threads", num_threads)
    else:
        m.setParam("Threads", cpu_count())

    if time_limit:
        m.setParam("TimeLimit", time_limit)

    a = m.addVars(f_count, vtype=GRB.BINARY, name="a") # a[j] lưu trữ số khách hàng được phục vụ bởi kho lưu trữ j
    c = m.addVars(c_count, f_count, vtype=GRB.BINARY, name="c") # c[(i , j)] biểu thị khách hàng i được phục vụ bởi kho lưu trữ

    m.setObjective(LinExpr((facilities[j].setup_cost, a[j]) for j in range(f_count)) +
                   LinExpr((dist(customers[i].location, facilities[j].location), c[(i, j)])
                           for i in range(c_count) for j in range(f_count)), GRB.MINIMIZE) # hàm mục tiêu

    m.addConstrs((c.sum(i, "*") == 1
                  for i in range(c_count)),
                 name="moi khach hang chi duoc phuc vu boi duy nhat mot kho luu tru")

    m.addConstrs((LinExpr((customers[i].demand, c[(i, j)])
                          for i in range(c_count)) <= facilities[j].capacity
                  for j in range(f_count)),
                 name="quan he rang buoc") # tổng chi phí yêu cầu các khách hàng liên kết 
    									   # với kho lưu trữ j không vượt quá khả năng lưu trữ của kho j

    m.update()
    m.optimize()

    total_cost = m.getObjective().getValue()
    solve = [[int(m.getVarByName("c[{},{}]".format(i, j)).x)
             for j in range(f_count)]
            for i in range(c_count)]
    solution = [j for i in range(c_count)
            for j in range(f_count) if solve[i][j] == 1]

    if m.status == 2:
        opt = 1
    else:
        opt = 0

    return total_cost, opt, solution


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')
