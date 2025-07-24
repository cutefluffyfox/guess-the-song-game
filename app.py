from os import environ

import dotenv
from flask import Flask, render_template, redirect, request, url_for, session
from datetime import timedelta
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session

# load environment variables
dotenv.load_dotenv(dotenv.find_dotenv())


app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")

app.debug = bool(int(environ['DEBUG']))
app.config['SECRET_KEY'] = environ['FLASK_SECRET_KEY']
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)

DEBUG = bool(environ.get('DEBUG', 0))
ADMIN = environ['ADMIN_USERNAME']

# game-related global variables
LEADERBOARD = dict()
# DEFAULT_LINK = 'https://sketchfab.com/models/befbb2c422fc4b92aecae8c5114967e9/embed?autostart=1&internal=1&tracking=0&ui_infos=0&ui_snapshots=1&ui_stop=0&ui_watermark=0'
DEFAULT_LINK = 'https://www.openstreetmap.org/export/embed.html?bbox=-0.004017949104309083%2C51.47612752641776%2C0.00030577182769775396%2C51.478569861898606&amp;layer=mapnik'
STREAM_LINK = DEFAULT_LINK

Session(app)


def publish_leaderboard(to: str):
    emit('score', LEADERBOARD, to=to)


def publish_link(to: str):
    emit('stream-change', {'link': STREAM_LINK}, to=to)


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
        return render_template('./room-admin.html' if username == ADMIN else './room.html', session=session)
    else:
        if session.get('room') is not None:
            return render_template('./room-admin.html' if session.get('username') == ADMIN else './room.html', session=session)
        else:
            return redirect(url_for('index'))


@socketio.on('text', namespace='/room')
def text(message):
    room = session.get('room')
    username = session.get('username')
    if username == ADMIN:
        username = '[admin]'
    emit('message', {'msg': f"{username}: {message['msg']}"}, to=room)


@socketio.on('leaderboard-change', namespace='/room')
def leaderboard_change(message):
    global LEADERBOARD

    room = session.get('room')
    username = session.get('username')
    if username != ADMIN:
        return
    template_leaderboard = eval(message['data'])
    if template_leaderboard:
        LEADERBOARD = template_leaderboard
        publish_leaderboard(to=room)


@socketio.on('stream-change', namespace='/room')
def stream_change(message):
    global STREAM_LINK

    room = session.get('room')
    username = session.get('username')

    if username != ADMIN:
        return
    link = message['link'].strip()
    if link == 'default':
        STREAM_LINK = DEFAULT_LINK
    elif link.startswith('https://'):
        STREAM_LINK = link
    publish_link(to=room)


@socketio.on('prediction', namespace='/room')
def prediction(message):
    room = session.get('room')
    username = session.get('username')

    if username != ADMIN:
        from random import choice, randint
        score = randint(0, 4)
        LEADERBOARD[username] += score
        publish_leaderboard(to=room)
        emit('result', {'type': message['type'], 'result': f"+{score}"}, to=username)


@socketio.on('join', namespace='/room')
def join(*args):
    global LEADERBOARD

    room = session.get('room')
    username = session.get('username')
    join_room(room)
    join_room(username)

    if username != ADMIN:
        from random import randint
        LEADERBOARD[username] = LEADERBOARD.get(username, randint(0, 69))
        emit('status', {'msg': f'welcome in game {username}'}, to=room)
    publish_leaderboard(to=room)
    publish_link(to=room)


@socketio.on('left', namespace='/room')
@socketio.on('disconnect', namespace='/room')
def left(*args):
    global LEADERBOARD

    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    leave_room(username)
    if LEADERBOARD.get(username):
        del LEADERBOARD[username]
    session.clear()
    if username != ADMIN:
        emit('status', {'msg': f'{username} has left the room'}, to=room)
    publish_leaderboard(to=room)
    publish_link(to=room)


if __name__ == '__main__':
    socketio.run(app, debug=DEBUG, host=environ.get('HOST', '127.0.0.1'), port=int(environ.get('PORT', 8080)), allow_unsafe_werkzeug=DEBUG)
