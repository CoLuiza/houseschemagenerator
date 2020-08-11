import numpy as np


def _line_int(l1, l2, precision=0):
    """Compute the intersection between two lines.
    Keyword arguments:
    l1 -- first line
    l2 -- second line
    precision -- precision to check if lines are parallel (default 0)
    Returns:
    The intersection point
    """
    i = [0, 0]  # point
    a1 = l1[1][1] - l1[0][1]
    b1 = l1[0][0] - l1[1][0]
    c1 = a1 * l1[0][0] + b1 * l1[0][1]
    a2 = l2[1][1] - l2[0][1]
    b2 = l2[0][0] - l2[1][0]
    c2 = a2 * l2[0][0] + b2 * l2[0][1]
    det = a1 * b2 - a2 * b1
    if not _scalar_eq(det, 0, precision):  # lines are not parallel
        i[0] = (b2 * c1 - b1 * c2) / det
        i[1] = (a1 * c2 - a2 * c1) / det
    return i


def _line_segment_intersects(p1, p2, q1, q2):
    """Checks if two line segments intersect.
    Keyword arguments:
    p1 -- The start vertex of the first line segment.
    p2 -- The end vertex of the first line segment.
    q1 -- The start vertex of the second line segment.
    q2 -- The end vertex of the second line segment.
    Returns:
    True if the two line segments intersect
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    da = q2[0] - q1[0]
    db = q2[1] - q1[1]

    # segments are parallel
    if (da * dy - db * dx) == 0:
        return False

    s = (dx * (q1[1] - p1[1]) + dy * (p1[0] - q1[0])) / (da * dy - db * dx)
    t = (da * (p1[1] - q1[1]) + db * (q1[0] - p1[0])) / (db * dx - da * dy)

    return 0 <= s <= 1 and 0 <= t <= 1


def _triangle_area(a, b, c):
    """Calculates the area of a triangle spanned by three points.
    Note that the area will be negative if the points are not given in counter-clockwise order.
    Keyword arguments:
    a -- First point
    b -- Second point
    c -- Third point
    Returns:
    Area of triangle
    """
    return ((b[0] - a[0]) * (c[1] - a[1])) - ((c[0] - a[0]) * (b[1] - a[1]))


def _is_left_on(a, b, c):
    return _triangle_area(a, b, c) >= 0


def _is_right(a, b, c):
    return _triangle_area(a, b, c) < 0


def _is_right_on(a, b, c):
    return _triangle_area(a, b, c) <= 0


def _square_dist(a, b):
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    return dx * dx + dy * dy


def _polygon_at(polygon, i):
    """Gets a vertex at position i on the polygon.
    It does not matter if i is out of bounds.
    Keyword arguments:
    polygon -- The polygon
    i -- Position desired on the polygon
    Returns:
    Vertex at position i
    """
    s = len(polygon)
    return polygon[i % s]


def _vertex_is_reflex(polygon, i):
    """Checks if a point in the polygon is a reflex point.
    Keyword arguments:
    polygon -- The polygon
    i -- index of point to check
    Returns:
    True is point is a reflex point
    """
    return _is_right(_polygon_at(polygon, i - 1), _polygon_at(polygon, i), _polygon_at(polygon, i + 1))


def _polygon_can_see(polygon, a, b):
    """Checks if two vertices in the polygon can see each other.
    Keyword arguments:
    polygon -- The polygon
    a -- Vertex 1
    b -- Vertex 2
    Returns:
    True if vertices can see each other
    """

    l1 = [None] * 2
    l2 = [None] * 2

    if _is_left_on(_polygon_at(polygon, a + 1), _polygon_at(polygon, a), _polygon_at(polygon, b)) \
            and _is_right_on(_polygon_at(polygon, a - 1), _polygon_at(polygon, a), _polygon_at(polygon, b)):
        return False

    dist = _square_dist(_polygon_at(polygon, a), _polygon_at(polygon, b))
    for i in range(len(polygon)):  # for each edge
        if (i + 1) % len(polygon) == a or i == a:  # ignore incident edges
            continue

        if _is_left_on(_polygon_at(polygon, a), _polygon_at(polygon, b), _polygon_at(polygon, i + 1)) and _is_right_on(
                _polygon_at(polygon, a), _polygon_at(polygon, b), _polygon_at(polygon, i)):  # if diag intersects an edge
            l1[0] = _polygon_at(polygon, a)
            l1[1] = _polygon_at(polygon, b)
            l2[0] = _polygon_at(polygon, i)
            l2[1] = _polygon_at(polygon, i + 1)
            p = _line_int(l1, l2)
            if _square_dist(_polygon_at(polygon, a), p) < dist:  # if edge is blocking visibility to b
                return False

    return True


def _get_sub_polygon(vertices, i, j):
    """Copies the polygon from vertex i to vertex j to targetPoly.
    Keyword arguments:
    polygon -- The source polygon
    i -- start vertex
    j -- end vertex (inclusive)
    targetPoly -- Optional target polygon
    Returns:
    The resulting copy.
    """
    if i < j:
        return vertices[i:j + 1]
    return vertices[i:] + vertices[:j + 1]


def _polygon_contains_points(vertices, points):
    return np.all(np.in1d(points, vertices))


def _polygon_slice(vertices, cut_edges):
    result = [vertices]

    for edge in cut_edges:
        for poly in result:
            if _polygon_contains_points(poly, edge):
                x = poly.index(edge[0])
                y = poly.index(edge[1])

                if x > y:
                    x, y = y, x

                left = poly[x:y + 1]
                right = poly[y:] + poly[:x + 1]

                result.remove(poly)
                result.append(left)
                result.append(right)
                break

    return result


def _polygon_is_simple(polygon):
    """Checks that the line segments of this polygon do not intersect each other.
    Keyword arguments:
    polygon -- The polygon
    Returns:
    True is polygon is simple (not self-intersecting)
    Todo:
    Should it check all segments with all others?
    """
    path = polygon
    # Check
    for i in range(len(path) - 1):
        for j in range(i - 1):
            if _line_segment_intersects(path[i], path[i + 1], path[j], path[j + 1]):
                return False

    # Check the segment between the last and the first point to all others
    for i in range(len(path) - 2):
        if _line_segment_intersects(path[0], path[len(path) - 1], path[i], path[i + 1]):
            return False

    return True


def _scalar_eq(a, b, precision=0):
    """Check if two scalars are equal.
    Keyword arguments:
    a -- first scalar
    b -- second scalar
    precision -- precision to check equality
    Returns:
    True if scalars are equal
    """
    return abs(a - b) <= precision


def _get_edges_to_be_cut(vertices):
    """Decomposes the polygon into convex pieces.
    Note that this algorithm has complexity O(N^4) and will be very slow for polygons with many vertices.
    Keyword arguments:
    polygon -- The polygon
    Returns:
    A list of edges [[p1,p2],[p2,p3],...] that cut the polygon.
    """
    result = []
    min_cut_edges_count = float('inf')

    for i in range(len(vertices)):
        if _vertex_is_reflex(vertices, i):
            for j in range(len(vertices)):
                if _polygon_can_see(vertices, i, j):
                    left = _get_edges_to_be_cut(_get_sub_polygon(vertices, i, j))
                    right = _get_edges_to_be_cut(_get_sub_polygon(vertices, j, i))
                    combined = left + right

                    if len(combined) < min_cut_edges_count:
                        min_cut_edges_count = len(combined)
                        result = combined + [[vertices[i], vertices[j]]]

    return result


def _convex_decomp(vertices):
    """Decomposes the polygon into one or more convex sub-polygons.
    Keyword arguments:
    polygon -- The polygon
    Returns:
    An array or polygon objects.
    """
    edges_to_be_cut = _get_edges_to_be_cut(vertices)
    if len(edges_to_be_cut) > 0:
        return _polygon_slice(vertices, edges_to_be_cut)
    else:
        return [vertices]
