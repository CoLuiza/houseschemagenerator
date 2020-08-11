import numpy as np


class Transform:
    def __init__(self, parent_transform=None):
        self._position = np.zeros(2)
        self.rotation = 0
        self._scale = np.ones(2)
        self.parent_transform = parent_transform

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = np.array(value)

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = np.array(value)

    def get_rotation_matrix(self):
        c, s = np.cos(self.rotation), np.sin(self.rotation)
        return np.array(((c, -s), (s, c)))

    def get_scale_matrix(self):
        return np.array(((self.scale[0], 0), (0, self.scale[1])))

    def apply(self, points):
        return points.dot(self.get_scale_matrix()).dot(self.get_rotation_matrix()) + self.position
