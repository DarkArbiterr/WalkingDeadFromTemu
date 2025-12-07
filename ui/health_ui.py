import pygame

class HealthUI:
    def __init__(self, max_hp=3):
        self.max_hp = max_hp

        # rozmiar serca
        self.size = 32

        # potem podmianka na png
        self.heart_full = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.heart_empty = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        self._draw_full_heart()
        self._draw_empty_heart()

    # to potem wywalic i dac png
    def _draw_full_heart(self):
        pygame.draw.polygon(self.heart_full, (255, 50, 50), [
            (16, 4), (28, 12), (28, 22), (16, 30), (4, 22), (4, 12)
        ])

    def _draw_empty_heart(self):
        pygame.draw.polygon(self.heart_empty, (80, 80, 80), [
            (16, 4), (28, 12), (28, 22), (16, 30), (4, 22), (4, 12)
        ], width=3)

    def draw(self, screen, current_hp):
        padding = 10
        x = screen.get_width() - (self.max_hp * (self.size + 8)) - padding
        y = padding

        for i in range(self.max_hp):
            if i < current_hp:
                screen.blit(self.heart_full, (x + i*(self.size+8), y))
            else:
                screen.blit(self.heart_empty, (x + i*(self.size+8), y))