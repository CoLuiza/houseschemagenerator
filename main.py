from export.draw import draw_house
from house.furniture_manager import FurnitureManager
from house.service import Furnisher, RoomTypesGa
from image_processor.service import Processor


def main():
    processor = Processor("debug.png")
    house = processor.get_house()
    manager = FurnitureManager()
    furnisher = Furnisher(manager)

    room_type_ga = RoomTypesGa(no_generations=4000, no_chromosomes=10, rooms=house.rooms, mutation_rate=0.3,
                               mutation_area=0.3)
    types = room_type_ga.run()
    for i in range(len(types)):
        house.rooms[i].type = types[house.rooms[i].id]
    furnisher.furnish_house(house)
    draw_house(house, path='/')


if __name__ == '__main__':
    main()
