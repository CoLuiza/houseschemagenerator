import math
import random
from copy import deepcopy
from datetime import datetime

from config.directions import Direction
from config.globals import factor, output_factor
from config.room_types import RoomType
from house.domain import Room, Furniture, House
from house.furniture_manager import FurnitureManager, ConfigurationError
from maths.service import check_collision_concave, check_collision, rotate
from utils.genetic_algorithm import GeneticAlgorithm


def get_points(door, room, index):
    return door.points[index][0] + room.origin[0], door.points[index][1] + room.origin[1]


def set_connected_rooms(rooms):
    for room in rooms:
        for other_room in rooms:
            if room != other_room:
                for door in room.doors:
                    for other_door in other_room.doors:
                        if set(
                                [get_points(door, room, index) for index in range(4)]
                        ) == set(
                            [get_points(other_door, other_room, index) for index in range(4)]
                        ):
                            room.connected_rooms.add(other_room)
                            other_room.connected_rooms.add(room)

    return rooms


class RoomTypesGa(GeneticAlgorithm):
    def __init__(self, no_generations, no_chromosomes, rooms, **kwargs):
        super().__init__(no_generations, no_chromosomes, **kwargs)
        self._rooms = rooms

    def mutate(self, chromosome):
        new_chromosome = dict()
        for i in self._rooms:
            new_chromosome[i.id] = chromosome[i.id]
            new_type = self.rand.choice(list(RoomType))
            to_mutate_element = self.rand.random() <= self.mutation_area
            if to_mutate_element:
                new_chromosome[i.id] = new_type
        return new_chromosome

    def crossover(self, chromosome1, chromosome2):
        new_chromosome = dict()
        for i in self._rooms:
            which = self.rand.random()
            new_chromosome[i.id] = deepcopy(chromosome1[i.id] if which >= 0.2 else chromosome2[i.id])
        return new_chromosome

    def get_fitness(self, chromosome):
        fitness = 0
        room_area_avg = 0
        for room in self._rooms:
            room_area_avg += room.area
        room_area_avg = room_area_avg / len(self._rooms) if len(self._rooms) else 0
        room_types = {
            RoomType.KITCHEN: 0,
            RoomType.BEDROOM: 0,
            RoomType.BATHROOM: 0,
            RoomType.HALL: 0,
            RoomType.LIVINGROOM: 0,
        }
        for room in self._rooms:
            for neighbor in room.connected_rooms:
                if chromosome[room.id] == RoomType.BATHROOM:
                    fitness -= 800 * len(room.windows)
                    if room_area_avg > room.area:
                        fitness += 300
                    else:
                        fitness -= 200
                    if chromosome[neighbor.id] == RoomType.BEDROOM or chromosome[neighbor.id] == RoomType.HALL:
                        fitness += 300
                    elif (
                            chromosome[neighbor.id] == RoomType.LIVINGROOM or
                            chromosome[neighbor.id] == RoomType.KITCHEN or
                            chromosome[neighbor.id] == RoomType.BATHROOM
                    ):
                        fitness -= 300
                elif chromosome[room.id] == RoomType.KITCHEN:
                    if chromosome[neighbor.id] == RoomType.LIVINGROOM:
                        fitness += 400
                    elif chromosome[neighbor.id] == RoomType.HALL:
                        fitness += 100
                    else:
                        fitness -= 300
                elif chromosome[room.id] == RoomType.BEDROOM:
                    if room_area_avg < room.area:
                        fitness += 300
            if chromosome[room.id] == RoomType.HALL:
                if len(room.doors) == 1:
                    fitness -= 1000
                if len(room.doors) > len(room.connected_rooms):
                    fitness += 600
                fitness += 600 * len(room.doors)
            room_types[chromosome[room.id]] += 1
        max_count = 0
        max_room_type = None
        for room_type, count in room_types.items():
            if count > 0:
                fitness += 300
            if count > max_count:
                max_count = count
                max_room_type = room_type
        if room_types[RoomType.BATHROOM] == 0:
            fitness -= 600
        if room_types[RoomType.BEDROOM] == 0:
            fitness -= 800
        if room_types[RoomType.KITCHEN] == 0:
            fitness -= 400
        if max_room_type == RoomType.BEDROOM:
            fitness += 600
        if room_types[RoomType.HALL] > 0 and (room_types[RoomType.BEDROOM] == 0 or room_types[
            RoomType.KITCHEN] == 0 or RoomType.BATHROOM == 0 or RoomType.LIVINGROOM == 0):
            fitness -= 1000
        return fitness

    def get_random_chromosome(self):
        new_chromosome = dict()
        for i in self._rooms:
            new_chromosome[i.id] = self.rand.choice(list(RoomType))
        return new_chromosome


def set_rooms_types(rooms):
    room_area_avg = 0
    for room in rooms:
        room_area_avg += room.area
    room_area_avg = room_area_avg / len(rooms)
    fixed_rooms = []
    for room in rooms:
        room.type = None
    for room in rooms:
        kitchen = 200
        bathroom = 300
        livingroom = 200
        hall = 100
        bedroom = 400
        hall -= len(room.windows) * 200

        hall += len(room.doors) * 200
        bathroom += 800 - len(room.windows) * 500
        for other_room in rooms:
            for door in room.doors:
                if door in other_room.doors:
                    if other_room.type == RoomType.BATHROOM:
                        bedroom += 300
                        hall += 300
                        kitchen -= 200
                        bathroom = 0
                        livingroom -= 200
                    elif other_room.type == RoomType.KITCHEN:
                        bathroom -= 300
                        livingroom += 300
                        bedroom -= 200
                        kitchen -= 300

        if room_area_avg < room.area:
            bathroom -= 200
            livingroom += 300
        if RoomType.KITCHEN in fixed_rooms:
            kitchen -= 300

        if RoomType.BATHROOM in fixed_rooms:
            bathroom -= 100

        if RoomType.LIVINGROOM in fixed_rooms:
            livingroom -= 300
        rand = random.Random(datetime.now())

        kitchen = kitchen if kitchen > 0 else 1
        bathroom = bathroom if bathroom > 0 else 1
        bedroom = bedroom if bedroom > 0 else 1
        hall = hall if hall > 0 else 1
        livingroom = livingroom if livingroom > 0 else 1
        room_type_number = rand.randrange(kitchen + bathroom + bedroom + hall + livingroom)
        if room_type_number < kitchen:
            fixed_rooms.append(RoomType.KITCHEN)
            room.type = RoomType.KITCHEN
        elif room_type_number < kitchen + bathroom:
            fixed_rooms.append(RoomType.BATHROOM)
            room.type = RoomType.BATHROOM
        elif room_type_number < kitchen + bathroom + bedroom:
            fixed_rooms.append(RoomType.BEDROOM)
            room.type = RoomType.BEDROOM
        elif room_type_number < kitchen + bathroom + bedroom + hall:
            fixed_rooms.append(RoomType.HALL)
            room.type = RoomType.HALL
        else:
            fixed_rooms.append(RoomType.LIVINGROOM)
            room.type = RoomType.LIVINGROOM


def can_place_furniture(furniture, room):
    for wall in room.walls:
        if check_collision(wall.poly, furniture.poly):
            return False
    for window in room.windows:
        if check_collision(window.poly, furniture.poly):
            return False
        if check_collision(window.blocker.poly, furniture.poly) and furniture.is_tall:
            return False
    for door in room.doors:
        if check_collision(door.poly, furniture.poly) or check_collision(door.blocker.poly, furniture.poly):
            return False
    for other_furniture in room.furniture:
        if check_collision(furniture.poly, other_furniture.poly):
            return False
    return not check_collision_concave(room.decomposed_parts, furniture.poly)


class Furnisher:
    def __init__(self, furniture_manager: FurnitureManager):
        self._furniture_manager = furniture_manager

    def _place_near_the_structure(self, structure, room):
        inner_margin = structure.inner_margin
        retries = abs(
            int((inner_margin[1][1] - inner_margin[0][1] + inner_margin[1][0] - inner_margin[0][0]) / factor)) * 2
        for i in range(retries):
            if inner_margin[0][0] == inner_margin[1][0]:
                point = (
                    inner_margin[0][0],
                    self._furniture_manager.rand.random() * (inner_margin[1][1] - inner_margin[0][1]) +
                    inner_margin[0][1]
                )
            else:
                point = (
                    self._furniture_manager.rand.random() * (inner_margin[1][0] - inner_margin[0][0]) +
                    inner_margin[0][0],
                    inner_margin[1][1]
                )

            self._try_to_place(point, room, structure.orientation)

    def _try_to_place(self, point, room, direction):
        new_object_config = self._furniture_manager.get_random_furniture(room.type)
        if not new_object_config:
            return False
        try:
            width = float(new_object_config.get("width"))
            height = float(new_object_config.get("height"))
        except TypeError:
            raise ConfigurationError("Width and height must be numbers")

        points = [
            point,
            (point[0] + width * factor, point[1]),
            (point[0] + width * factor, point[1] + height * factor),
            (point[0], point[1] + height * factor)

        ]
        if direction == Direction.RIGHT:
            points = [(point[0], point[1] + factor +2) for point in points]
        elif direction == Direction.UP:
            points = [rotate(points[0], point, math.pi / 2) for point in points]
            points = [(point[0] - 1, point[1]) for point in points]
        elif direction == Direction.LEFT:
            points = [rotate(points[0], point, math.pi) for point in points]
            points = [(point[0], point[1] - 1) for point in points]
        else:
            points = [rotate(points[0], point, 3 * math.pi / 2) for point in points]
            points = [(point[0] + 2, point[1]) for point in points]
        new_object = Furniture(points=points, orientation=direction, img=new_object_config.get("src"),
                               is_tall=new_object_config.get("is_tall"), furniture_type=new_object_config.get("type"))
        if can_place_furniture(new_object, room):
            self._furniture_manager.furniture_placed(new_object.type)
            room.furniture.append(new_object)

    def furnish_room(self, room: Room):
        self._furniture_manager.reset_room_resources()
        for door in room.doors:
            door.img = self._furniture_manager.get_door_image()
        for window in room.windows:
            window.img = self._furniture_manager.get_window_image()
            self._place_near_the_structure(window, room)

        for wall in room.walls:
            self._place_near_the_structure(wall, room)

    def furnish_house(self, house: House):
        for room in house.rooms:
            self.furnish_room(room)
