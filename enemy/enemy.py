import random
import math
import pygame

class Enemy:
    def __init__(self, x, y, radius=20, color=(200,50,50)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def collides_with_obstacle(self, obstacle):
        dx = self.x - obstacle.x
        dy = self.y - obstacle.y
        dist_sq = dx*dx + dy*dy
        radius_sum = self.radius + obstacle.radius
        return dist_sq < radius_sum*radius_sum

    # kolizja z graczem
    def collides_with_player(self, player):
        dx = self.x - player.x
        dy = self.y - player.y
        dist_sq = dx*dx + dy*dy
        radius_sum = self.radius + player.radius
        return dist_sq < radius_sum*radius_sum