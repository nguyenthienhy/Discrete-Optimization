#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import numpy as np
from collections import namedtuple
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import vehical_with_many_strategy

Customer = namedtuple("Customer", ['index', 'demand', 'x', 'y'])

def length(customer1, customer2):
    return math.sqrt((customer1.x - customer2.x)**2 + (customer1.y - customer2.y)**2)

def solve_it(input_data):
    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    customer_count = int(parts[0])
    vehicle_count = int(parts[1])
    vehicle_capacity = int(parts[2])
    
    customers = []
    for i in range(1, customer_count+1):
        line = lines[i]
        parts = line.split()
        customers.append(Customer(i-1, int(parts[0]), float(parts[1]), float(parts[2])))

    if customer_count <= 51:
        app = vehical_with_many_strategy.Vehical_Solver(customers , vehicle_count , vehicle_capacity)
        app.solve()
        outputData = app.returnOutPut()
    else:
        outputData = or_tool_solver_vehicle(customer_count , vehicle_count , vehicle_capacity , customers)

    return outputData

def or_tool_solver_vehicle(customer_count , vehicle_count , vehicle_capacity , customers):

    def get_solution(data, manager, routing, solution , vehicle_count):
        total_distance = 0
        customers_index = [[] for i in range(vehicle_count)]
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route_distance = 0
            while not routing.IsEnd(index):
                customers_index[vehicle_id].append(str(manager.IndexToNode(index)))
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            total_distance += route_distance
            customers_index[vehicle_id].append(str(manager.IndexToNode(index)))
        outputData = '%.2f' % total_distance + ' ' + str(0) + '\n'
        for v in range(0, vehicle_count):
            outputData += ' '.join(customers_index[v]) + '\n'
        return outputData
    
    def create_data_model(customer_count , vehicle_count , vehicle_capacity , customers):
        data = {}
        distance_matrix = np.zeros((customer_count , customer_count))
        for i in range(customer_count):
            for j in range(customer_count):
                distance_matrix[i][j] = length(customers[i] , customers[j])
        data['distance_matrix'] = distance_matrix
        data['demands'] = [customers[i].demand for i in range(customer_count)]
        data['vehicle_capacities'] = [vehicle_capacity for i in range(vehicle_count)]
        data['num_vehicles'] = vehicle_count
        data['depot'] = 0
        return data

    def main(customer_count , vehicle_count , vehicle_capacity , customers):
        data = create_data_model(customer_count , vehicle_count , vehicle_capacity , customers)
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                            data['num_vehicles'], data['depot'])
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]
        
        demand_callback_index = routing.RegisterUnaryTransitCallback(
            demand_callback)
        routing.AddDimensionWithVehicleCapacity(demand_callback_index,0,data['vehicle_capacities'],True,'Capacity')

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            return get_solution(data, manager, routing, solution , vehicle_count)

    return main(customer_count , vehicle_count , vehicle_capacity , customers)

import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/vrp_5_4_1)')

