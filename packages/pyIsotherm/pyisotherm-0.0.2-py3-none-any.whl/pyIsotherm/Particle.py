import random

import numpy as np


class Particle:
    def __init__(self, param):
        self.position = np.array(
            [min_max[0] + random.random() * (min_max[1] - min_max[0]) for min_max in param])
        self.velocity = np.zeros_like(self.position)
        self.best_position = self.position.copy()
        self.best_fitness = float('inf')
        self.fitness = float('inf')

    def update_velocity(self, swarm_best_position):
        w = 0.8
        c1 = 1.2
        c2 = 1.2
        r1 = random.random()
        r2 = random.random()
        v = self.velocity
        best_position = self.best_position
        position = self.position
        self.velocity = w * v + c1 * r1 * (best_position - position) + c2 * r2 * (swarm_best_position - position)

    def update_position(self):
        self.position += self.velocity