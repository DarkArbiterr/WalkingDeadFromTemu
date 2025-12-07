import random
import math
import pygame
from utils.collision import circle_collision, resolve_circle_overlap, collision_with_walls
from steeringBehaviors.steering_behaviors import SteeringBehaviors
from utils.smoothing import Smoother
from utils.debuging import *
from .enemy_steering import *
from .enemy_group_manager import *
from config import *


class Enemy:
    def __init__(self, x, y, radius=15, mass=1.0, max_speed=150, max_force=2000, color=(196, 39, 113), flocking_radius=70.0):
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
        self.enemy_steering = EnemySteering(self)
        self.steering_force = pygame.Vector2(0, 0)  # do implementacji steering behavior

        self.neighbors = []
        self.flocking_radius = flocking_radius

        self.smoother = Smoother(num_samples=10)
        self.smoothed_heading = self.heading.copy()

        self.peek = EnemyPeek(self, base_chance=0.12, group_scale=0.6, min_duration=1.0, max_duration=3.0)

        # grupowanie/ataki
        self.state = "explore"  # możliwe: "explore" | "attack" | "dead"
        self.attack_group_id = None
        self.group = EnemyGroupManager(self, ATTACK_THRESHOLD)
        self.is_group_leader = False

    def get_triangle_points(self):
        # Skala trójkąta
        size = self.radius

        # Przód trójkąta — w kierunku heading
        tip = self.pos + self.smoothed_heading * size

        side = pygame.Vector2(-self.smoothed_heading.y, self.smoothed_heading.x)

        # Boki trójkąta
        left = self.pos - self.smoothed_heading * (size * 0.5) + side * (size * 0.6)
        right = self.pos - self.smoothed_heading * (size * 0.5) - side * (size * 0.6)

        return [tip, left, right]

    def update(self, dt, game_map, player=None):
        # resetujemy siłę sterującą
        self.steering_force = pygame.Vector2(0, 0)

        # oznacz sąsiadów
        self.find_neighbors(game_map.enemies)

        # update stanu grupy
        self.group.update()

        # sterring
        self.steering_force = self.enemy_steering.calculate_steering(dt, player, game_map)

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

        # smoothing
        self.smoothed_heading = self.smoother.update(self.heading)

        # Kolizje: przeszkody
        self.collides_with_obstacles(game_map.obstacles)

        # Kolizje: gracz i ściany
        if player:
            self.collides_with_player(player)

        self.collides_with_walls(game_map.width, game_map.height)

        # Non-Penetration Constraint dla wrogów
        if game_map.enemies is not None:
            self.enforce_non_penetration(game_map.enemies)

    def draw(self, screen, enemies):
        # wybór koloru w zależności od stanu
        if self.state == "attack":
            if self.is_group_leader:
                color_to_draw = (237, 63, 19)  # lider
            else:
                color_to_draw = (245, 124, 17)  # followers
        else:
            color_to_draw = self.color  # normalny kolor

        points = self.get_triangle_points()
        pygame.draw.polygon(screen, color_to_draw, [(p.x, p.y) for p in points])

        # debug: półprzezroczysta strefa
        draw_neighbors_area(screen, self.pos, radius=self.flocking_radius, color=(80, 80, 200), alpha=10)

        # debug: obwódki sąsiadów
        # draw_neighbors_outline(screen, self.neighbors, outline_color=(0, 255, 0))

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

    def enforce_non_penetration(self, agents):
        """Wymusza brak nakładania się jednostek.
        nie pozwalamy, aby lider był przesuwany przez followers.
        """
        n = len(agents)
        for i in range(n):
            a = agents[i]
            for j in range(i + 1, n):
                b = agents[j]
                # pomiń, jeśli to samo
                if a is b:
                    continue

                delta = a.pos - b.pos
                dist_sq = delta.length_squared()
                min_dist = a.radius + b.radius

                if dist_sq == 0:
                    # losowy kierunek, by uniknąć podziału przez zero
                    direction = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))
                    dist = 1.0
                else:
                    dist = math.sqrt(dist_sq)
                    direction = delta / dist  # od b do a

                overlap = min_dist - dist
                if overlap > 0:
                    # jeśli a jest liderem i b nie, przesuwamy tylko b
                    if getattr(a, "is_group_leader", False) and not getattr(b, "is_group_leader", False):
                        # przesuwamy b na zewnątrz (od a)
                        b.pos -= direction * overlap
                    elif getattr(b, "is_group_leader", False) and not getattr(a, "is_group_leader", False):
                        # przesuwamy a na zewnątrz (od b)
                        a.pos += direction * overlap
                    else:
                        half = overlap * 0.5
                        a.pos += direction * half
                        b.pos -= direction * half
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