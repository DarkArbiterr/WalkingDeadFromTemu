import random
import math
import pygame
from utils.collision import circle_collision, resolve_circle_overlap, collision_with_walls
from steeringBehaviors.steering_behaviors import SteeringBehaviors
from utils.debuging import *
from .enemy_steering import *


class Enemy:
    def __init__(self, x, y, radius=15, mass=1.0, max_speed=150, max_force=8000, color=(200,50,50), flocking_radius=100.0):
        self.pos = pygame.Vector2(x, y)
        self.radius = radius
        self.mass = mass
        self.max_speed = max_speed
        self.max_force = max_force
        self.color = color
        self.velocity = pygame.Vector2(0, 0)
        self.heading = pygame.Vector2(1, 0)
        self.side = pygame.Vector2(-1, 0)  # prostopadły wektor

        self.steering = SteeringBehaviors(self)
        self.steering_force = pygame.Vector2(0, 0)  # do implementacji steering behavior

        self.neighbors = []
        self.flocking_radius = flocking_radius

    def get_triangle_points(self):
        # Skala trójkąta
        size = self.radius

        # Przód trójkąta — w kierunku heading
        tip = self.pos + self.heading * size

        # Boki trójkąta
        left = self.pos - self.heading * (size * 0.5) + self.side * (size * 0.6)
        right = self.pos - self.heading * (size * 0.5) - self.side * (size * 0.6)

        return [tip, left, right]

    def update(self, dt, game_map, player=None, all_enemies=None):
        # resetujemy siłę sterującą
        self.steering_force = pygame.Vector2(0, 0)

        # oznacz sąsiadów
        self.find_neighbors(game_map.enemies)

        self.steering_force = calculate_steering(self, dt, player, game_map)

        # przyspieszenie: F = ma
        acceleration = self.steering_force / self.mass

        # aktualizacja prędkości
        self.velocity += acceleration * dt

        # przytnij prędkość do max_speed
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

        # aktualizacja pozycji
        self.pos += self.velocity * dt

        # aktualizacja heading i side
        if self.velocity.length_squared() > 1e-6:
            self.heading = self.velocity.normalize()
            self.side = pygame.Vector2(-self.heading.y, self.heading.x)

        # Kolizje: przeszkody
        self.collides_with_obstacles(game_map.obstacles)

        # iteracyjne odpychanie enemies, 3-5 iteracji stabilizuje układ
        # for _ in range(4):
        #     for other in game_map.enemies:
        #         if other is self:
        #             continue
        #         if circle_collision(self.pos, self.radius, other.pos, other.radius):
        #             resolve_circle_overlap(self.pos, self.radius, other.pos, other.radius)
        #     # po każdej iteracji upewniamy się, że nie wpadliśmy w przeszkodę
        #     self.collides_with_obstacles(game_map.obstacles)

        # Kolizje: gracz i ściany
        if player:
            self.collides_with_player(player)

        self.collides_with_walls(game_map.width, game_map.height)

    def draw(self, screen, enemies):
        points = self.get_triangle_points()
        pygame.draw.polygon(screen, self.color, [(p.x, p.y) for p in points])

        # debug: półprzezroczysta strefa
        draw_neighbors_area(screen, self.pos, radius=100, color=(80, 80, 200), alpha=10)

        # debug: obwódki sąsiadów
        draw_neighbors_outline(screen, self.neighbors, outline_color=(0, 255, 0))

    def collides_with_obstacles(self, obstacles):
        collided = False
        for obs in obstacles:
            if circle_collision(self.pos, self.radius, obs.pos, obs.radius):
                resolve_circle_overlap(self.pos, self.radius, obs.pos, obs.radius)
                collided = True
        return collided

    def collides_with_player(self, player):
        if circle_collision(self.pos, self.radius, player.pos, player.radius):
            # odpychanie gracza (jak przy przeszkodach)
            resolve_circle_overlap(self.pos, self.radius, player.pos, player.radius)
            return True
        return False

    def collides_with_walls(self, map_width, map_height):
        collision_with_walls(self.pos, self.radius, map_width, map_height)

    def collides_with_enemies(self, enemies):
        collided = False
        for other in enemies:
            if other is self:
                continue  # nie sprawdzaj samego siebie
            if circle_collision(self.pos, self.radius, other.pos, other.radius):
                resolve_circle_overlap(self.pos, self.radius, other.pos, other.radius)
                collided = True
        return collided

    def find_neighbors(self, agents):
        """Zbiera listę sąsiadów tylko dla tego agenta."""
        self.neighbors = []

        for other in agents:
            if other is self:
                continue

            to = other.pos - self.pos
            range_check = self.flocking_radius + other.radius

            if to.length_squared() < range_check ** 2:
                self.neighbors.append(other)