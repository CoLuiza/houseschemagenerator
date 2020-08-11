import numpy as np

from maths.domain import AbstractPolygon


def _check_collision(poly1: AbstractPolygon, poly2: AbstractPolygon):
    p1 = poly1.get_points()
    p2 = poly2.get_points()

    edges = _edges_of(p1)
    edges += _edges_of(p2)
    normals = [_normal(e) for e in edges]

    for o in normals:
        separates = _is_separating_axis(o, p1, p2)
        if separates:
            return False

    return True


def _edges_of(vertices):
    edges = []
    n = len(vertices)
    for i in range(n):
        edge = vertices[(i + 1) % n] - vertices[i]
        edges.append(edge)

    return edges


def _normal(v):
    return np.array([-v[1], v[0]])


def _is_separating_axis(o, p1, p2):
    min1, max1 = float('+inf'), float('-inf')
    min2, max2 = float('+inf'), float('-inf')

    for v in p1:
        projection = np.dot(v, o)

        min1 = min(min1, projection)
        max1 = max(max1, projection)

    for v in p2:
        projection = np.dot(v, o)

        min2 = min(min2, projection)
        max2 = max(max2, projection)

    if max1 >= min2 and max2 >= min1:
        return False
    return True
