import pygame

class SteeringBehaviors:
    def __init__(self, agent):
        self.agent = agent

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