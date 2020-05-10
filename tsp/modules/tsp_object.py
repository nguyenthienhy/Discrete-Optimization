import math
import random
random.seed(2)

class tsp_object(object):

    def __init__(self , points):
        self.threshold = 10 ** -6
        self.points = points
        self.cycle = list(range(len(points)))
        random.shuffle(self.cycle)
        self.cycle = self.cycle + [self.cycle[0]]
        self.obj = self.cycle_length()

    def point_dist(self , p1 , p2):
        return math.sqrt((self.points[p1].x - self.points[p2].x) ** 2 + 
                        (self.points[p1].y - self.points[p2].y) ** 2)
    
    def cycle_length(self):
        return sum(self.point_dist(v1 , v2) 
                    for v1 , v2 in zip(self.cycle[:-1] , self.cycle[1:]))
    
    def greed(self):
        cycle = [self.cycle[0]]
        candidates = set(self.cycle[1 : -1])
        while candidates:
            current_point = cycle[-1]
            nearest_neighbor = None
            nearest_dist = math.inf
            for neighbor in candidates:
                neighbor_dist = self.point_dist(current_point , neighbor)
                if nearest_dist < nearest_dist:
                    nearest_neighbor = neighbor
                    nearest_dist = neighbor_dist
            cycle.append(nearest_neighbor)
            candidates.remove(nearest_neighbor)
        cycle.append(self.cycle[0])
        self.cycle = cycle
        self.obj = self.cycle_length()
        return self
    
        