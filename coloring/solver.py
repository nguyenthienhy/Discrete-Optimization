#!/usr/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
import random
import math
from psutil import cpu_count
from gurobipy import *

def solve_it(input_data):
    # Modify this code to run your optimization algorithm
    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))

    Adjs = createAdjs(node_count, edge_count, edges)

    Adjs_sorted = sort_degree_largest_first(Adjs)

    time_limit = 0

    if edge_count < 3000:
        time_limit = 15 * 60
        obj, opt, solution = mip(node_count, edges, Adjs_sorted,
                                 verbose=False,
                                 num_threads=3,
                                 time_limit=time_limit)
    else:
        obj, opt, solution = greedy(Adjs_sorted, list(range(node_count)), 1000)

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(opt) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


def mip(node_count, edges, Adjs_sorted, verbose=False, num_threads=None, time_limit=None):
    m = Model("graph_coloring")
    m.setParam('OutputFlag', verbose)
    if num_threads:
        m.setParam("Threads", num_threads)
    else:
        m.setParam("Threads", cpu_count())

    if time_limit:
        m.setParam("TimeLimit", time_limit)

    init_color_count, _, greedy_color = greedy(Adjs_sorted, list(range(node_count)), 1000)
    # sử dụng một thuật toán greedy để tìm ra cận trên cho số màu của đồ thị

    colors = m.addVars(init_color_count, vtype=GRB.BINARY, name="colors")  # biến quyết định số màu
    nodes = m.addVars(node_count, init_color_count, vtype=GRB.BINARY, name="assignments")  # biến quyết định đỉnh tương
    # ứng với màu nào đó
    # node[i][j] = 1 biểu thị đỉnh i được tô bằng màu j
    for i in range(init_color_count):
        colors[i].setAttr("Start", 0)
        for j in range(node_count):
            nodes[(j, i)].setAttr("Start", 0)

    for i, j in enumerate(greedy_color):  # i là số thứ tự đỉnh , j là số thứ tự màu mà i được tô
        colors[j].setAttr("Start", 1)
        nodes[(i, j)].setAttr("Start", 1)

    m.setObjective(quicksum(colors), GRB.MINIMIZE)  # hàm mục tiêu tối ưu sao số màu là nhỏ nhất

    # Mỗi đỉnh chỉ có một màu
    m.addConstrs((nodes.sum(i, "*") == 1 for i in range(node_count)), name="Chi co mot mau")

    m.addConstrs((nodes[(i, k)] - colors[k] <= 0 for i in range(node_count) for k in range(init_color_count)),
                 name="add constr")

    # Những đỉnh kề nhau sẽ có màu khác nhau
    m.addConstrs((nodes[(edge[0], k)] + nodes[(edge[1], k)] <= 1 for edge in edges for k in range(init_color_count)),
                 name="ke nhau")

    m.addConstrs((colors[i] - colors[i + 1] >= 0 for i in range(init_color_count - 1)), name="add constr 2")

    m.update()
    m.optimize()

    isol = [int(var.x) for var in m.getVars()]
    color_count = sum(isol[:init_color_count])
    solution = [j for i in range(node_count) for j in range(init_color_count)
            if isol[init_color_count + init_color_count * i + j] == 1]

    if m.status == 2:
        opt = 1
    else:
        opt = 0

    return color_count, opt, solution


def sort_degree_largest_first(Adjs):
    Adjs_sorted = {}
    Adjs = sorted(Adjs.items(), key=lambda kv: len(kv[1]))
    for item in Adjs:
        Adjs_sorted[item[0]] = item[1]
    return Adjs_sorted


def createAdjs(node_count, edge_count, edges):
    Adjs = {}
    for node in range(node_count):
        Adjs[node] = []
    for node in range(node_count):
        for edge in range(edge_count):
            if (edges[edge])[0] == node:
                Adjs[node].append((edges[edge])[1])
            elif (edges[edge])[1] == node:
                Adjs[node].append((edges[edge])[0])
    return Adjs


def first_available(color_list): # trả lại số màu nhỏ nhất chưa được tô
    color_set = set(color_list)
    count = 0
    while True:
        if count not in color_set:
            return count
        count += 1


def greedy(adjs, order, max_shuffle_count):
    shuffle_count = 0
    saved = {}
    color_drawed = None
    max_color = 999
    while shuffle_count <= max_shuffle_count:
        random.shuffle(order)
        color = dict() # key : đỉnh , values : màu
        for node in order:
            used_neighbour_colors = [color[nbr] for nbr in adjs[node]
                                     if nbr in color] # các màu đã được tô
            color[node] = first_available(used_neighbour_colors) # tô màu nhỏ nhất cho đỉnh hiện tại
        color_values = color.values()
        count_color = max(color_values)
        if count_color < max_color:
            max_color = count_color
            saved[max_color] = color_values
        shuffle_count += 1
    for entry in saved:
        if entry == max_color:
            color_drawed = saved[entry]
    return max_color + 1 , 0 , color_drawed


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print(
            'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')
