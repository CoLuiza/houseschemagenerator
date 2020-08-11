import time

from PIL import Image, ImageDraw
from numpy import random

from maths.domain import Polygon, Rect
from maths.service import convex_decomposition, check_collision_concave

H_SHAPE_VERTICES = [
    [100, 100],
    [300, 100],
    [300, 200],
    [200, 200],
    [200, 300],
    [100, 300]
]


def drawable_points(np_points):
    return list(np_points.ravel())


def random_color():
    levels = range(32, 256, 32)
    return tuple(random.choice(levels) for _ in range(3))


def generate_rect():
    size_range = range(50, 300, 10)
    position_range = range(0, 800, 10)
    width = random.choice(size_range)
    height = random.choice(size_range)
    x = random.choice(position_range)
    y = random.choice(position_range)
    rect = Rect(width, height)
    rect.transform.position = [x, y]

    return rect


def generate_rects(n):
    for i in range(n):
        yield generate_rect()


def map_rect(rect, concave_polygon):
    if check_collision_concave(concave_polygon, rect):
        return rect, '#FF222288'
    return rect, '#44444488'


if __name__ == '__main__':
    im = Image.new('RGB', (1000, 1000), '#CCCCCC')
    draw = ImageDraw.Draw(im)

    polygon = Polygon(H_SHAPE_VERTICES)
    convex_polys = convex_decomposition(polygon)

    for poly in convex_polys:
        draw.polygon(drawable_points(poly.get_points()), fill=random_color())

    start_time = time.time()

    rect_tuples = list(map(lambda x: map_rect(x, convex_polys), generate_rects(10)))

    elapsed_time = time.time() - start_time

    print(elapsed_time)
    for rect, color in rect_tuples:
        draw.polygon(drawable_points(rect.get_points()), fill=color)

    im.show()
