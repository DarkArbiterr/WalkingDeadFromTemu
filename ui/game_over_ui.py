import pygame

class GameOverUI:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font_big = pygame.font.SysFont("Arial", 70, bold=True)
        self.font_btn = pygame.font.SysFont("Arial", 20, bold=True)

        self.button_rect = pygame.Rect(
            width // 2 - 120,
            height // 2 + 40,
            240,
            70
        )

    def draw(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        text = self.font_big.render("GAME OVER", True, (222, 55, 92))
        screen.blit(text, (self.width // 2 - text.get_width() // 2, self.height // 2 - 100))

        pygame.draw.rect(screen, (50, 125, 217), self.button_rect, border_radius=5)

        label = self.font_btn.render("RESTART", True, (218, 222, 227))
        screen.blit(label, (
            self.button_rect.x + self.button_rect.width // 2 - label.get_width() // 2,
            self.button_rect.y + self.button_rect.height // 2 - label.get_height() // 2
        ))

    def is_restart_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                return True
        return False