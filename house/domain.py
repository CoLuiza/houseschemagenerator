from config.directions import Direction
from config.globals import factor
from maths.domain import Polygon
from maths.service import convex_decomposition


def make_blocker(points, orientation):
    if orientation == Direction.LEFT:
        min_y = min(points[0][1], points[1][1], points[2][1])
        xs = (min(points[0][0], points[1][0], points[2][0]), max(points[0][0], points[1][0], points[2][0]))
        blocker = Blocker(
            (
                (xs[0], (min_y - factor)),
                (xs[1], (min_y - factor)),
                (xs[1], min_y),
                (xs[0], min_y),
            ),
            orientation
        )
    elif orientation == Direction.RIGHT:
        max_y = max(points[0][1], points[1][1], points[2][1])
        xs = (min(points[0][0], points[1][0], points[2][0]), max(points[0][0], points[1][0], points[2][0]))
        blocker = Blocker(
            (
                (xs[0], (max_y + factor)),
                (xs[0], max_y),
                (xs[1], max_y),
                (xs[1], (max_y + factor)),
            ),
            orientation
        )
    elif orientation == Direction.UP:
        min_x = min(points[0][0], points[1][0], points[2][0])
        ys = (min(points[0][1], points[1][1], points[2][1]), max(points[0][1], points[1][1], points[2][1]))
        blocker = Blocker(
            (
                ((min_x - factor), ys[0]),
                (min_x, ys[0]),
                (min_x, ys[1]),
                ((min_x - factor), ys[1]),
            ),
            orientation
        )
    else:
        max_x = max(points[0][0], points[1][0], points[2][0])
        ys = (min(points[0][1], points[1][1], points[2][1]), max(points[0][1], points[1][1], points[2][1]))
        blocker = Blocker(
            (
                ((max_x + factor), ys[0]),
                (max_x, ys[0]),
                (max_x, ys[1]),
                ((max_x + factor), ys[1]),
            ),
            orientation
        )
    return blocker


class Structure:
    def __init__(self, points, orientation):
        self.poly = Polygon(points)
        self.orientation = orientation
        self.points = points


class Blocker(Structure):
    def __init__(self, points, orientation):
        super().__init__(points, orientation)


class Wall(Structure):
    def __init__(self, points, orientation, inner_margin):
        super().__init__(points, orientation)
        self.inner_margin = inner_margin


class Window(Structure):
    def __init__(self, points, orientation, inner_margin):
        super().__init__(points, orientation)
        self.blocker = make_blocker(points, orientation)
        self.inner_margin = inner_margin
        self.img = None


class Door(Structure):
    def __init__(self, points, orientation, inner_margin):
        super().__init__(points, orientation)
        self.points = points
        self.blocker = make_blocker(points, orientation)
        self.inner_margin = inner_margin
        self.img = None


class House:
    def __init__(self, rooms, width, height):
        self.rooms = rooms
        self.width = width
        self.height = height


class Furniture(Structure):
    def __init__(self, points, orientation, img, furniture_type, is_tall=False):
        super().__init__(points, orientation)
        self.is_tall = is_tall
        self.img = img
        self.type = furniture_type


class Room(Structure):
    def __init__(self, id, origin, farthest_point, walls, doors, windows, area, points, orientation):
        super().__init__(points, orientation)
        self.walls = walls
        self.doors = doors
        self.windows = windows
        self.origin = origin
        self.area = area
        self.farthest_point = farthest_point
        self.type = None
        self.connected_rooms = set()
        self.id = id
        self.points = points
        self.blockers = list()
        self.decomposed_parts = list()
        self.furniture = list()

    def _convex_decompose(self):
        self.decomposed_parts = convex_decomposition(self.poly)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
