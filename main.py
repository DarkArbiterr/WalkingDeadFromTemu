import pygame
from config import *
from map.game_map import GameMap
from player.player import Player
from enemy.enemy import Enemy
from ui.game_over_ui import GameOverUI
from ui.health_ui import HealthUI


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Walking Dead From Temu")
    clock = pygame.time.Clock()

    player = Player(30, 30)
    player_dead = False
    health_ui = HealthUI(player.hp)
    game_over_ui = GameOverUI(WINDOW_WIDTH, WINDOW_HEIGHT)

    # create map
    game_map = GameMap(WINDOW_WIDTH, WINDOW_HEIGHT)
    game_map.generate_obstacles(
        count=OBSTACLE_COUNT,
        min_radius=OBSTACLE_MIN_R,
        max_radius=OBSTACLE_MAX_R,
        safe_zone_center = player.pos,
        safe_zone_size = 200
    )

    game_map.generate_enemies(
        count=ENEMY_COUNT,
        enemy_radius=player.radius,
        safe_zone_center= player.pos,
        safe_zone_size=500
    )

    running = True
    player_dead = False
    game_over_ui = GameOverUI(WINDOW_WIDTH, WINDOW_HEIGHT)

    while running:
        dt = clock.tick(FPS) / 1000  # seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not player_dead:
                if player:
                    player.handle_shoot_event(event)
            else:
                # GAME OVER
                if game_over_ui.is_restart_clicked(event):
                    return main()

        # draw
        screen.fill((30, 30, 30))  # background

        if not player_dead:
            if player:
                player.update(dt, game_map, screen)
                if player.hp <= 0:
                    player_dead = True
                    player = None

            if player:
                for enemy in game_map.enemies:
                    enemy.update(dt, game_map, player)

        if player:
            player.draw(screen)

        game_map.draw(screen)
        if not player_dead:
            health_ui.draw(screen, player.hp)
        else:
            game_over_ui.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()