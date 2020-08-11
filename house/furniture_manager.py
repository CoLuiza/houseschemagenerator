import json
import random
from collections import defaultdict
from numpy.random import choice
from config.convertor import room_type_to_json_room


class FurnitureManager:
    def __init__(self, furniture_config_file="furniture_config.json", room_config_file="room_config.json"):
        self._furniture_config = self._load_json(furniture_config_file)
        self._room_config = self._load_json(room_config_file)
        self._given_furniture = defaultdict(lambda: 0)
        self.rand = random.SystemRandom()

    def _load_json(self, file):
        with open(file) as json_file:
            try:
                return json.load(json_file)
            except Exception:
                raise ConfigurationError("Invalid config json file.")

    def reset_room_resources(self):
        self._given_furniture = defaultdict(lambda: 0)

    def furniture_placed(self, furniture):
        self._given_furniture[furniture] = self._given_furniture[furniture]+1

    def get_door_image(self):
        return self._furniture_config.get("door").get("src")

    def get_window_image(self):
        return self._furniture_config.get("window").get("src")

    def get_random_furniture(self, room_type):
        try:
            furniture = self._room_config.get(room_type_to_json_room(room_type))
            furniture_configs = list()
            fitness_sum = 0
            if not furniture:
                return None
            for furniture_type, properties in furniture.items():
                furniture_config = self._furniture_config.get(furniture_type)
                limit = properties.get("limit", "none")
                try:
                    likeness = float(properties.get("likeness"))
                except ValueError:
                    raise ConfigurationError("Likeness should be an integer number.")
                if limit == "none":
                    furniture_config["fitness"] = likeness
                    if not furniture_config["fitness"]:
                        raise ConfigurationError("All furniture must have likeness attribute in room config class..")
                else:
                    try:
                        limit = int(limit)
                        if limit < 0:
                            raise ValueError
                    except ValueError:
                        raise ConfigurationError("Limit should be a natural number or 'none'.")
                    furniture_config["fitness"] = likeness * (limit - self._given_furniture[furniture_type])
                furniture_config["type"] = furniture_type
                furniture_configs.append(furniture_config)
                fitness_sum += furniture_config["fitness"]
            if fitness_sum == 0:
                return None
            unit = 1 / fitness_sum
            draw = choice(furniture_configs, 1,
                          p=[furniture.get("fitness") * unit for furniture in furniture_configs])
            return draw.tolist()[0]
        except TypeError:
            return None


class ConfigurationError(Exception):
    pass
