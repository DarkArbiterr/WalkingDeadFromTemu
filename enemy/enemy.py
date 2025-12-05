import random
import math
import pygame
from utils.collision import circle_collision, resolve_circle_overlap, collision_with_walls
from steeringBehaviors.steering_behaviors import SteeringBehaviors

class Enemy:
    def __init__(self, x, y, radius=20, mass=1.0, max_speed=100, max_force=200, color=(200,50,50)):
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

    def update(self, dt, game_map, player=None, all_enemies=None):
        # resetujemy siłę sterującą
        self.steering_force = pygame.Vector2(0, 0)

        # Steering behaviors
        if player is not None:

            # PURSUIT
            self.steering_force += self.steering.pursuit(player)

            # ARRIVE - deceleration: 'slow', 'normal', 'fast'
            # self.steering_force += self.steering.arrive(player.pos, deceleration='normal')

            # SEEK I FLEE:
            # panic_distance = 200
            # to_player = player.pos - self.pos
            #
            # if to_player.length_squared() <= panic_distance ** 2:
            #     # gracz jest blisko -> FLEE
            #     self.steering_force += self.steering.flee(player.pos, panic_distance)
            # else:
            #     # gracz daleko -> SEEK
            #     self.steering_force += self.steering.seek(player.pos)

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
        for _ in range(4):
            for other in game_map.enemies:
                if other is self:
                    continue
                if circle_collision(self.pos, self.radius, other.pos, other.radius):
                    resolve_circle_overlap(self.pos, self.radius, other.pos, other.radius)
            # po każdej iteracji upewniamy się, że nie wpadliśmy w przeszkodę
            self.collides_with_obstacles(game_map.obstacles)

        # Kolizje: gracz i ściany
        if player:
            self.collides_with_player(player)

        self.collides_with_walls(game_map.width, game_map.height)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

    def collides_with_obstacles(self, obstacles):
        collided = False
        for obs in obstacles:
            if circle_collision(self.pos, self.radius, obs.pos, obs.radius):
                resolve_circle_overlap(self.pos, self.radius, obs.pos, obs.radius)
                collided = True
        return collided

    # kolizja z graczem
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