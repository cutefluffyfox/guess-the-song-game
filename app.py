import logging
from os import environ

import dotenv
from flask import Flask, render_template, redirect, request, url_for, session
from datetime import timedelta
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session

from scripts.game_rules import DEFAULT_IFRAME_LINK, POSSIBLE_SUBMITTERS, ADMIN_USERNAME, TEXT_TO_EMOTE, POSSIBLE_TITLES, POSSIBLE_AUTHORS
from scripts.permissions import BASE_PERMISSIONS, VIEWER_PERMISSIONS, ADMIN_PERMISSIONS, AUTOMATIC_DRIVEN_PERMISSIONS, CHAT_MOD_CHANGE_PERMISSIONS
from scripts import memory

# load environment variables
dotenv.load_dotenv(dotenv.find_dotenv())

DEBUG = bool(environ.get('DEBUG', 0))
ADMIN = environ['ADMIN_USERNAME']

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='logs.log',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG if DEBUG else logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")

app.debug = bool(int(environ['DEBUG']))
app.config['SECRET_KEY'] = environ['FLASK_SECRET_KEY']
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)

# game-related global variables
GAME = memory.load_or_create(try_to_load=True, room_name='main')

Session(app)


def publish_leaderboard(to: str):
    logger.info(f'publish-leaderboard -> {to}')
    emit('score', GAME.get_leaderboard(), to=to)
    memory.save_game(GAME, bypass_time_constraint=True)


def publish_link(to: str):
    logger.info(f'stream-change -> {GAME.stream_url}')
    emit('stream-change', {'link': GAME.stream_url}, to=to)
    memory.save_game(GAME, bypass_time_constraint=True)


def publish_player_info(username: str):
    logger.info(f'stream-change -> {GAME.stream_url}')
    emit('user-info', GAME.get_user(username), to=username)
    memory.save_game(GAME)


def publish_clean_chat(messages: list[str], to: str):
    logger.info(f'SOCKET clear-chat -> {messages}')
    emit('clear-chat', messages, to=to)
    memory.save_game(GAME)


def show_user_permissions(username: str, to: str, request_username: str):
    logger.info(f'SOCKET show-user-permissions -> {username}')
    permissions = [
        {'name': permission, 'value': val}
        for permission, val in GAME.get_user_permissions(username).items()
        if permission not in AUTOMATIC_DRIVEN_PERMISSIONS
    ]

    if GAME.user_has_permission(username=request_username, permission='can_manage_users'):
        pass
    elif GAME.user_has_permission(username=request_username, permission='can_moderate_chat'):
        permissions = list(filter(lambda perm: perm['name'] in CHAT_MOD_CHANGE_PERMISSIONS, permissions))
    else:
        permissions = []

    emit('show-permissions', {'username': username, 'permissions': permissions}, to=to)
    memory.save_game(GAME)


def publish_submission_queue():
    logger.info(f'SOCKET publish-submission-queue')
    for user in GAME.get_with_permission(permission='can_check_submissions', only_online=True):
        emit('prediction-queue', GAME.get_submissions(), to=user)
    memory.save_game(GAME)


def send_chat_status(username: str, message: str, to: str):
    global GAME
    logger.info(f'SOCKET send-chat-status -> {to} | {username} | {message}')
    msg = GAME.chat.add_message(text=message, username=username, kind='status', can_send=True)
    emit('status', {'msg': GAME.chat.process(msg), 'username': username}, to=to)
    memory.save_game(GAME)


def send_chat_message(username: str, message: str, to: str):
    global GAME

    can_chat = GAME.user_has_permission(username, permission='can_chat')
    msg = GAME.chat.add_message(text=message, username=username, kind='message', can_send=can_chat)
    logger.info(f'SOCKET send-chat-message -> {to} | {username} | {message}')

    if not can_chat:
        logger.error(f'SOCKET send-chat-message -> FAILED {username} do not have chat permissions')
        memory.save_game(GAME)
        return

    emit('message', {
        'msg': GAME.chat.process(msg),
        'username': ADMIN_USERNAME if username == ADMIN else username,
        'color': GAME.get_user(username)['color'],
        'msg_id': str(msg.id),
    }, to=to)
    memory.save_game(GAME)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    logger.info(f'REQUESTS main page join')
    return render_template('homepage.html')


@app.route('/room', methods=['GET', 'POST'])
def room():
    global GAME

    logger.info(f'REQUESTS room join')
    emotes = [{'keyword': key, 'link': link} for key, link in TEXT_TO_EMOTE.items()]

    if request.method == 'POST':
        username = request.form['username']

        if set(username) - set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'):
            logger.error(f'API unsuccessful username attempt `{username}`')
            return render_template('homepage.html', message='Invalid username symbols: accepted one [a-zA-Z0-9_- ]')

        if not GAME.user_can_join(username):
            logger.error(f'API user already exists: `{username}`')
            return render_template('homepage.html', message='User with such username already in the game')

        # Store the data in session
        session['username'] = username
        session['room'] = GAME.room_name

        logger.info(f'API New session created')
        return render_template(
            './room.html',
            session=session,
            possible_submitters=POSSIBLE_SUBMITTERS,
            emotes=emotes,
            permissions=VIEWER_PERMISSIONS,
            possible_authors=POSSIBLE_AUTHORS,
            possible_titles=POSSIBLE_TITLES,
        )
    else:
        if session.get('room') is not None:
            logger.info(f'API old session loaded')
            return render_template(
                './room.html',
                session=session,
                possible_submitters=POSSIBLE_SUBMITTERS,
                emotes=emotes,
                permissions=VIEWER_PERMISSIONS,
                possible_authors=POSSIBLE_AUTHORS,
                possible_titles=POSSIBLE_TITLES,
            )
        else:
            return redirect(url_for('index'))


@socketio.on('text', namespace='/room')
def text(message):
    room = session.get('room')
    username = session.get('username')
    logger.info(f'API text `{username}` -> `{message}`')
    send_chat_message(message=message['msg'], username=username, to=room)


@socketio.on('leaderboard-change', namespace='/room')
def leaderboard_change(message):
    global GAME

    room = session.get('room')
    username = session.get('username')
    if not GAME.user_has_permission(username, permission='can_change_leaderboard'):
        logger.error(f'API failed attempt to change-leaderboard from user with no permission `{username}` | {GAME.get_user_permissions(username)} | {message}')
        return
    logger.info(f'API leaderboard-change `{username}` -> `{message}`')

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

    if not GAME.user_has_permission(username, permission='can_change_stream'):
        logger.error(f'API failed attempt to change-stream from user with no permission `{username}` | {GAME.get_user_permissions(username)} | {message}')
        return
    logger.info(f'API stream-change `{username}` -> `{message}`')

    link = message['link'].strip()
    if link == 'default':
        GAME.stream_url = DEFAULT_IFRAME_LINK
    elif link.startswith('https://'):
        GAME.stream_url = link
    publish_link(to=room)


@socketio.on('chat-action', namespace='/room')
def chat_action(data):
    global GAME

    room = session.get('room')
    username = session.get('username')

    if not GAME.user_has_permission(username, permission='can_moderate_chat'):
        logger.error(f'API failed attempt to chat-action from user with no permission `{username}` | {GAME.get_user_permissions(username)} | {data}')
        return

    if not data['msg_id'].lstrip('-').isdigit():
        logger.error(f'API failed to parse non-int message-id `{data}`')
        return

    logger.info(f'API chat-action `{username}` -> `{data}`')

    message_id = int(data['msg_id'])
    message = GAME.chat.find_message(message_id)
    delete_messages: list[int] = [message.id]

    if data.get('mute', False):
        GAME.mute_user(message.author)
        logger.info(f'API muting user `{message.author}`')

    if data.get('all', False):
        delete_messages.extend([msg.id for msg in GAME.chat.get_last_messages(username=message.author)])
        logger.info(f'API deleting last messages from `{message.author}`')

    GAME.chat.set_messages_status(delete_messages, status=f'Deleted by {username}')
    publish_clean_chat(messages=list(map(str, delete_messages)), to=room)
    publish_player_info(username=message.author)


@socketio.on('set-permission', namespace='/room')
def set_permission(data):
    global GAME

    username = session.get('username')

    if not GAME.user_has_permission(username, permission='can_manage_users') and not GAME.user_has_permission(username, permission='can_moderate_chat') :
        logger.error(f'API failed attempt to set-permission from user with no permission `{username}` | {GAME.get_user_permissions(username)} | {data}')
        return

    user = data['username']
    permission = data['permission']
    value = data['value']

    if permission not in BASE_PERMISSIONS:
        logger.error(f'API failed to set permission, unknown permission `{permission}')
        return

    if not GAME.user_has_permission(username, permission='can_manage_users') and GAME.user_has_permission(username, permission='can_moderate_chat') and permission not in CHAT_MOD_CHANGE_PERMISSIONS:
        logger.error(f'API failed to set permission, chatmods cant set permission `{permission}`')
        return

    logger.info(f'API set-permission `{username}` -> `{data}`')

    GAME.change_permissions(username=user, permissions={permission: value})
    publish_player_info(username=user)
    publish_leaderboard(to=session.get('room'))
    publish_submission_queue()


@socketio.on('check-permission', namespace='/room')
def check_permission(data):
    global GAME

    username = session.get('username')

    if not GAME.user_has_permission(username, permission='can_manage_users') and not GAME.user_has_permission(username, permission='can_moderate_chat'):
        logger.error(f'API failed attempt to check-permission from user with no permission `{username}` | {GAME.get_user_permissions(username)} | {data}')
        return
    logger.info(f'API check-permission `{username}` -> `{data}`')

    user = data['username']
    show_user_permissions(username=user, to=username, request_username=username)


@socketio.on('update-leaderboard', namespace='/room')
def update_leaderboard(data):
    global GAME

    username = session.get('username')

    if not GAME.user_has_permission(username, permission='can_change_leaderboard'):
        logger.error(f'API failed attempt to update-leaderboard from user with no permission `{username}` | {GAME.get_user_permissions(username)} | {data}')
        return
    logger.info(f'API update-leaderboard `{username}` -> `{data}`')

    GAME.update_leaderboard(data)
    GAME.reset_submissions()
    GAME.set_new_round_permissions()

    publish_leaderboard(to=session.get('room'))
    publish_submission_queue()

    for player in GAME.get_players(only_online=True):
        publish_player_info(username=player)


@socketio.on('set-score', namespace='/room')
def prediction(data):
    global GAME

    username = session.get('username')

    if not GAME.user_has_permission(username, permission='can_check_submissions'):
        logger.error(f'API failed attempt to set-score from user with no permission `{username}` | {GAME.get_user_permissions(username)} | {data}')
        return
    logger.info(f'API set-score `{username}` -> `{data}`')

    GAME.score_submission(username=data['username'], submission_id=data['submission'], score=data['score'])
    publish_submission_queue()
    publish_player_info(username=data['username'])



@socketio.on('prediction', namespace='/room')
def prediction(message):
    global GAME

    username = session.get('username')

    if not GAME.is_player(username):
        logger.error(f'API failed attempt to add-prediction from user with no permission `{username}` | {GAME.get_user_permissions(username)} | {message}')
        return
    logger.info(f'API new prediction `{username}` -> `{message}`')

    GAME.add_submission(
        username=username,
        song_info=message.get('author', '<none>'),
        submitter=message.get('submitter', '<none>')
    )

    publish_submission_queue()
    publish_player_info(username=username)


@socketio.on('join', namespace='/room')
def join(*args):
    global GAME

    room = session.get('room')
    username = session.get('username')

    if username is None:
        emit('redirect', {})
        return
    logger.info(f'API user join `{username}`')

    join_room(room)
    join_room(username)

    if username == ADMIN:
        GAME.add_user(username=username, permissions=ADMIN_PERMISSIONS.copy(), points=0)
    else:
        GAME.add_user(username=username, permissions=VIEWER_PERMISSIONS.copy(), points=0)

    send_chat_status(message=f'welcome in game {ADMIN_USERNAME if username == ADMIN else username}', username=username, to=room)
    publish_player_info(username=username)
    publish_leaderboard(to=room)
    publish_link(to=room)  # ideally send to username only, but this helps sync all users just in case
    publish_submission_queue()


@socketio.on('left', namespace='/room')
@socketio.on('disconnect', namespace='/room')
def left(*args):
    global GAME

    room = session.get('room')
    username = session.get('username')

    if username is None:
        logger.info(f'API null user left (normal after restarts)')
        return
    logger.info(f'API user left `{username}`')

    leave_room(room)
    leave_room(username)
    GAME.remove_user(username=username)

    session.clear()
    send_chat_status(message=f'{ADMIN_USERNAME if username == ADMIN else username} has left the game', username=username, to=room)
    publish_leaderboard(to=room)
    publish_link(to=room)


if __name__ == '__main__':
    logger.info(f'Starting application')
    socketio.run(
        app,
        debug=bool(environ.get('DEBUG', False)),
        host=environ.get('HOST', '127.0.0.1'),
        port=int(environ.get('PORT', 8080)),
        allow_unsafe_werkzeug=True,
    )
