def _are_points_ccw(points):
    val = 0
    for i in range(1, len(points)):
        x2, x1 = points[i, 0], points[i - 1, 0]
        y2, y1 = points[i, 1], points[i - 1, 1]
        val += (x2 - x1) * (y2 + y1)

    val += (points[0, 0] - points[len(points) - 1, 0]) * (points[0, 1] + points[len(points) - 1, 1])
    return val < 0
