import math
from typing import List

from maths._ccw import _are_points_ccw
from maths._collisions import _check_collision
from maths.domain import AbstractPolygon, Polygon
from maths._poly_decomp import _convex_decomp


def convex_decomposition(polygon: AbstractPolygon):
    vertices = polygon.get_points().tolist()
    polygon_vertices_list = _convex_decomp(vertices)
    return [Polygon(vertices) for vertices in polygon_vertices_list]


def check_collision(polygon_a: AbstractPolygon, polygon_b: AbstractPolygon):
    return _check_collision(polygon_a, polygon_b)


def check_collision_concave(polygon_concave: List[AbstractPolygon], polygon_convex: AbstractPolygon):
    for poly in polygon_concave:
        if check_collision(poly, polygon_convex):
            return True
    return False


def are_points_ccw(points):
    return _are_points_ccw(points)


def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

