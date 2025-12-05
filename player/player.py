import pygame
import math

class Player:
    def __init__(self, x, y, speed=250, radius=20):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius  # collider
        self.angle = 0        # rotation

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

    def update(self, dt):
        self.handle_input(dt)
        self.update_angle()

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