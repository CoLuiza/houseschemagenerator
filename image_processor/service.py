import logging
from config.globals import factor

from PIL import Image

from config.convertor import pixel_to_material, material_to_class
from config.directions import Direction
from config.materials import Material, STRUCTURES
from house.domain import Room, House
from house.service import set_connected_rooms
from utils.domain import Matrix


class Processor:
    def __init__(self, path):
        self._image = None
        self._logger = logging.getLogger(__name__)
        self._load_image(path)

    def _load_image(self, path):
        if self._image is not None:
            self._logger.debug(f"Load a new image ({path}) overriding the last one...")
        self._image = Image.open(path)
        self._loaded_image = self._image.load()
        self._logger.debug(f"Loading {path}")

    def _image_to_schema(self):
        schema = Matrix(self._image.height, self._image.width, Material.BLANK)
        for i in range(self._image.width):
            for j in range(self._image.height):
                schema.set(i, j, pixel_to_material(self._loaded_image[i, j]))
        return schema

    def get_house(self):
        rooms = list()
        schema = self._image_to_schema()
        visited = Matrix(self._image.height, self._image.width)
        room = Matrix(self._image.height, self._image.width, Material.BLANK)
        self._logger.debug("Marking the outdoor...")
        self._dfs(schema, room, 0, 0, Material.MARKED, visited)
        id = 1
        for i in range(self._image.width):
            for j in range(self._image.height):
                if schema.get(i, j) == Material.BLANK:
                    self._logger.debug("Marking room...")
                    visited = Matrix(self._image.height, self._image.width)
                    room = Matrix(self._image.height, self._image.width, Material.BLANK)
                    area = self._dfs(schema, room, i, j, Material.MARKED, visited)
                    self._border_room(room, schema)
                    origin, farthest_point = self._get_origin_and_farthest_point(room)
                    structures, room_points = self._get_structures(room, origin)
                    rooms.append(
                        Room(
                            id,
                            origin,
                            farthest_point,
                            structures.get(Material.WALL, list()),
                            structures.get(Material.DOOR, list()),
                            structures.get(Material.WINDOW, list()),
                            area,
                            room_points,
                            Direction.UP,
                        )
                    )
                    id += 1
        rooms = set_connected_rooms(rooms)
        house = House(rooms=rooms, height=self._image.height * factor, width=self._image.width * factor)
        return house

    def _dfs(self, schema, room, i, j, block_type, visited):
        stack = []
        first = True
        height = self._image.height
        width = self._image.width
        room_area = 0
        while stack or first:
            if visited.get(i, j) == 0 and schema.get(i, j) == Material.BLANK:
                visited.set(i, j, 1)
                room_area += 1
                room.set(i, j, Material.MARKED)
                schema.set(i, j, block_type)
                if i > 0:
                    stack.append((schema, room, i - 1, j, block_type, visited))
                if i < width - 1:
                    stack.append((schema, room, i + 1, j, block_type, visited))
                if j > 0:
                    stack.append((schema, room, i, j - 1, block_type, visited))
                if j < height - 1:
                    stack.append((schema, room, i, j + 1, block_type, visited))
                first = False
            try:
                schema, room, i, j, block_type, visited = stack.pop()
            except:
                raise BadHouseSchema("The house schema isn't valid")
        return room_area

    def _border_room(self, room, schema):
        for i in range(self._image.width):
            for j in range(self._image.height):
                if room.get(i, j) == Material.BLANK and Material.MARKED in self._get_neighbors(i, j, room):
                    room.set(i, j, schema.get(i, j))

    def _get_origin_and_farthest_point(self, bordered_room):
        origin_x, origin_y = self._image.width, self._image.height
        far_point_x, far_point_y = 0, 0
        for x in range(self._image.width):
            for y in range(self._image.height):
                if bordered_room.get(x, y) in STRUCTURES:
                    if origin_x > x:
                        origin_x = x
                    if origin_y > y:
                        origin_y = y
                    if far_point_x < x:
                        far_point_x = x
                    if far_point_y < y:
                        far_point_y = y
        return (origin_x * factor, origin_y * factor), (far_point_x * factor, far_point_y * factor)

    @staticmethod
    def _get_neighbors(i, j, matrix):
        neighbors = list()
        neighbors_index = [
            (i - 1, j - 1),
            (i, j - 1),
            (i - 1, j),
            (i + 1, j),
            (i, j + 1),
            (i + 1, j + 1),
            (i + 1, j - 1),
            (i - 1, j + 1),
        ]
        for index in neighbors_index:
            try:
                neighbors.append(matrix.get(index[0], index[1]))
            except IndexError:
                continue
        return neighbors

    def _get_structures(self, bordered_room, origin):

        result = {
            Material.WALL: list(),
            Material.WINDOW: list(),
            Material.DOOR: list()
        }

        secondary_direction = {
            Direction.LEFT: [Direction.UP, Direction.DOWN],
            Direction.RIGHT: [Direction.UP, Direction.DOWN],
            Direction.UP: [Direction.LEFT, Direction.RIGHT],
            Direction.DOWN: [Direction.LEFT, Direction.RIGHT],
        }
        corner_i, corner_j = None, None
        for i in range(bordered_room.width):
            for j in range(bordered_room.height):
                if bordered_room.get(i, j) in STRUCTURES:
                    corner_i, corner_j = i, j
                    break
            if corner_i is not None:
                break
        if corner_i is None:
            raise BadHouseSchema("No corner found.")

        room_points = [(corner_i * factor - origin[0], corner_j * factor - origin[1])]

        point_i, point_j = corner_i, corner_j
        direction = Direction.RIGHT
        try:
            bordered_room.get(corner_i + 1, corner_j)
        except IndexError:
            raise BadHouseSchema("Bad house schema, can't return to the start point")

        first_pass = True
        while (point_i != corner_i or point_j != corner_j) or first_pass:
            primary_direction = direction
            first_pass = False
            current_structure = bordered_room.get(point_i, point_j)
            current_size = 1
            current_position = (point_i, point_j)
            to_save = False
            while direction == primary_direction:
                point_i, point_j, structure = self._move(bordered_room, point_i, point_j, direction)
                if structure:
                    to_save = True
                    if current_structure == structure:
                        current_size += 1
                    else:
                        klass = self._make_structure(current_position, origin,
                                                     current_structure, current_size, direction)
                        result[current_structure].append(klass)
                        current_structure = structure
                        current_size = 1
                        current_position = (point_i, point_j)
                else:
                    self._set_room_points(room_points, origin, point_i, point_j)

                    if to_save:
                        klass = self._make_structure(current_position, origin,
                                                     current_structure, current_size, direction)
                        result[current_structure].append(klass)
                        to_save = False
                    point_i, point_j, structure = self._move(bordered_room, point_i, point_j,
                                                             secondary_direction[direction][0])
                    if structure:
                        direction = secondary_direction[direction][0]
                        break
                    point_i, point_j, structure = self._move(bordered_room, point_i, point_j,
                                                             secondary_direction[direction][1])
                    if structure:
                        direction = secondary_direction[direction][1]

                if point_j == corner_j and point_i == corner_i and not first_pass:
                    klass = self._make_structure(current_position, origin,
                                                 current_structure, current_size, direction)
                    result[current_structure].append(klass)
                    break

        return result, room_points

    def _set_room_points(self, room_points, origin, point_i, point_j):
        room_points.append(
            (point_i * factor - origin[0], (point_j * factor - origin[1])))

    @staticmethod
    def _move(bordered_room, i, j, direction):
        if bordered_room.get(i + direction[0], j + direction[1]) in STRUCTURES:
            return i + direction[0], j + direction[1], bordered_room.get(i + direction[0], j + direction[1])
        return i, j, None

    @staticmethod
    def _make_structure(current_position, origin, current_structure,
                        current_size, direction):

        x_pos = current_position[0] - origin[0] / factor
        y_pos = current_position[1] - origin[1] / factor
        current_size = current_size - 1
        if direction == Direction.DOWN:
            orientation = Direction.LEFT
            point_a = (factor * x_pos, factor * y_pos)
            point_b = (point_a[0] + factor * (current_size + 1), point_a[1])
            point_c = (point_b[0], point_b[1] + factor)
            point_d = (point_a[0], point_c[1])
            inner_margin = (point_a, point_b)

        elif direction == Direction.RIGHT:
            orientation = Direction.DOWN
            point_a = (factor * x_pos, factor * y_pos)
            point_b = (point_a[0] + factor, point_a[1])
            point_c = (point_b[0], point_b[1] + factor * (current_size + 1))
            point_d = (point_a[0], point_c[1])
            inner_margin = (point_b, point_c)

        elif direction == Direction.UP:
            orientation = Direction.RIGHT
            point_a = (factor * (x_pos + 1), factor * y_pos)
            point_b = (point_a[0] - factor * (1 + current_size), point_a[1])
            point_c = (point_b[0], point_b[1] + factor)
            point_d = (point_a[0], point_c[1])
            inner_margin = (point_b, point_a)

        else:
            orientation = Direction.UP
            point_a = (factor * (x_pos + 1), factor * (y_pos + 1))
            point_b = (point_a[0] - factor, point_a[1])
            point_c = (point_b[0], point_b[1] - factor * (1 + current_size))
            point_d = (point_a[0], point_c[1])
            inner_margin = (point_b, point_c)

        klass = material_to_class(current_structure)((point_a, point_b, point_c, point_d), orientation, inner_margin)
        return klass


class BadHouseSchema(Exception):
    pass
