import pygame

class SteeringBehaviors:
    def __init__(self, agent):
        """
        agent: obiekt
        """
        self.agent = agent

    def seek(self, target_pos):
        """
        Seek: zwraca siłę skierowaną w stronę celu
        """
        if target_pos is None:
            return pygame.Vector2(0, 0)

        desired_velocity = target_pos - self.agent.pos
        if desired_velocity.length_squared() > 0:
            desired_velocity = desired_velocity.normalize() * self.agent.max_speed
        else:
            desired_velocity = pygame.Vector2(0, 0)

        steering_force = desired_velocity - self.agent.velocity
        return steering_force

    # tu później dodamy inne steering behaviors (flee, arrive, wander itd.)