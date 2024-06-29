from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os

from flask import request, redirect, url_for
from werkzeug.utils import secure_filename
import string
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/videos')
def videos():
    static_folder = os.path.join(app.static_folder, '')
    all_media_files = [f for f in os.listdir(static_folder) if f.endswith(('.mp4', '.jpg', '.png','.webp'))]

    media_categories = {"generic": []}

    for file in all_media_files:
        parts = file.split('-', 1)
        prefix = parts[0] if len(parts) > 1 else "generic"
        
        if prefix not in media_categories:
            media_categories[prefix] = [file]
        else:
            media_categories[prefix].append(file)
    
    return render_template("videos.html", media_categories=media_categories)

@app.route('/player')
def player():
    return render_template("player.html")

@socketio.on('media selected',namespace='/')
def handle_media_selection(media_name):
    print(media_name)
    emit('switch media', media_name, namespace='/', broadcast=True)

UPLOAD_FOLDER = 'static'

def generate_random_filename(extension):
    random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f'{random_suffix}.{extension}'

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        selected_name = request.form['name']  # Extract the selected name from the form data
        if file and selected_name:  # Ensure both file and name are present
            filename, extension = os.path.splitext(file.filename)
            new_filename = f'{selected_name}-{generate_random_filename(extension.lstrip("."))}'
            file.save(os.path.join(UPLOAD_FOLDER, new_filename))
            print(new_filename)
            socketio.emit('switch media', new_filename, namespace='/')
            return redirect(url_for('player'))
    return redirect(url_for('player'))


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
