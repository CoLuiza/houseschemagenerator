import numpy as np

from maths._transform import Transform


class AbstractPolygon:
    def get_points(self):
        pass


class Polygon(AbstractPolygon):
    def __init__(self, vertices):
        self._vertices = np.array(vertices)

    def get_points(self):
        return self._vertices


class Rect(AbstractPolygon):
    def __init__(self, width, height, transform=None):
        self.width = width
        self.height = height
        if transform is not None:
            self.transform = transform
        else:
            self.transform = Transform()

    def get_points(self, max_depth=-1):
        points = np.array([
            [0, 0],
            [0, self.height],
            [self.width, self.height],
            [self.width, 0]
        ])

        if max_depth == -1:
            transform = self.transform
            while transform is not None:
                points = transform.apply(points)
                transform = transform.parent_transform
        else:
            transform = self.transform
            while transform is not None and max_depth > 0:
                points = transform.apply(points)
                transform = transform.parent_transform
                max_depth -= 1

        return points
