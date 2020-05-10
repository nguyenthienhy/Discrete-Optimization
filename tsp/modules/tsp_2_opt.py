from modules.tsp_object import *
from itertools import combinations
import time
import random

class tsp_2_opt(tsp_object):
    
    def swap(self , start , end):
        improved = False
        new_cycle = self.cycle[:start] + self.cycle[start : end + 1][::-1] + self.cycle[end + 1:]
        new_obj = self.obj - \
                    (self.point_dist(self.cycle[start - 1] , self.cycle[start]) + self.point_dist(self.cycle[end] , self.cycle[end + 1])) + \
                    (self.point_dist(new_cycle[start - 1] , new_cycle[start]) + self.point_dist(new_cycle[end] , new_cycle[end + 1]))

        if new_obj < self.obj - self.threshold:
            self.cycle = new_cycle
            self.obj = new_obj
            improved = True
        
        return improved
    
    def solve(self , t_threshold = None):
        improved = True
        t = time.time()
        while improved:
            if t_threshold and time.time() - t >= t_threshold:
                break
            improved = False
            for start, end in combinations(range(1, len(self.cycle) - 1), 2):
                if self.swap(start, end):
                    improved = True
                    break
        return self
