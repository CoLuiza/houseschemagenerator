class Matrix:
    def __init__(self, height, width, default=0):
        self.height = height
        self.width = width
        self.matrix = [[default for _ in range(height)] for _ in range(width)]

    def get(self, i, j):
        try:
            if i < 0 or j < 0:
                return None
            return self.matrix[i][j]
        except IndexError:
            return None

    def set(self, i, j, value):
        self.matrix[i][j] = value
