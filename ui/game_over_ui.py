import pygame

class GameOverUI:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.overlay = pygame.Surface((width, height))
        self.overlay.set_alpha(150)
        self.overlay.fill((0, 0, 0))

        self.font = pygame.font.SysFont("arial", 72, bold=True)

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0))

        text_surface = self.font.render("GAME OVER", True, (255, 50, 50))
        rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))

        screen.blit(text_surface, rect)