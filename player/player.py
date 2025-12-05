import pygame
import math
from utils.geometry import ray_circle_intersection

class Player:
    def __init__(self, x, y, speed=250, radius=20):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius  # collider
        self.angle = 0        # rotacja
        self.shoot_cooldown = 0.5  # w sekundach
        self.time_since_last_shot = 0
        self.want_to_shoot = False

    def handle_shoot_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.want_to_shoot = True

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        # normalizacja ruchu
        if dx != 0 or dy != 0:
            length = math.sqrt(dx*dx + dy*dy)
            dx /= length
            dy /= length

        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt

    def update_angle(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.angle = math.atan2(mouse_y - self.y, mouse_x - self.x)

    def update(self, dt, game_map, screen):
        self.handle_input(dt)
        self.collide_with_walls(game_map.width, game_map.height)
        self.collide_with_obstacles(game_map.obstacles)
        self.update_angle()
        self.time_since_last_shot += dt

        # sprawdzamy przytrzymanie LPM
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if mouse_pressed:
            self.want_to_shoot = True

        # jeśli gracz kliknął i cooldown minął to strzel
        if self.want_to_shoot and self.time_since_last_shot >= self.shoot_cooldown:
            self.shoot(game_map.obstacles, screen, game_map.enemies)
            self.time_since_last_shot = 0

        # reset kliknięcia
        if not mouse_pressed:
            self.want_to_shoot = False

    def collide_with_walls(self, map_width, map_height):
        # left wall
        if self.x - self.radius < 0:
            self.x = self.radius
        # right wall
        if self.x + self.radius > map_width:
            self.x = map_width - self.radius
        # top wall
        if self.y - self.radius < 0:
            self.y = self.radius
        # bottom wall
        if self.y + self.radius > map_height:
            self.y = map_height - self.radius

    def collide_with_obstacles(self, obstacles):
        for obs in obstacles:
            dx = self.x - obs.x
            dy = self.y - obs.y
            dist = math.sqrt(dx * dx + dy * dy)
            overlap = self.radius + obs.radius - dist

            if overlap > 0:  # kolizja
                if dist == 0:
                    # edge case: środek idealnie się pokrywa to przesuwamy losowo
                    dx, dy = 1, 0
                    dist = 1

                # normalizacja
                nx = dx / dist
                ny = dy / dist

                # odpychanie gracza od przeszkody
                self.x += nx * overlap
                self.y += ny * overlap

    def shoot(self, obstacles, screen, enemies=None):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # direction (normalize)
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        length = math.sqrt(dx * dx + dy * dy)
        dx /= length
        dy /= length

        closest_t = None
        closest_hit = None  # przeszkoda, która zatrzyma promień

        # intersection with every obstacle
        for obs in obstacles:
            t = ray_circle_intersection(
                self.x, self.y,
                dx, dy,
                obs.x, obs.y, obs.radius
            )
            if t is not None:
                if closest_t is None or t < closest_t:
                    closest_t = t
                    closest_hit = obs

        # sprawdzamy kolizję z enemy
        if enemies is not None:
            for enemy in enemies[:]:  # kopiujemy listę, żeby można usuwać
                t_enemy = ray_circle_intersection(self.x, self.y, dx, dy, enemy.x, enemy.y, enemy.radius)
                if t_enemy is not None:
                    # jeśli enemy jest bliżej niż przeszkoda lub brak przeszkody
                    if closest_t is None or t_enemy < closest_t:
                        closest_t = t_enemy
                        closest_hit = enemy

        # jeśli trafiono w enemy - usuwamy
        if isinstance(closest_hit, type(enemies[0])):  # jest enemy
            enemies.remove(closest_hit)

        # koniec promienia do rysowania
        if closest_t is not None:
            end_x = self.x + dx * closest_t
            end_y = self.y + dy * closest_t
        else:
            far = 5000
            end_x = self.x + dx * far
            end_y = self.y + dy * far

        # draw ray
        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (end_x, end_y), 2)

    def draw(self, screen):

        # 3 wierzchołki trójkąta
        tip = (
            self.x + math.cos(self.angle) * self.radius,
            self.y + math.sin(self.angle) * self.radius
        )

        left = (
            self.x + math.cos(self.angle + 2.5) * self.radius,
            self.y + math.sin(self.angle + 2.5) * self.radius
        )

        right = (
            self.x + math.cos(self.angle - 2.5) * self.radius,
            self.y + math.sin(self.angle - 2.5) * self.radius
        )

        pygame.draw.polygon(
            screen,
            (200, 200, 50),
            [tip, left, right]
        )

        pygame.draw.circle(screen, (255,0,0), (int(self.x),int(self.y)), self.radius, 1)