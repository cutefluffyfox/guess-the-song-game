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
LEADERBOARD = dict()

Session(app)


def publish_leaderboard(to: str):
    # output = [(key, item) for (key, item) in LEADERBOARD.items()]
    # emit('score', {'leaderboard': output}, to=to)
    emit('score', LEADERBOARD, to=to)


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
def join(*args):
    global LEADERBOARD

    room = session.get('room')
    username = session.get('username')
    join_room(room)

    from random import randint
    LEADERBOARD[username] = LEADERBOARD.get(username, randint(0, 69))

    emit('status', {'msg': f'welcome in game {username}'}, to=room)
    publish_leaderboard(to=room)


@socketio.on('text', namespace='/room')
def text(message):
    room = session.get('room')
    username = session.get('username')
    emit('message', {'msg': f"{username}: {message['msg']}"}, to=room)


@socketio.on('left', namespace='/room')
@socketio.on('disconnect', namespace='/room')
def left(*args):
    global LEADERBOARD

    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    if LEADERBOARD.get(username):
        del LEADERBOARD[username]
    session.clear()
    emit('status', {'msg': f'{username} has left the room'}, to=room)
    publish_leaderboard(to=room)


if __name__ == '__main__':
    socketio.run(app, debug=DEBUG, host=environ.get('HOST', '127.0.0.1'), port=int(environ.get('PORT', 8080)), allow_unsafe_werkzeug=DEBUG)
