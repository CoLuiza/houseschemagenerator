from config.materials import Material
from config.room_types import RoomType
from house.domain import Door, Wall, Window


def pixel_to_material(pixel):
    materials = {
        (255, 255, 255): Material.BLANK,
        (255, 0, 0): Material.DOOR,
        (0, 0, 255): Material.WINDOW,
        (0, 0, 0): Material.WALL,
        (255, 255, 255, 255): Material.BLANK,
        (255, 0, 0, 255): Material.DOOR,
        (0, 0, 255, 255): Material.WINDOW,
        (0, 0, 0, 255): Material.WALL,
    }
    return materials.get(pixel) if materials.get(pixel) else Material.BLANK


def material_to_class(material):
    classes = {
        Material.DOOR: Door,
        Material.WALL: Wall,
        Material.WINDOW: Window,
    }
    return classes.get(material) if classes.get(material) else Material.WALL


def json_room_to_room_type(room_name):
    rooms = {
        "kitchen": RoomType.KITCHEN,
        "livingroom": RoomType.LIVINGROOM,
        "bathroom": RoomType.BATHROOM,
        "hall": RoomType.HALL,
        "bedroom": RoomType.BEDROOM,
    }
    return rooms.get(room_name)


def room_type_to_json_room(room_type):
    rooms = {
        RoomType.KITCHEN: "kitchen",
        RoomType.LIVINGROOM: "livingroom",
        RoomType.BATHROOM: "bathroom",
        RoomType.HALL: "hall",
        RoomType.BEDROOM: "bedroom",
    }
    return rooms.get(room_type)
