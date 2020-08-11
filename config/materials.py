from enum import Enum


class Material(Enum):
    BLANK = 0
    WALL = 1
    DOOR = 2
    WINDOW = 3

    MARKED = 4


STRUCTURES = [Material.WALL, Material.DOOR, Material.WINDOW]
