from PIL import Image

from config.directions import Direction


def format_image(points, orientation, path):
    img = Image.open(path)
    min_point = (min([x for x, y in points]), min([y for x, y in points]))
    height = max([y for x, y in points]) - min_point[1]
    width = max([x for x, y in points]) - min_point[0]
    if orientation == Direction.RIGHT:
        img = img.rotate(180, expand=True)
    elif orientation == Direction.DOWN:
        img =img.rotate(270, expand=True)
    elif orientation == Direction.UP:
        img = img.rotate(90, expand=True)
    img = img.resize((int(width), int(height)))
    return img, min_point


def draw_onto(image, image_to_draw, point):
    image.paste(image_to_draw, (int(point[0]), int(point[1])))
