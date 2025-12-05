import pygame

def circle_collision(pos1: pygame.Vector2, radius1: float,
                     pos2: pygame.Vector2, radius2: float) -> bool:
    """Sprawdza, czy dwa okręgi kolidują"""
    return (pos1 - pos2).length_squared() < (radius1 + radius2) ** 2


def resolve_circle_overlap(pos1: pygame.Vector2, radius1: float,
                           pos2: pygame.Vector2, radius2: float):
    """Przesuwa pos1, aby nie nachodziło na pos2"""
    delta = pos1 - pos2
    dist_sq = delta.length_squared()
    min_dist = radius1 + radius2

    if dist_sq == 0:
        # edge case: nakładające się środki
        delta = pygame.Vector2(1, 0)
        dist_sq = 1

    if dist_sq < min_dist * min_dist:
        dist = dist_sq ** 0.5
        overlap = min_dist - dist
        pos1 += (delta / dist) * overlap

def collision_with_walls(pos: pygame.Vector2, radius: float, map_width: int, map_height: int):
    """Zapobiega wychodzeniu okręgu poza granice mapy"""
    if pos.x - radius < 0:
        pos.x = radius
    elif pos.x + radius > map_width:
        pos.x = map_width - radius

    if pos.y - radius < 0:
        pos.y = radius
    elif pos.y + radius > map_height:
        pos.y = map_height - radius