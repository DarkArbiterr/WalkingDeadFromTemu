import pygame
import colorsys

def draw_neighbors_area(screen, pos, radius, color=(80, 80, 200), alpha=20):
    """
    Rysuje półprzezroczyste kółko wokół bota - obszar szukania sasiadow.
    :param screen: Surface, na którym rysujemy
    :param pos: pygame.Vector2 lub tuple (x, y) — środek bota
    :param radius: promień obszaru zainteresowania
    :param color: RGB kółka
    :param alpha: przezroczystość 0-255
    """
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(surf, (*color, alpha), (radius, radius), radius)
    screen.blit(surf, (pos[0] - radius, pos[1] - radius))

def draw_neighbors_outline(screen, neighbors, outline_color=(0, 255, 0)):
    """
    Rysuje obwódki wokół sąsiadów.
    :param screen: Surface
    :param neighbors: lista agentów (muszą mieć .pos i .radius)
    :param outline_color: kolor obwódki
    """
    for other in neighbors:
        pygame.draw.circle(
            screen,
            outline_color,
            (int(other.pos.x), int(other.pos.y)),
            other.radius + 3,
            2
        )