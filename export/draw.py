from PIL import Image
from PIL.ImageDraw import Draw

from config.globals import factor
from export.image import format_image, draw_onto
from house.domain import House


def transform_point(point, origin):
    return (point[0] + origin[0]), (point[1] + origin[1])


def draw_room_debug(draw, room):
    origin = room.origin
    for wall in room.walls:
        final_polygon_points = [transform_point((point[0], point[1]), origin) for point in
                                wall.points]
        draw.polygon(final_polygon_points, fill="black")
        # draw.polygon(wall.inner_margin, fill="gray")
    for window in room.windows:
        final_polygon_points = [transform_point((point[0], point[1]), origin) for point in
                                window.points]
        draw.polygon(final_polygon_points, fill="blue")
        final_blocker_points = [transform_point((point[0], point[1]), origin) for point in
                                window.blocker.points]
        draw.polygon(final_blocker_points, fill="yellow")
        # draw.polygon(window.inner_margin, fill="yellow")
    for door in room.doors:
        final_polygon_points = [transform_point((point[0], point[1]), origin) for point in
                                door.points]
        final_blocker_points = [transform_point((point[0], point[1]), origin) for point in
                                door.blocker.points]
        draw.polygon(final_polygon_points, fill="red")
        draw.polygon(final_blocker_points, fill="brown")
    for obj in room.furniture:
        final_polygon_points = [transform_point((point[0], point[1]), origin) for point in
                                obj.points]
        if obj.type == "stove":
            draw.polygon(final_polygon_points, fill="green")
        else:
            draw.polygon(final_polygon_points, fill="orange")


def draw_room_shadow(room):
    img = Image.new(mode="RGBA",
                    size=(room.farthest_point[0] - room.origin[0],
                          room.farthest_point[1] - room.origin[1],),
                    color=(112, 112, 112, 255))

    draw = Draw(img, mode="RGBA")
    draw.polygon(room.points, fill="black")

    img.save("room_shadow.png", "png")


def draw_room(draw, image, room):
    origin = room.origin
    for wall in room.walls:
        final_polygon_points = [transform_point((point[0], point[1]), origin) for point in
                                wall.points]
        draw.polygon(final_polygon_points, fill=(71, 71, 71, 255))
    for window in room.windows:
        final_polygon_points = [transform_point((point[0], point[1]), origin) for point in
                                window.points]
        if window.img:
            img, min_point = format_image(final_polygon_points, window.orientation, window.img)
            draw_onto(image, img, min_point)
        else:
            draw.polygon(final_polygon_points, fill="blue")

    for door in room.doors:
        final_polygon_points = [transform_point((point[0], point[1]), origin) for point in
                                door.points]
        if door.img:
            img, min_point = format_image(final_polygon_points, door.orientation, door.img)
            draw_onto(image, img, min_point)
        else:
            draw.polygon(final_polygon_points, fill="red")
    for obj in room.furniture:
        final_polygon_points = [transform_point((point[0], point[1]), origin) for point in
                                obj.points]
        img, min_point = format_image(final_polygon_points, obj.orientation, obj.img)
        draw_onto(image, img, min_point)


def draw_house(house: House, path):
    img = Image.new(mode="RGBA",
                    size=(house.width,
                          house.height,),
                    color=(64, 116, 64, 255))
    draw = Draw(img, mode="RGBA")
    for room in house.rooms:
        points = [transform_point((point[0], point[1]), room.origin) for point in
                  room.points]
        draw.polygon(points, fill=(112, 112, 112, 255))
        draw_room(draw, img, room)
    img.save(f"{path}house.png", "PNG")
