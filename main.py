import pygame
from config import *
from map.game_map import GameMap
from player.player import Player

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mob Survival")
    clock = pygame.time.Clock()

    # create map
    game_map = GameMap(WINDOW_WIDTH, WINDOW_HEIGHT)
    game_map.generate_obstacles(
        count=OBSTACLE_COUNT,
        min_radius=OBSTACLE_MIN_R,
        max_radius=OBSTACLE_MAX_R
    )

    player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000  # seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # draw
        screen.fill((30, 30, 30))  # background
        player.update(dt)
        player.draw(screen)
        game_map.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()