
import math
import itertools
from time import time

class Vehical_Solver(object):
    def __init__(self, customers, vehicle_count, vehicle_capacity):
        self.THRESHOLD = 10 ** -6
        self.customers = customers
        self.n_customer = len(customers)
        self.n_vehical = vehicle_count
        self.vehical_cap = vehicle_capacity
        self.obj = 0
        self.tours = self.greedy_init_solution()
        return

    def dist(c1, c2):
        return math.sqrt((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2)

    def total_demand_of_tour(self, tour):
        return sum([self.customers[i].demand for i in tour])

    def dist_of_tour(self, tour):
        if not self.is_valid_tour(tour):
            return math.inf
        tour_dist = 0
        for i in range(1, len(tour)):
            tour_dist += self.dist(self.customers[tour[i - 1]], self.customers[tour[i]])
        return tour_dist

    def dist_of_tours(self):
        return [self.dist_of_tour(tour) for tour in self.tours]

    def total_tour_dist(self):
        dists = self.dist_of_tours()
        if math.inf in dists:
            None
        else:
            return sum(dists)

    def is_valid_tour(self, tour):
        """
        Một tour là thoả mã nếu như :
        1. tổng hàng của các khách trên một tour không vượt quá khả năng của xe
        2. bắt đầu và kết thúc tại điểm 0
        3. Các điểm trong tour ngoại trừ điểm xuất phát với điểm kết thúc đều phải khác 0
        """
        if (self.total_demand_of_tour(tour) <= self.vehical_cap) and \
            (tour[0] == 0) and (tour[-1] == 0) and \
            (0 not in tour[1:-1]) and \
            (len(set(tour[1:-1])) == len(tour[1:-1])):
            return True
        return False

    def is_valid_solution(self):
        return all([self.is_valid_tour(tour) for tour in self.tours])

    def greedy_init_solution(self):
        tours = []
        remaining_customers = set(self.customers[1:])
        for v in range(self.n_vehical):
            remaining_cap = self.vehical_cap
            tours.append([])
            tours[-1].append(0)
            while remaining_customers and remaining_cap > min([c.demand for c in remaining_customers]):
                for customer in sorted(remaining_customers, reverse=True, key=lambda c: c.demand):
                    if customer.demand <= remaining_cap:
                        tours[-1].append(customer.index)
                        remaining_cap -= customer.demand
                        remaining_customers.remove(customer)
            tours[-1].append(0)
        if remaining_customers:
            None
        else:
            self.tours = tours
            self.obj = self.total_tour_dist()
            return self.tours

    def One_point_move(self, i_from, start_from, end_from, i_to, j_to):
        tour_from_old = self.tours[i_from]
        tour_to_old = self.tours[i_to]
        improved = False

        seg_or = tour_from_old[start_from: end_from + 1]
        tour_from_new = tour_from_old[:start_from] + tour_from_old[end_from + 1:]
        tour_to_new_1 = tour_to_old[:j_to] + seg_or + tour_to_old[j_to:]
        tour_to_new_2 = tour_to_old[:j_to] + seg_or[::-1] + tour_to_old[j_to:]

        dist_from_old = self.dist_of_tour(tour_from_old)
        dist_to_old = self.dist_of_tour(tour_to_old)

        dist_from_new = self.dist_of_tour(tour_from_new)
        dist_to_new_1 = self.dist_of_tour(tour_to_new_1)
        dist_to_new_2 = self.dist_of_tour(tour_to_new_2)

        obj_new_1 = self.obj - \
                    (dist_from_old + dist_to_old) + \
                    (dist_from_new + dist_to_new_1)

        obj_new_2 = self.obj - \
                    (dist_from_old + dist_to_old) + \
                    (dist_from_new + dist_to_new_2)

        if obj_new_1 < self.obj - self.THRESHOLD:
            self.tours[i_from] = tour_from_new
            self.tours[i_to] = tour_to_new_1
            self.obj = self.total_tour_dist()
            improved = True

        if obj_new_2 < self.obj - self.THRESHOLD:
            self.tours[i_from] = tour_from_new
            self.tours[i_to] = tour_to_new_2
            self.obj = self.total_tour_dist()
            improved = True

        return improved

    def Two_opt_move(self, i_1, start_1, end_1, i_2, start_2, end_2):
        tour_1_old = self.tours[i_1]
        tour_2_old = self.tours[i_2]
        improved = False

        seg_1 = tour_1_old[start_1: end_1 + 1]
        seg_2 = tour_2_old[start_2: end_2 + 1]

        tour_1_new_1 = tour_1_old[: start_1] + seg_2 + tour_1_old[end_1 + 1:]

        tour_1_new_2 = tour_1_old[: start_1] + seg_2[::-1] + tour_1_old[end_1 + 1:]

        tour_2_new_1 = tour_2_old[: start_2] + seg_1 + tour_2_old[end_2 + 1:]

        tour_2_new_2 = tour_2_old[: start_2] + seg_1[::-1] + tour_2_old[end_2 + 1:]

        dist_1_old = self.dist_of_tour(tour_1_old)
        dist_2_old = self.dist_of_tour(tour_2_old)

        dist_1_new_1 = self.dist_of_tour(tour_1_new_1)
        dist_1_new_2 = self.dist_of_tour(tour_1_new_2)
        dist_2_new_1 = self.dist_of_tour(tour_2_new_1)
        dist_2_new_2 = self.dist_of_tour(tour_2_new_2)

        new_obj_1 = self.obj - (dist_1_old + dist_2_old) + (dist_1_new_1 + dist_2_new_1)
        new_obj_2 = self.obj - (dist_1_old + dist_2_old) + (dist_1_new_1 + dist_2_new_2)
        new_obj_3 = self.obj - (dist_1_old + dist_2_old) + (dist_1_new_2 + dist_2_new_1)
        new_obj_4 = self.obj - (dist_1_old + dist_2_old) + (dist_1_new_2 + dist_2_new_2)

        if new_obj_1 < self.obj - self.THRESHOLD:
            self.tours[i_1] = tour_1_new_1
            self.tours[i_2] = tour_2_new_1
            self.obj = self.total_tour_dist()
            improved = True

        if new_obj_2 < self.obj - self.THRESHOLD:
            self.tours[i_1] = tour_1_new_1
            self.tours[i_2] = tour_2_new_2
            self.obj = self.total_tour_dist()
            improved = True

        if new_obj_3 < self.obj - self.THRESHOLD:
            self.tours[i_1] = tour_1_new_2
            self.tours[i_2] = tour_2_new_1
            self.obj = self.total_tour_dist()
            improved = True

        if new_obj_4 < self.obj - self.THRESHOLD:
            self.tours[i_1] = tour_1_new_2
            self.tours[i_2] = tour_2_new_2
            self.obj = self.total_tour_dist()
            improved = True

        return improved

    def Cross_exchange(self, i, start, end, debug=False):
        improved = False
        tour_old = self.tours[i]
        seg = tour_old[start: end + 1]
        tour_new = tour_old[:start] + seg[::-1] + tour_old[end + 1:]

        new_obj = self.obj - self.dist_of_tour(tour_old) + self.dist_of_tour(tour_new)
        if new_obj < self.obj - self.THRESHOLD:
            self.tours[i] = tour_new
            self.obj = self.total_tour_dist()
            improved = True
        return improved

    def solve(self,Or_point_move=True,Two_opt_move=True,Cross_exchange=True,t_threshold=None):
        improved = True
        t_start = time()

        while improved:
            if t_threshold and time() - t_start >= t_threshold:
                break
            or_point = False
            two_point = False
            cross_point = False
            self.obj = self.total_tour_dist()
            prev_obj = self.obj

            if Or_point_move:
                for i_from, tour_from in enumerate(self.tours):
                    if or_point: break
                    for start_from, end_from in itertools.combinations(range(1, len(tour_from) - 1), 2):
                        if or_point: break
                        for i_to, tour_to in enumerate(self.tours):
                            if or_point: break
                            if i_from == i_to: continue
                            for j_to in range(1, len(tour_to) - 1):
                                if self.or(i_from, start_from, end_from, i_to, j_to):
                                    or_point = True
                                    break

            if Two_opt_move:
                for i_1, tour_1 in enumerate(self.tours):
                    if two_point: break
                    for start_1, end_1 in itertools.combinations(range(1, len(tour_1) - 1), 2):
                        if two_point: break
                        for i_2, tour_2 in enumerate(self.tours):
                            if two_point: break
                            if i_1 == i_2: continue
                            for start_2, end_2 in itertools.combinations(range(1, len(tour_2) - 1), 2):
                                if self.interchange(i_1, start_1, end_1, i_2, start_2, end_2):
                                    two_point = True
                                    break

            if Cross_exchange:
                for i, tour in enumerate(self.tours):
                    for start, end in itertools.combinations(range(1, len(tour) - 1), 2):
                        if self.exchange(i, start, end):
                            cross_point = True
                            break
            
            improved = or_point or two_point or cross_point

        return self.tours
    def returnOutPut(self):
        obj = self.total_tour_dist()
        opt = 0
        output_str = "{:.2f} {}\n".format(obj, opt)
        for tour in self.tours:
            output_str += (' '.join(map(str, [c for c in tour])) + '\n')
        return output_str
