import unittest

import numpy as np

from maths._poly_decomp import _convex_decomp


class ConvexDecompTest(unittest.TestCase):
    H_SHAPE_VERTICES = [
        [100, 100],
        [600, 100],
        [600, 300],
        [500, 300],
        [500, 500],
        [700, 500],
        [700, 800],
        [0, 800],
        [0, 600],
        [200, 600],
        [200, 200],
        [100, 200],
    ]

    RECT_SHAPE_VERTICES = [
        [100, 100],
        [200, 100],
        [200, 200],
        [100, 200]
    ]

    L_SHAPE_VERTICES = [
        [100, 100],
        [300, 100],
        [300, 200],
        [200, 200],
        [200, 300],
        [100, 300]
    ]

    @staticmethod
    def polygon_equals(vertices1, vertices2):
        if len(vertices1) != len(vertices2):
            return False
        return np.all(np.in1d(vertices1, vertices2)) and np.all(np.in1d(vertices2, vertices1))

    @staticmethod
    def list_contains(arr, searched, equals):
        for element in arr:
            if equals(element, searched):
                return True
        return False

    @staticmethod
    def are_vertices_unique(vertices):
        for index, vertex in enumerate(vertices):
            if index < len(vertices) - 1:
                continue
            if vertex in vertices[index + 1:]:
                return False
        return True

    def test_h_completion(self):
        polys = _convex_decomp(self.H_SHAPE_VERTICES)

        result1 = [[700, 800], [0, 800], [0, 600], [200, 600]]
        result2 = [[500, 500], [700, 500], [700, 800], [200, 600]]
        result3 = [[200, 200], [100, 200], [100, 100]]
        result4 = [[500, 300], [500, 500], [200, 600], [200, 200]]
        result5 = [[200, 200], [100, 100], [600, 100], [600, 300], [500, 300]]

        self.assertTrue(self.list_contains(polys, result1, self.polygon_equals))
        self.assertTrue(self.list_contains(polys, result2, self.polygon_equals))
        self.assertTrue(self.list_contains(polys, result3, self.polygon_equals))
        self.assertTrue(self.list_contains(polys, result4, self.polygon_equals))
        self.assertTrue(self.list_contains(polys, result5, self.polygon_equals))

    def test_h_unique_vertices(self):
        polys = _convex_decomp(self.H_SHAPE_VERTICES)
        for poly in polys:
            self.assertTrue(self.are_vertices_unique(poly))

    def test_l_completion(self):
        polys = _convex_decomp(self.L_SHAPE_VERTICES)

        result1 = [[100, 100], [300, 100], [300, 200], [200, 200]]
        result2 = [[100, 100], [200, 200], [200, 300], [100, 300]]

        self.assertTrue(self.list_contains(polys, result1, self.polygon_equals))
        self.assertTrue(self.list_contains(polys, result2, self.polygon_equals))

    def test_l_unique_vertices(self):
        polys = _convex_decomp(self.L_SHAPE_VERTICES)
        for poly in polys:
            self.assertTrue(self.are_vertices_unique(poly))

    def test_rect_completion(self):
        polys = _convex_decomp(self.RECT_SHAPE_VERTICES)
        self.assertTrue(self.list_contains(polys, self.RECT_SHAPE_VERTICES, self.polygon_equals))

    def test_rect_unique_vertices(self):
        polys = _convex_decomp(self.RECT_SHAPE_VERTICES)
        for poly in polys:
            self.assertTrue(self.are_vertices_unique(poly))


if __name__ == '__main__':
    unittest.main()
