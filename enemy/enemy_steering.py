import pygame

def accumulate_force(enemy, running_total, force_to_add):
    magnitude_so_far = running_total.length()
    remaining = enemy.max_force - magnitude_so_far

    if remaining <= 0:
        return running_total, False

    to_add_length = force_to_add.length()
    if to_add_length < remaining:
        running_total += force_to_add
    else:
        running_total += force_to_add.normalize() * remaining

    return running_total, True

def calculate_steering(enemy, dt, player, game_map):
    steering = pygame.Vector2(0, 0)
    force = pygame.Vector2(0, 0)
    ok = True

    # Hide
    if player is not None:
        force = enemy.steering.hide(player, game_map.obstacles) * 10
        steering, ok = accumulate_force(enemy, steering, force)

    # Wall Avoidance
    force = enemy.steering.wall_avoidance(game_map.walls) * 10
    steering, ok = accumulate_force(enemy, steering, force)
    if not ok: return steering

    # Obstacle Avoidance
    force = enemy.steering.obstacle_avoidance(game_map.obstacles) * 10
    steering, ok = accumulate_force(enemy, steering, force)
    if not ok: return steering

    # Separation
    if enemy.neighbors:
        force = enemy.steering.separation(enemy.neighbors) * 18000
        steering, ok = accumulate_force(enemy, steering, force)
        if not ok: return steering

    # Alignment
    if enemy.neighbors:
        force = enemy.steering.alignment() * 200
        steering, ok = accumulate_force(enemy, steering, force)
        if not ok: return steering

    # Cohesion
    if enemy.neighbors:
        force = enemy.steering.cohesion(enemy.neighbors) * 0.1
        steering, ok = accumulate_force(enemy, steering, force)
        if not ok: return steering

    # Wander
    force = enemy.steering.wander(dt) * 3.5
    steering, ok = accumulate_force(enemy, steering, force)
    if not ok: return steering



    return steering