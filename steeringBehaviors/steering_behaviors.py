import math
import random
import pygame

def world_to_local(point, agent_pos, heading, side):
    # Transformacja punktu do lokalnej przestrzeni agenta
    dx = point.x - agent_pos.x
    dy = point.y - agent_pos.y
    local_x = dx * heading.x + dy * heading.y
    local_y = dx * side.x + dy * side.y
    return pygame.Vector2(local_x, local_y)

def local_to_world(local_vec, heading, side):
    # Transformacja wektora z lokalnej przestrzeni do świata
    world_x = local_vec.x * heading.x + local_vec.y * side.x
    world_y = local_vec.x * heading.y + local_vec.y * side.y
    return pygame.Vector2(world_x, world_y)

class SteeringBehaviors:
    def __init__(self, agent):
        self.agent = agent

        # --- WANDER parameters ---
        self.wander_radius = 30.0  # promień okręgu
        self.wander_distance = 40.0  # odległość środka okręgu od agenta
        self.wander_jitter = 80.0  # max losowe przesunięcie na sekundę

        # pozycja początkowa celu na okręgu
        self.wander_target = pygame.Vector2(self.wander_radius, 0)

        # parametry do strojenia Obstacle-avoidance
        self.min_detection_box_length = 120.0  # minimalna długość boxa
        self.braking_weight = 0.1

        # feelery do Wall Avoidance
        self.feeler_length = 500  # długość feelerów
        self.feelers = [pygame.Vector2(0, 0) for _ in range(3)]  # 3 feelery: przód, lewy, prawy

        # ustawienie dystansu od przeszkody
        self.distance_from_boundary = 50.0

        # lista waypointów - PATH FOLLOW
        self.path = None
        self.current_waypoint_index = 0
        self.waypoint_seek_radius = 50  # promień w pikselach
        self.waypoint_seek_radius_sq = self.waypoint_seek_radius ** 2

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
            deceleration_tweaker = 0.3
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

    def obstacle_avoidance(self, obstacles):
        if not obstacles:
            return pygame.Vector2(0, 0)

        # dynamiczna długość boxa zależna od prędkości
        speed_ratio = self.agent.velocity.length() / self.agent.max_speed
        detection_box_length = self.min_detection_box_length + speed_ratio * self.min_detection_box_length

        closest_intersection = None
        dist_to_closest = float('inf')
        local_pos_of_closest = None

        for obs in obstacles:
            # transformacja przeszkody do lokalnej przestrzeni agenta
            local_pos = world_to_local(obs.pos, self.agent.pos, self.agent.heading, self.agent.side)

            if local_pos.x >= 0:  # tylko przeszkody przed agentem
                expanded_radius = obs.radius + self.agent.radius
                if abs(local_pos.y) < expanded_radius:
                    # prosta linia x=0, przecięcie z okręgiem przeszkody
                    cX = local_pos.x
                    cY = local_pos.y
                    sqrt_part = math.sqrt(expanded_radius ** 2 - cY ** 2)
                    ip = cX - sqrt_part
                    if ip <= 0:
                        ip = cX + sqrt_part

                    if ip < dist_to_closest:
                        dist_to_closest = ip
                        closest_intersection = obs
                        local_pos_of_closest = local_pos

        # jeśli nic nie znaleziono
        if closest_intersection is None:
            return pygame.Vector2(0, 0)

        # obliczamy lateral i braking force
        multiplier = 1.0 + (detection_box_length - local_pos_of_closest.x) / detection_box_length
        lateral_force = (closest_intersection.radius - local_pos_of_closest.y) * multiplier
        braking_force = (closest_intersection.radius - local_pos_of_closest.x) * self.braking_weight

        steering_local = pygame.Vector2(braking_force, lateral_force)
        steering_world = local_to_world(steering_local, self.agent.heading, self.agent.side)
        return steering_world

    def create_feelers(self):
        """Tworzy 3 feelery: środkowy, lewy i prawy"""
        length = self.feeler_length
        heading = self.agent.heading
        side = self.agent.side
        pos = self.agent.pos

        # centralny feeler
        self.feelers[0] = pos + heading * length
        # lewy
        self.feelers[1] = pos + (heading.rotate(30)) * length * 0.8
        # prawy
        self.feelers[2] = pos + (heading.rotate(-30)) * length * 0.8

    def wall_avoidance(self, walls):
        """
        walls: lista obiektów Wall, które mają:
            - from_pos (pygame.Vector2) początek
            - to_pos (pygame.Vector2) koniec
            - normal (pygame.Vector2) normalna
        Zwraca wektor siły sterującej
        """
        self.create_feelers()
        steering_force = pygame.Vector2(0, 0)
        closest_dist = float('inf')
        closest_wall = None
        closest_point = None
        feeler_index = 0

        for i, feeler in enumerate(self.feelers):
            for wall in walls:
                # prosta funkcja przecięcia linii
                intersect, point = self.line_intersection(self.agent.pos, feeler, wall.from_pos, wall.to_pos)
                if intersect:
                    dist = (point - self.agent.pos).length()
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_wall = wall
                        closest_point = point
                        feeler_index = i

        if closest_wall:
            overshoot = self.feelers[feeler_index] - closest_point
            steering_force = closest_wall.normal * overshoot.length()

        return steering_force

    def interpose(self, agent_a, agent_b):
        """
        Agent stara się znaleźć w połowie drogi między agent_a i agent_b,
        przewidując ich przyszłą pozycję.
        """
        # midpoint aktualnych pozycji
        midpoint = (agent_a.pos + agent_b.pos) / 2

        # czas potrzebny naszemu agentowi, aby dotrzeć do midpointu
        to_mid = midpoint - self.agent.pos
        dist = to_mid.length()
        max_speed = self.agent.max_speed
        if max_speed > 0:
            time_to_reach = dist / max_speed
        else:
            time_to_reach = 0

        # przewidywanie przyszłych pozycji agentów
        future_a_pos = agent_a.pos + agent_a.velocity * time_to_reach
        future_b_pos = agent_b.pos + agent_b.velocity * time_to_reach

        # midpoint przyszłych pozycji
        future_midpoint = (future_a_pos + future_b_pos) / 2

        # wektor sterujący przy użyciu Arrive (szybkie hamowanie)
        return self.arrive(future_midpoint, deceleration='fast')

    def get_hiding_position(self, obstacle_pos: pygame.Vector2, obstacle_radius: float,
                            target_pos: pygame.Vector2) -> pygame.Vector2:
        to_obstacle = (obstacle_pos - target_pos).normalize()
        dist_away = obstacle_radius + self.distance_from_boundary
        hiding_spot = obstacle_pos + to_obstacle * dist_away
        return hiding_spot

    def hide(self, target, obstacles: list):
        """
        Oblicza siłę sterującą, by ukryć się przed celem.
        """
        best_hiding_spot = None
        dist_to_closest = float('inf')

        for obs in obstacles:
            hiding_spot = self.get_hiding_position(obs.pos, obs.radius, target.pos)
            dist_sq = (hiding_spot - self.agent.pos).length_squared()
            if dist_sq < dist_to_closest:
                dist_to_closest = dist_sq
                best_hiding_spot = hiding_spot

        if best_hiding_spot is None:
            # brak przeszkód – uciekaj od celu
            return self.evade(target)

        # idź do najlepszego punktu ukrycia
        return self.arrive(best_hiding_spot, deceleration='fast')

    def follow_path(self):
        if not self.path or len(self.path) == 0:
            return pygame.Vector2(0, 0)

        # aktualny waypoint
        target = self.path[self.current_waypoint_index]

        # distance squared do waypointu
        dist_sq = (target - self.agent.pos).length_squared()

        # jeśli blisko waypointu, do następnego
        if dist_sq < self.waypoint_seek_radius_sq:
            self.current_waypoint_index += 1
            if self.current_waypoint_index >= len(self.path):
                # jeśli trasa jest zamknięta, wróć do początku
                if getattr(self.path, "closed", False):
                    self.current_waypoint_index = 0
                else:
                    self.current_waypoint_index = len(self.path) - 1  # ostatni punkt

            target = self.path[self.current_waypoint_index]

        # jeśli jesteśmy w ostatnim punkcie trasy otwartej - arrive
        if self.current_waypoint_index == len(self.path) - 1 and not getattr(self.path, "closed", False):
            return self.arrive(target, deceleration='normal')
        else:
            # w przeciwnym razie - seek
            return self.seek(target)

    def offset_pursuit(self, leader, offset: pygame.Vector2):
        """
            Utrzymuje agenta w określonym przesunięciu względem lidera.
            :param leader: agent do podążania
            :param offset: Pozycja przesunięcia w przestrzeni lokalnej lidera (pygame.Vector2)
            :return: Steering force (pygame.Vector2)
        """
        # offset w przestrzeni świata
        world_offset_pos = leader.pos + leader.heading * offset.x + leader.side * offset.y

        # wektor do offsetu
        to_offset = world_offset_pos - self.agent.pos

        # przewidywanie pozycji
        look_ahead_time = to_offset.length() / (self.agent.max_speed + leader.velocity.length())

        # przewidywana przyszła pozycja offsetu
        future_pos = world_offset_pos + leader.velocity * look_ahead_time

        # arrive do przewidywanej pozycji
        return self.arrive(future_pos, deceleration='fast')

    def separation(self, neighbors):
        """
        Oblicza siłę separacji względem sąsiadów.c
        """
        if not neighbors:
            return pygame.Vector2()

        steering_force = pygame.Vector2(0, 0)

        for other in neighbors:
            to = self.agent.pos - other.pos
            dist = to.length()

            if dist > 0:
                steering_force += to.normalize() / dist  # im bliżej, tym silniejsze odpychanie

        return steering_force

    def alignment(self):
        """
        Steering: ALIGNMENT
        Zwraca wektor kierujący agenta tak, aby wyrównał kierunek
        do średniego kierunku swoich sąsiadów.
        """
        neighbors = self.agent.neighbors

        if not neighbors:
            return pygame.Vector2(0, 0)

        # sredni heading sąsiadów
        avg_heading = pygame.Vector2(0, 0)
        count = 0

        for other in neighbors:
            if other is self.agent:
                continue
            avg_heading += other.heading
            count += 1

        if count == 0:
            return pygame.Vector2(0, 0)

        avg_heading /= count

        steering = avg_heading - self.agent.heading

        return steering

    def cohesion(self, neighbors):
        """
        Zwraca siłę steering przyciągającą agenta do środka masy jego sąsiadów.
        """
        if not neighbors:
            return pygame.Vector2(0, 0)

        # środek masy sąsiadów
        center_of_mass = pygame.Vector2(0, 0)
        for neighbor in neighbors:
            center_of_mass += neighbor.pos
        center_of_mass /= len(neighbors)

        # Wektor kierunku do środka masy (seek)
        desired_velocity = (center_of_mass - self.agent.pos).normalize() * self.agent.max_speed
        steering_force = desired_velocity - self.agent.velocity

        # ograniczamy siłę do max_force
        if steering_force.length() > self.agent.max_force:
            steering_force.scale_to_length(self.agent.max_force)

        return steering_force


    @staticmethod
    def line_intersection(p1, p2, q1, q2):
        r = p2 - p1
        s = q2 - q1
        denominator = r.cross(s)
        if denominator == 0:
            return False, None  # równoległe

        t = (q1 - p1).cross(s) / denominator
        u = (q1 - p1).cross(r) / denominator

        if 0 <= t <= 1 and 0 <= u <= 1:
            intersection_point = p1 + r * t
            return True, intersection_point
        return False, None