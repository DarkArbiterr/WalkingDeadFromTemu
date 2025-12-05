import random
import pygame
from .circle_obstacle import CircleObstacle

class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.obstacles: list[CircleObstacle] = []

    def generate_obstacles(
        self,
        count: int,
        min_radius: int = 20,
        max_radius: int = 60,
        max_attempts: int = 2000,
        safe_zone_center = None,  # tuple (x, y)
        safe_zone_size = 0
    ):
        attempts = 0

        while len(self.obstacles) < count and attempts < max_attempts:
            attempts += 1

            radius = random.randint(min_radius, max_radius)

            x = random.randint(radius, self.width - radius)
            y = random.randint(radius, self.height - radius)

            # sprawdzenie safe zone
            if safe_zone_center is not None and safe_zone_size > 0:
                sx, sy = safe_zone_center
                half = safe_zone_size / 2
                if sx - half - radius < x < sx + half + radius and sy - half - radius < y < sy + half + radius:
                    continue  # kolizja ze strefą startową - generuj nowy

            new_circle = CircleObstacle(x, y, radius)

            if any(new_circle.collides_with(o) for o in self.obstacles):
                continue

            self.obstacles.append(new_circle)

    def draw(self, surface: pygame.Surface):
        """Draw all obstacles"""
        for obs in self.obstacles:
            pygame.draw.circle(surface, (120, 120, 120), (int(obs.x), int(obs.y)), obs.radius)