from os import environ

import dotenv
from flask import Flask, render_template, redirect, request, url_for, session, Response
from datetime import timedelta
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session

from scripts.camera import Camera

# TODO: understand how to properly host ngrok
# from waitress import serve
# from flask_ngrok import run_with_ngrok

# load environment variables
dotenv.load_dotenv(dotenv.find_dotenv())


app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")

app.debug = bool(int(environ['DEBUG']))
app.config['SECRET_KEY'] = environ['FLASK_SECRET_KEY']
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)

Session(app)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('homepage.html')


@app.route('/room', methods=['GET', 'POST'])
def room():
    if request.method == 'POST':
        username = request.form['username']

        # Store the data in session
        session['username'] = username
        session['room'] = 'default'
        return render_template('./room.html', session=session)
    else:
        if session.get('room') is not None:
            return render_template('./room.html', session=session)
        else:
            return redirect(url_for('index'))


@socketio.on('join', namespace='/room')
def join(message):
    room = session.get('room')
    username = session.get('username')
    join_room(room)
    emit('status', {'msg': f'welcome in game {username}'}, to=room)


@socketio.on('text', namespace='/room')
def text(message):
    room = session.get('room')
    username = session.get('username')
    emit('message', {'msg': f"{username}: {message['msg']}"}, to=room)


@socketio.on('left', namespace='/room')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': f'{username} has left the room'}, to=room)


def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


def make_frame_generator(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(make_frame_generator(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # run_with_ngrok(app)
    app.run()
