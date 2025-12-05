import math

def ray_circle_intersection(px, py, dx, dy, cx, cy, r):
    """
    Ray starting at P(px,py) with direction D(dx,dy)
    Circle centered at C(cx,cy) with radius r
    Returns distance t to nearest intersection or None
    """

    # vector PC
    fx = px - cx
    fy = py - cy

    a = dx*dx + dy*dy
    b = 2 * (fx*dx + fy*dy)
    c = (fx*fx + fy*fy) - r*r

    discriminant = b*b - 4*a*c
    if discriminant < 0:
        return None  # no intersection

    discriminant = math.sqrt(discriminant)

    # two solutions
    t1 = (-b - discriminant) / (2*a)
    t2 = (-b + discriminant) / (2*a)

    # first positive intersection
    t_candidates = [t for t in (t1, t2) if t > 0]

    if not t_candidates:
        return None

    return min(t_candidates)