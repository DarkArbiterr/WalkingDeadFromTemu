import pygame
import random
import math

class EnemyPeek:
    """
    Obsługuje logikę krótkiego wychodzenia zza przeszkód (peek) dla Enemy.
    """
    def __init__(self, enemy, base_chance = 0.19, group_scale = 0.9, min_duration = 1.0,
                 max_duration = 3.0, check_interval = 0.25):
        self.enemy = enemy

        # parametry sterujące
        self.base_chance = base_chance
        self.group_scale = group_scale
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.check_interval = check_interval

        # stan peek
        self.peeking = False
        self.peek_timer = 0.0
        self.peek_duration = 0.0

        # cooldown między peekami
        self.cooldown = random.uniform(2.0, 6.0)

        # wewnętrzny licznik
        self._check_acc = 0.0

    def update(self, dt):
        """
        Wywoływane co klatkę. Jeśli peeking: odliczamy czas.
        Jeśli nie peeking - co `check_interval` obliczamy, czy zacząć peek
        w oparciu o rozmiar grupy (neighbors).
        """
        if self.peeking:
            self.peek_timer += dt
            if self.peek_timer >= self.peek_duration:
                self._end_peek()
            return

        if self.cooldown > 0:
            self.cooldown -= dt
            if self.cooldown < 0:
                self.cooldown = 0.0

        self._check_acc += dt
        if self._check_acc < self.check_interval:
            return
        self._check_acc = 0.0

        if self.cooldown > 0:
            return

        # rozmiar grupy
        group_size = 1 + (len(self.enemy.neighbors) if self.enemy.neighbors is not None else 0)

        # szansa maleje wykładniczo wraz ze wzrostem grupy
        peek_chance = self.base_chance * math.exp(-self.group_scale * (group_size - 1))

        if random.random() < peek_chance:
            self._start_peek()

    def _start_peek(self):
        self.enemy.is_peeking = True
        self.peeking = True
        self.peek_timer = 0.0
        self.peek_duration = random.uniform(self.min_duration, self.max_duration)
        # lekko przemieszczamy wander_target
        try:
            wt = self.enemy.steering.wander_target
            wt += pygame.Vector2(random.uniform(-5, 5), random.uniform(-5, 5))
        except Exception:
            pass

    def _end_peek(self):
        self.enemy.is_peeking = False
        self.peeking = False
        self.peek_timer = 0.0
        self.peek_duration = 0.0
        # po peek losowy cooldown
        self.cooldown = random.uniform(4.0, 12.0)

    def is_peeking(self):
        """
        Zwraca True jeśli bot aktualnie wychodzi zza przeszkody
        """
        return self.peeking