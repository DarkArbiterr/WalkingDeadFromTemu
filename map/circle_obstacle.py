import pygame

class CircleObstacle:
    def __init__(self, x: float, y: float, radius: float):
        self.pos = pygame.Vector2(x, y)
        self.radius = radius

    def collides_with(self, other: "CircleObstacle") -> bool:
        offset = self.pos - other.pos
        distance_sq = offset.length_squared()
        radius_sum = self.radius + other.radius
        return distance_sq < radius_sum * radius_sum