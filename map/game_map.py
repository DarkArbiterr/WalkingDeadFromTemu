import random
import pygame
from enemy.enemy import Enemy
from .circle_obstacle import CircleObstacle

class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.obstacles: list[CircleObstacle] = []
        self.enemies: list[Enemy] = []

    def generate_obstacles(
        self,
        count: int,
        min_radius: int = 20,
        max_radius: int = 60,
        max_attempts: int = 2000,
        safe_zone_center: pygame.Vector2 = None,
        safe_zone_size = 0
    ):
        attempts = 0

        while len(self.obstacles) < count and attempts < max_attempts:
            attempts += 1

            radius = random.randint(min_radius, max_radius)

            x = random.randint(radius, self.width - radius)
            y = random.randint(radius, self.height - radius)
            pos = pygame.Vector2(x, y)

            # sprawdzenie safe zone
            if safe_zone_center is not None and safe_zone_size > 0:
                half = safe_zone_size / 2
                if (safe_zone_center.x - half - radius < pos.x < safe_zone_center.x + half + radius and
                    safe_zone_center.y - half - radius < pos.y < safe_zone_center.y + half + radius):
                    continue  # kolizja ze strefą startową - generuj nowy

            new_circle = CircleObstacle(x, y, radius)

            if any(new_circle.collides_with(o) for o in self.obstacles):
                continue

            self.obstacles.append(new_circle)

    def generate_enemies(
            self,
            count: int,
            enemy_radius: int,
            safe_zone_center: pygame.Vector2 = None,
            safe_zone_size=0,
            max_attempts=2000
    ):
        attempts = 0
        self.enemies = []

        while len(self.enemies) < count and attempts < max_attempts:
            attempts += 1

            x = random.randint(enemy_radius, self.width - enemy_radius)
            y = random.randint(enemy_radius, self.height - enemy_radius)
            pos = pygame.Vector2(x, y)

            # sprawdzenie safe zone
            if safe_zone_center is not None and safe_zone_size > 0:
                half = safe_zone_size / 2
                if (safe_zone_center.x - half - enemy_radius < pos.x < safe_zone_center.x + half + enemy_radius and
                        safe_zone_center.y - half - enemy_radius < pos.y < safe_zone_center.y + half + enemy_radius):
                    continue  # kolizja ze strefą startową - generuj nowy

            # kolizja z przeszkodami
            new_enemy = Enemy(x, y, enemy_radius)
            if new_enemy.collides_with_obstacles(self.obstacles):
                continue

            self.enemies.append(new_enemy)

    def draw(self, surface: pygame.Surface):
        """Draw all obstacles and enemies"""
        for obs in self.obstacles:
            pygame.draw.circle(surface, (120, 120, 120), obs.pos, obs.radius)
        for enemy in self.enemies:
            enemy.draw(surface)