import pygame

class Wall:
    def __init__(self, start: pygame.Vector2, end: pygame.Vector2):
        self.start = start
        self.end = end
        # normal skierowany do wnętrza mapy
        delta = end - start
        self.normal = pygame.Vector2(-delta.y, delta.x).normalize()

    def from_pos(self):
        return self.start

    def to_pos(self):
        return self.end

    def normal_vec(self):
        return self.normal