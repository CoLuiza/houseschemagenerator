import unittest

import numpy as np

from maths.domain import AbstractPolygon


class PolygonTest(unittest.TestCase):
    SIMPLE_CCW_POLYGON_POINTS = np.array([
        [5, 0],
        [6, 4],
        [4, 5],
        [1, 5],
        [1, 0]
    ])
    SIMPLE_CW_POLYGON_POINTS = np.flipud(SIMPLE_CCW_POLYGON_POINTS)

    FAR_CCW_POLYGON_POINTS = np.array([
        [126, 14],
        [168, -27],
        [175, -20],
        [133, 21]
    ])
    FAR_CW_POLYGON_POINTS = np.flipud(FAR_CCW_POLYGON_POINTS)

    def test_simple_ccw(self):
        self.assertTrue(AbstractPolygon.are_ccw(self.SIMPLE_CCW_POLYGON_POINTS))

    def test_simple_cw(self):
        self.assertFalse(AbstractPolygon.are_ccw(self.SIMPLE_CW_POLYGON_POINTS))

    def test_far_ccw(self):
        self.assertTrue(AbstractPolygon.are_ccw(self.FAR_CCW_POLYGON_POINTS))

    def test_far_cw(self):
        self.assertFalse(AbstractPolygon.are_ccw(self.FAR_CW_POLYGON_POINTS))


if __name__ == '__main__':
    unittest.main()
