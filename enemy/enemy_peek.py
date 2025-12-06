import pygame
import random

class EnemyPeek:
    """
    Obsługuje logikę krótkiego wychodzenia zza przeszkód (peek) dla Enemy.
    """
    def __init__(self, enemy):
        self.enemy = enemy

        self.time_since_last_peek = 0.0
        self.peek_interval = random.uniform(5.0, 15.0)  # losowy odstęp między peek
        self.peeking = False
        self.peek_timer = 0.0
        self.peek_duration = random.uniform(1.0, 3.0)

    def update(self, dt):
        """
        Update timerów, zmienia stan peeka w razie potrzeby.
        """
        if self.peeking:
            self.peek_timer += dt
            if self.peek_timer >= self.peek_duration:
                self._end_peek()
        else:
            self.time_since_last_peek += dt
            if self.time_since_last_peek >= self.peek_interval:
                self._start_peek()

    def _start_peek(self):
        self.peeking = True
        self.peek_timer = 0.0
        self.peek_duration = random.uniform(1.0, 3.0)
        # lekko przemieszczamy wander_target
        try:
            wt = self.enemy.steering.wander_target
            wt += pygame.Vector2(random.uniform(-5, 5), random.uniform(-5, 5))
        except Exception:
            pass

    def _end_peek(self):
        self.peeking = False
        self.time_since_last_peek = 0.0
        self.peek_interval = random.uniform(6.0, 18.0)  # następny losowy interwał

    def is_peeking(self):
        """
        Zwraca True jeśli bot aktualnie wychodzi zza przeszkody
        """
        return self.peeking