import pygame
from collections import deque

class Smoother:
    """Przechowuje próbki wektorów i zwraca ich średnią."""
    def __init__(self, num_samples: int):
        self.num_samples = num_samples
        self.samples = deque(maxlen=num_samples)

    def update(self, new_value: pygame.Vector2) -> pygame.Vector2:
        """Dodaje nową próbkę i zwraca średnią wszystkich próbek."""
        self.samples.append(new_value)
        if not self.samples:
            return new_value
        avg = pygame.Vector2(0, 0)
        for v in self.samples:
            avg += v
        avg /= len(self.samples)
        if avg.length_squared() > 1e-6:
            avg = avg.normalize()
        return avg