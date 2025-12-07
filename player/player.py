import pygame
import math
from utils.geometry import ray_circle_intersection
from utils.collision import circle_collision, resolve_circle_overlap, collision_with_walls

class Player:
    def __init__(self, x, y, speed=150, radius=15):
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = speed
        self.radius = radius  # collider
        self.heading = pygame.Vector2(1, 0)
        self.side = pygame.Vector2(-1, 0)
        self.shoot_cooldown = 0.5  # w sekundach
        self.time_since_last_shot = 0
        self.want_to_shoot = False

    def handle_shoot_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.want_to_shoot = True

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1

        # normalizacja ruchu
        if move.length_squared() > 0:
            move = move.normalize()

        self.velocity = move * self.speed
        self.pos += self.velocity * dt

    def update_angle(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        direction = mouse_pos - self.pos
        if direction.length_squared() > 0:
            self.heading = direction.normalize()
            self.side = pygame.Vector2(-self.heading.y, self.heading.x)

    def update(self, dt, game_map, screen):
        self.handle_input(dt)
        self.collides_with_walls(game_map.width, game_map.height)
        self.collides_with_obstacles(game_map.obstacles)
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

    def collides_with_walls(self, map_width, map_height):
        collision_with_walls(self.pos, self.radius, map_width, map_height)

    def collides_with_obstacles(self, obstacles):
        for obs in obstacles:
            if circle_collision(self.pos, self.radius, obs.pos, obs.radius):
                resolve_circle_overlap(self.pos, self.radius, obs.pos, obs.radius)

    def shoot(self, obstacles, screen, enemies=None):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        # direction (normalize)
        direction = (mouse_pos - self.pos).normalize()

        closest_t = None
        closest_hit = None  # przeszkoda, która zatrzyma promień

        # kolizje z obstacles
        for obs in obstacles:
            t = ray_circle_intersection(
                self.pos.x, self.pos.y,
                direction.x, direction.y,
                obs.pos.x, obs.pos.y, obs.radius
            )
            if t is not None:
                if closest_t is None or t < closest_t:
                    closest_t = t
                    closest_hit = obs

        # kolizje z enemy
        if enemies is not None:
            for enemy in enemies[:]:  # kopiujemy listę, żeby można usuwać
                t_enemy = ray_circle_intersection(
                    self.pos.x, self.pos.y,
                    direction.x, direction.y,
                    enemy.pos.x, enemy.pos.y, enemy.radius)
                if t_enemy is not None:
                    # jeśli enemy jest bliżej niż przeszkoda lub brak przeszkody
                    if closest_t is None or t_enemy < closest_t:
                        closest_t = t_enemy
                        closest_hit = enemy

        # jeśli trafiono w enemy - usuwamy
        if isinstance(closest_hit, type(enemies[0])):
            closest_hit.state = "dead"
            closest_hit.is_group_leader = False
            enemies.remove(closest_hit)

        # koniec promienia do rysowania
        if closest_t is not None:
            end_pos = self.pos + direction * closest_t
        else:
            far = 5000
            end_pos = self.pos + direction * far

        # draw ray
        pygame.draw.line(screen, (255, 0, 0), self.pos, end_pos, 2)

    def draw(self, screen):
        # 3 wierzchołki trójkąta
        tip = self.pos + self.heading * self.radius

        left = self.pos + pygame.Vector2(
            math.cos(math.atan2(self.heading.y, self.heading.x) + 2.5),
            math.sin(math.atan2(self.heading.y, self.heading.x) + 2.5)
        ) * self.radius

        right = self.pos + pygame.Vector2(
            math.cos(math.atan2(self.heading.y, self.heading.x) - 2.5),
            math.sin(math.atan2(self.heading.y, self.heading.x) - 2.5)
        ) * self.radius

        pygame.draw.polygon(
            screen,
            (200, 200, 50),
            [tip, left, right]
        )

        pygame.draw.circle(screen, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), self.radius, 1)

