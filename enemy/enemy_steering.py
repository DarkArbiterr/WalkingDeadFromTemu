import pygame
import random

class EnemySteering:
    def __init__(self, enemy):
        self.enemy = enemy

        # wagi zachowań
        self.weights = {
            "wall_avoidance": 10,
            "obstacle_avoidance": 10,
            "separation": 32000,
            "alignment": 200,
            "cohesion": 0.03,
            "wander": 3.5,
            "hide": 2
        }

        # prawdopodobieństwa wykonania zachowań
        self.probabilities = {
            "wall_avoidance": 0.9,
            "obstacle_avoidance": 0.9,
            "separation": 0.9,
            "alignment": 0.5,
            "cohesion": 0.1,
            "wander": 0.8,
            "hide": 0.9
        }


    def calculate_steering(self, dt, player=None, game_map=None):
        steering_force = pygame.Vector2(0, 0)

        # lista zachowań w kolejności priorytetu
        behaviors = ["hide",  "separation", "wall_avoidance", "obstacle_avoidance",
                     "alignment", "cohesion", "wander"]

        for behavior in behaviors:
            if random.random() <= self.probabilities[behavior]:
                force = getattr(self, behavior)(dt, player, game_map) * self.weights[behavior]
                if force.length_squared() > 0:
                    # ogranicz do max_force
                    if force.length() > self.enemy.max_force:
                        force.scale_to_length(self.enemy.max_force)
                    return force
        return steering_force

    def wall_avoidance(self, dt, player, game_map):
        return self.enemy.steering.wall_avoidance(game_map.walls)


    def obstacle_avoidance(self, dt, player, game_map):
        return self.enemy.steering.obstacle_avoidance(game_map.obstacles)


    def separation(self, dt, player, game_map):
        return self.enemy.steering.separation(self.enemy.neighbors)


    def alignment(self, dt, player, game_map):
        return self.enemy.steering.alignment()


    def cohesion(self, dt, player, game_map):
        return self.enemy.steering.cohesion(self.enemy.neighbors)


    def wander(self, dt, player, game_map):
        return self.enemy.steering.wander(dt)


    def hide(self, dt, player, game_map):
        if player is None:
            return pygame.Vector2(0, 0)
        return self.enemy.steering.hide(player, game_map.obstacles)