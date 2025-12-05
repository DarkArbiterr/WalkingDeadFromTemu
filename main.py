import pygame
from config import *
from map.game_map import GameMap

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mob Survival")

    # create map
    game_map = GameMap(WINDOW_WIDTH, WINDOW_HEIGHT)
    game_map.generate_obstacles(
        count=OBSTACLE_COUNT,
        min_radius=OBSTACLE_MIN_R,
        max_radius=OBSTACLE_MAX_R
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # draw
        screen.fill((30, 30, 30))  # background
        game_map.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()