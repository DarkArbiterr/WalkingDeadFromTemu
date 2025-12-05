import random
import pygame

class SteeringBehaviors:
    def __init__(self, agent):
        self.agent = agent

        # --- WANDER parameters ---
        self.wander_radius = 30.0  # promień okręgu
        self.wander_distance = 40.0  # odległość środka okręgu od agenta
        self.wander_jitter = 80.0  # max losowe przesunięcie na sekundę

        # pozycja początkowa celu na okręgu
        self.wander_target = pygame.Vector2(self.wander_radius, 0)

    def seek(self, target_pos):
        """Seek target position"""
        if target_pos is None:
            return pygame.Vector2(0, 0)

        desired_velocity = target_pos - self.agent.pos
        if desired_velocity.length_squared() > 0:
            desired_velocity = desired_velocity.normalize() * self.agent.max_speed
        else:
            desired_velocity = pygame.Vector2(0, 0)

        steering_force = desired_velocity - self.agent.velocity
        return steering_force

    def flee(self, target_pos, panic_distance=None):
        """Flee from target position. Optional panic distance."""
        to_target = self.agent.pos - target_pos

        # jeśli jest panic_distance i cel jest dalej niż dystans paniki, nic nie rób
        if panic_distance is not None and to_target.length_squared() > panic_distance**2:
            return pygame.Vector2(0, 0)
        desired_velocity = to_target.normalize() * self.agent.max_speed
        return desired_velocity - self.agent.velocity

    def arrive(self, target_pos: pygame.Vector2, deceleration: str = 'normal') -> pygame.Vector2:
        # deceleration: 'slow', 'normal', 'fast'
        deceleration_mapping = {'fast': 1, 'normal': 2, 'slow': 3}
        decel = deceleration_mapping.get(deceleration, 2)

        to_target = target_pos - self.agent.pos
        dist = to_target.length()

        if dist > 0:
            deceleration_tweaker = 1.3
            # prędkość wymagana, aby dojść do celu
            speed = dist / (decel * deceleration_tweaker)
            speed = min(speed, self.agent.max_speed)

            desired_velocity = to_target * speed / dist
            return desired_velocity - self.agent.velocity

        return pygame.Vector2(0, 0)

    def pursuit(self, evader):
        to_evader = evader.pos - self.agent.pos

        # Dot product: czy evader jest przed agentem?
        relative_heading = self.agent.heading.dot(evader.heading)

        # Czy evader jest "przed nami" i niemal się nie obraca względem nas?
        if to_evader.dot(self.agent.heading) > 0 and relative_heading < -0.95:
            # seek do aktualnej pozycji
            return self.seek(evader.pos)

        # przewidujemy przyszłą pozycję:
        distance = to_evader.length()
        speed_sum = self.agent.max_speed + evader.velocity.length()

        if speed_sum != 0:
            look_ahead_time = distance / speed_sum
        else:
            look_ahead_time = 0

        future_pos = evader.pos + evader.velocity * look_ahead_time

        return self.seek(future_pos)

    def evade(self, pursuer):
        to_pursuer = pursuer.pos - self.agent.pos

        # przewidujemy przyszłą pozycję
        look_ahead_time = to_pursuer.length() / (self.agent.max_speed + pursuer.velocity.length())

        future_pos = pursuer.pos + pursuer.velocity * look_ahead_time

        # flee
        return self.flee(future_pos)

    def wander(self, dt: float):
        # losowy jitter dodany do celu na okręgu
        jitter = self.wander_jitter * dt
        self.wander_target += pygame.Vector2(
            random.uniform(-1, 1) * jitter,
            random.uniform(-1, 1) * jitter
        )

        # normalizacja + rzut z powrotem na okrąg
        if self.wander_target.length_squared() > 0:
            self.wander_target = self.wander_target.normalize() * self.wander_radius

        # przesunięcie okręgu przed agenta
        target_local = self.wander_target + pygame.Vector2(self.wander_distance, 0)

        # transformacja do świata
        heading = self.agent.velocity.normalize() if self.agent.velocity.length() > 0 else pygame.Vector2(1, 0)
        side = pygame.Vector2(-heading.y, heading.x)

        target_world = (
                self.agent.pos +
                heading * target_local.x +
                side * target_local.y
        )

        # 5) Siła sterująca — SEEK do target_world
        return (target_world - self.agent.pos).normalize() * self.agent.max_speed