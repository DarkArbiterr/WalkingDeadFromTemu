import pygame
import random
from .enemy_peek import EnemyPeek

class EnemySteering:
    def __init__(self, enemy):
        self.enemy = enemy

        # wagi zachowań dla trybu eksploracji
        self.explore_weights = {
            "wall_avoidance": 10,
            "obstacle_avoidance": 10,
            "separation": 22000,
            "alignment": 400,
            "cohesion": 0.03,
            "wander": 3.5,
            "hide": 12
        }

        # wagi zachowań dla trybu ataku
        self.attack_weights = {
            "wall_avoidance": 50,
            "obstacle_avoidance": 65,
            "separation": 4000,
            "alignment": 300,
            "cohesion": 0.1,
            "offset_pursuit": 100,
            "pursuit": 60
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
        self.enemy.peek.update(dt)

        if self.enemy.state == "attack":
            # leader jest przechowywany w group managerze
            leader = getattr(self.enemy.group, "group_leader", None)
            if leader is None:
                # fallback - brak lidera
                return self.exploration_mode(dt, player, game_map)
            return self.attack_mode(dt, leader, player, game_map)
        else:
            return self.exploration_mode(dt, player, game_map)

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

    def pursuit(self, dt, player, game_map):
        return self.enemy.steering.pursuit(player)

    def offset_pursuit(self, dt, leader, game_map):
        if not hasattr(self.enemy, 'attack_offset'):
            # losowy offset w lokalnej przestrzeni lidera
            self.enemy.attack_offset = pygame.Vector2(
                random.uniform(-30, 30),
                random.uniform(-30, 30)
            )
        return self.enemy.steering.offset_pursuit(leader, self.enemy.attack_offset)

    def exploration_mode(self, dt, player, game_map):
        steering_force = pygame.Vector2(0, 0)

        behaviors = ["hide", "separation", "wall_avoidance", "obstacle_avoidance",
                     "alignment", "cohesion", "wander"]

        for behavior in behaviors:
            if behavior == "hide" and self.enemy.peek.is_peeking():
                continue

            if random.random() <= self.probabilities.get(behavior, 1.0):
                force = getattr(self, behavior)(dt, player, game_map) * self.explore_weights.get(behavior, 1.0)

                if self.enemy.peek.is_peeking() and behavior == "wander":
                    force *= 1.8

                steering_force += force

        # ograniczamy siłę do max_force
        if steering_force.length() > self.enemy.max_force:
            steering_force.scale_to_length(self.enemy.max_force)

        return steering_force

    def attack_mode(self, dt, leader, player, game_map):
        steering_force = pygame.Vector2(0, 0)

        # Jeśli to lider - pursuit
        if self.enemy.is_group_leader:
            # lider musi iść do gracza i unikać przeszkód/ścian
            force_pursuit = self.pursuit(dt, player, game_map) if player is not None else pygame.Vector2(0, 0)

            steering_force += force_pursuit * self.attack_weights.get("pursuit", 1.0)
            steering_force += self.obstacle_avoidance(dt, player, game_map) * self.attack_weights.get(
                "obstacle_avoidance", 1.0)
            steering_force += self.wall_avoidance(dt, player, game_map) * self.attack_weights.get(
                "wall_avoidance", 1.0)

        else:
            # followers - offset_pursuit
            steering_force += self.offset_pursuit(dt, leader, game_map) * self.attack_weights.get("offset_pursuit", 1.0)
            # separation / alignment / cohesion
            steering_force += self.separation(dt, leader, game_map) * self.attack_weights.get("separation", 1.0)
            steering_force += self.alignment(dt, leader, game_map) * self.attack_weights.get("alignment", 1.0)
            steering_force += self.cohesion(dt, leader, game_map) * self.attack_weights.get("cohesion", 1.0)
            # avoidance
            steering_force += self.obstacle_avoidance(dt, player, game_map) * self.attack_weights.get(
                "obstacle_avoidance", 1.0)
            steering_force += self.wall_avoidance(dt, player, game_map) * self.attack_weights.get(
                "wall_avoidance", 1.0)

        # ograniczamy siłę do max_force
        if steering_force.length() > self.enemy.max_force:
            steering_force.scale_to_length(self.enemy.max_force)

        return steering_force