# House Schema Generator


About the project
-----------------
The project is meant to receive as input an empty house and furnish it.
The initial image (1) is taken and is converted. The image processor is using BFS to find the rooms areas (2), then, a margin is drawn which represents the walls, doors or windows depending on the input image color (3). The rooms types are selected using a genetic algorithm (4) and then furnished depending on the room type, windows, doors and config files.
![transform](https://github.com/CoLuiza/houseschemagenerator/blob/master/readme/transform.png?raw=true)

Project architecture
--------------------
![diagram](https://github.com/CoLuiza/houseschemagenerator/blob/master/readme/diagram.png?raw=true)

Notes
-----
The input file should contain white pixels (255,255,255,1) RGBa which represent the inside and the outside of the house, black pixels (0,0,0,1) RGBa which represent the walls, blue pixels (0,0,255,1) RGBa which represent the windows and finally, red pixels (255,0,0,1) which represent the doors.
A door is represented by 2 red pixels. Walls and windows can be represented by any number of pixels but the corners should be made of walls.
There are two config files [furniture config](https://github.com/CoLuiza/houseschemagenerator/blob/master/furniture_config.json) and [room config](https://github.com/CoLuiza/houseschemagenerator/blob/master/room_config.json).
The furniture config - contains for each furniture the name, the photo, the width, the height and a boolean that tells if the furniture item si tall or not. (Tall objects will never be placed in front of windows and furniture will never be placed in front of the doors).
The rooms config - contains for each type of room (which are fixed - kitchen, living room, bedroom, hall, bathroom), what furniture can be placed there (the name should be the same with the one declared in the furniture config file), limit (which can be set to "none" so there is no limit) and likeness which represent the chance of the object to be placed when crossing the room.
Example of input:
![input](https://github.com/CoLuiza/houseschemagenerator/blob/master/readme/input.png?raw=true)


Example of output:
![output](https://github.com/CoLuiza/houseschemagenerator/blob/master/readme/output.png?raw=true)
