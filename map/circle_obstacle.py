class CircleObstacle:
    def __init__(self, x: float, y: float, radius: float):
        self.x = x
        self.y = y
        self.radius = radius

    def collides_with(self, other: "CircleObstacle") -> bool:
        dx = self.x - other.x
        dy = self.y - other.y
        distance_sq = dx*dx + dy*dy
        radius_sum = self.radius + other.radius
        return distance_sq < radius_sum * radius_sum