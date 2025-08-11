from os import environ

import dotenv
from flask import Flask, render_template, redirect, request, url_for, session
from datetime import timedelta
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session

from scripts.game_rules import DEFAULT_IFRAME_LINK, POSSIBLE_SUBMITTERS, ADMIN_USERNAME, TEXT_TO_EMOTE
from scripts.permissions import VIEWER_PERMISSIONS, PLAYER_PERMISSIONS, ADMIN_PERMISSIONS
from scripts import game

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
GAME = game.Game('main', throw_exceptions=False)

Session(app)


def publish_leaderboard(to: str):
    emit('score', GAME.get_leaderboard(), to=to)


def publish_link(to: str):
    emit('stream-change', {'link': GAME.stream_url}, to=to)


def publish_player_info(username: str):
    emit('user-info', GAME.get_user(username), to=username)


def publish_clean_chat(messages: list[str], to: str):
    emit('clear-chat', messages, to=to)


def send_chat_status(username: str, message: str, to: str):
    global GAME
    msg = GAME.chat.add_message(text=message, username=username, kind='status')
    emit('status', {'msg': GAME.chat.process(msg), 'username': username}, to=to)


def send_chat_message(username: str, message: str, to: str):
    global GAME
    msg = GAME.chat.add_message(text=message, username=username, kind='message')
    if not GAME.user_has_permission(username, permission='can_chat'):
        return
    emit('message', {
        'msg': GAME.chat.process(msg),
        'username': ADMIN_USERNAME if username == ADMIN else username,
        'color': GAME.get_user(username)['color'],
        'msg_id': str(msg.id),
    }, to=to)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('homepage.html')


@app.route('/room', methods=['GET', 'POST'])
def room():
    global GAME

    emotes = [{'keyword': key, 'link': link} for key, link in TEXT_TO_EMOTE.items()]

    if request.method == 'POST':
        username = request.form['username']

        # Store the data in session
        session['username'] = username
        session['room'] = GAME.room_name

        return render_template('./room-admin.html' if username == ADMIN else './room.html', session=session, possible_submitters=POSSIBLE_SUBMITTERS, emotes=emotes)
    else:
        if session.get('room') is not None:
            return render_template('./room-admin.html' if session.get('username') == ADMIN else './room.html', session=session, possible_submitters=POSSIBLE_SUBMITTERS, emotes=emotes)
        else:
            return redirect(url_for('index'))


@socketio.on('text', namespace='/room')
def text(message):
    room = session.get('room')
    username = session.get('username')
    send_chat_message(message=message['msg'], username=username, to=room)


@socketio.on('leaderboard-change', namespace='/room')
def leaderboard_change(message):
    global GAME

    room = session.get('room')
    username = session.get('username')
    if username != ADMIN:
        return
    try:
        template_leaderboard = eval(message['data'])
        if isinstance(template_leaderboard, dict):
            GAME.set_leaderboard(template_leaderboard)
            publish_leaderboard(to=room)
    except Exception as ex:  # if formatting has failed
        pass


@socketio.on('stream-change', namespace='/room')
def stream_change(message):
    global GAME

    room = session.get('room')
    username = session.get('username')

    if username != ADMIN:
        return
    link = message['link'].strip()
    if link == 'default':
        GAME.stream_url = DEFAULT_IFRAME_LINK
    elif link.startswith('https://'):
        GAME.stream_url = link
    publish_link(to=room)


@socketio.on('chat-action', namespace='/room')
def stream_change(data):
    global GAME

    room = session.get('room')
    username = session.get('username')

    if not GAME.user_has_permission(username, permission='can_moderate_chat'):
        return

    if not data['msg_id'].lstrip('-').isdigit():
        return

    message_id = int(data['msg_id'])
    message = GAME.chat.find_message(message_id)
    delete_messages: list[str] = [str(message.id)]

    if data.get('mute', False):
        GAME.mute_user(message.author)

    if data.get('all', False):
        delete_messages.extend([str(msg.id) for msg in GAME.chat.get_last_messages(username=message.author)])

    publish_clean_chat(messages=delete_messages, to=room)
    publish_player_info(username=message.author)


@socketio.on('prediction', namespace='/room')
def prediction(message):
    global GAME

    username = session.get('username')

    if GAME.is_player(username):
        GAME.add_submission(
            username=username,
            song_info=message.get('author', '<none>'),
            submitter=message.get('submitter', '<none>')
        )

        # TODO: remove it
        from random import randint
        GAME.score_submission(username=username, submission_id=len(GAME.get_user_submissions(username))-1, score=randint(0, 4))
        GAME.update_leaderboard({username: 10})
        publish_leaderboard(to=session.get('room'))

        submissions = GAME.get_submissions()
        for admin in GAME.get_admins():
            emit('prediction-queue', submissions, to=admin)
        publish_player_info(username=username)


@socketio.on('join', namespace='/room')
def join(*args):
    global GAME

    room = session.get('room')
    username = session.get('username')

    if username is None:
        emit('redirect', {})
        return

    join_room(room)
    join_room(username)

    if username == ADMIN:
        GAME.add_user(username=username, permissions=ADMIN_PERMISSIONS)
    else:
        GAME.add_user(username=username, permissions=PLAYER_PERMISSIONS, points=0)  # TODO: swap to viewer
    if username == 'cutefluffyfox':
        GAME.change_permissions(username=username, permissions={'can_moderate_chat': True})

    send_chat_status(message=f'welcome in game {ADMIN_USERNAME if GAME.is_admin(username) else username}', username=username, to=room)
    publish_player_info(username=username)
    publish_leaderboard(to=room)
    publish_link(to=room)


@socketio.on('left', namespace='/room')
@socketio.on('disconnect', namespace='/room')
def left(*args):
    global GAME

    room = session.get('room')
    username = session.get('username')

    if username is None:
        return

    leave_room(room)
    leave_room(username)
    GAME.remove_user(username=username)

    session.clear()
    send_chat_status(message=f'{ADMIN_USERNAME if GAME.is_admin(username) else username} has left the game', username=username, to=room)
    publish_leaderboard(to=room)
    publish_link(to=room)


if __name__ == '__main__':
    socketio.run(
        app,
        debug=bool(environ.get('DEBUG', False)),
        host=environ.get('HOST', '127.0.0.1'),
        port=int(environ.get('PORT', 8080)),
        allow_unsafe_werkzeug=True,
    )
