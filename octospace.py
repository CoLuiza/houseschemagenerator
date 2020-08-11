from flask import Flask, render_template, send_from_directory
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import string
import random
from export.draw import draw_house
from house.furniture_manager import FurnitureManager
from house.service import Furnisher, RoomTypesGa
from image_processor.service import Processor

UPLOAD_FOLDER = 'external/uploads'
RESULTS_FOLDER = 'external/results'
ALLOWED_EXTENSIONS = {'png', }

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def generate_filename(prefix):
    name = f"{prefix}_"
    rand = random.SystemRandom()

    for i in range(6):
        name += rand.choice(string.ascii_letters+string.digits)
    return name


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['POST', 'GET'])
def primary_page():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('result_page', filename=filename))
    return render_template("base.html")


@app.route('/result/<filename>')
def result_page(filename):
    processor = Processor(filename)
    house = processor.get_house()
    manager = FurnitureManager()
    furnisher = Furnisher(manager)

    room_type_ga = RoomTypesGa(no_generations=4000, no_chromosomes=10, rooms=house.rooms, mutation_rate=0.3,
                               mutation_area=0.3)
    types = room_type_ga.run()
    for i in range(len(types)):
        house.rooms[i].type = types[house.rooms[i].id]
    furnisher.furnish_house(house)
    name = generate_filename(prefix=filename.split(".")[0])
    try:
        draw_house(house, path=f'{RESULTS_FOLDER}/{name}')
    except Exception:
        return redirect(url_for('primary_page'))
    return send_from_directory(f'{RESULTS_FOLDER}', f"{name}house.png")


if __name__ == "__main__":
    app.run(debug=True)
