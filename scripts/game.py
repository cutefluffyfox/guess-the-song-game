from datetime import datetime

from scripts.chat import Chat
from scripts.errors import GameRuleViolation, UserManagementError, GameErrors
from scripts.game_rules import MAX_SUBMISSION_COUNT, POSSIBLE_SUBMITTERS, DEFAULT_IFRAME_LINK
from scripts.permissions import BASE_PERMISSIONS, PLAYER_PERMISSIONS


class Submission:
    song_title: str
    submitter: str
    score: float
    submit_time: datetime
    score_time: datetime
    processed: bool

    def __init__(self, song_title: str, submitter: str):
        # if submitter and submitter not in POSSIBLE_SUBMITTERS:
        #     raise GameRuleViolation(f'Invalid submitter username')
        self.song_title = song_title
        self.submitter = submitter
        self.submit_time = datetime.now()
        self.processed = False


    def set_score(self, score: float):
        if score is None:
            score = 0
        self.score = score
        self.score_time = datetime.now()
        self.processed = True

    def json(self) -> dict:
        data = {
            'song': self.song_title,
            'submitter': self.submitter,
            'submit_time': self.submit_time.timestamp(),
            'processed': self.processed,
        }
        if self.processed:
            data['score'] = self.score
            data['score_time'] = self.score_time.timestamp()
        return data


class User:
    permissions: dict[str, bool] = BASE_PERMISSIONS
    username: str
    color: str
    points: float = 0.0
    submissions: list[Submission]

    def __init__(self, username: str, color: str or None = None, points: float or None = None, permissions: dict[str, bool] = None):
        self.username = username
        self.points = points if points else 0
        self.submissions = list()

        # base permissions
        self.permissions = BASE_PERMISSIONS.copy()
        self.permissions['can_chat'] = True
        if permissions:
            for key, val in permissions.items():
                self.permissions[key] = val
        # at the moment of creation, each user is online
        self.permissions['is_online'] = True

        # select random color
        from random import choice
        self.color = (
            color
            if isinstance(color, str) else
            User.__from_hex(choice([
                '#e6194B',
                '#3cb44b',
                '#ffe119',
                '#4363d8',
                '#f58231',
                '#911eb4',
                '#42d4f4',
                '#f032e6',
                '#bfef45',
                '#fabed4',
                '#469990',
                '#dcbeff',
                '#9A6324',
                '#fffac8',
                '#800000',
                '#aaffc3',
                '#808000',
                '#ffd8b1',
                '#000075'
            ]))
        )

    @staticmethod
    def __from_hex(color: str) -> str:
        color = color.lstrip('#').strip()
        return f"rgb({int(color[0:2], 16)}, {int(color[2:4], 16)}, {int(color[4:6], 16)});"

    @property
    def is_online(self) -> bool:
        return self.permissions['is_online']

    def add_submission(self, submission: Submission):
        if not self.get_permission('can_play'):
            raise UserManagementError('Attempted to add submission to a non-player')

        if len(self.submissions) >= MAX_SUBMISSION_COUNT:
            raise GameRuleViolation(f'User violated amount of submissions')
        self.submissions.append(submission)
        self.submissions.sort(key=lambda s: s.submit_time)

    def get_submissions(self):
        self.submissions.sort(key=lambda s: s.submit_time)
        return self.submissions

    def clear_submissions(self):
        self.submissions.clear()

    def change_permissions(self, permissions: dict[str, bool] = None):
        if not permissions:
            return
        for permission, val in permissions.items():
            self.permissions[permission] = val

    def get_permission(self, permission: str) -> bool:
        return self.permissions[permission]

    def get_permissions(self) -> dict[str, bool]:
        return self.permissions

    def json(self):
        self.submissions.sort(key=lambda s: s.submit_time)
        return {
            'username': self.username,
            'color': self.color,
            'points': self.points,
            'submissions': [submission.json() for submission in self.submissions],
            'permissions': self.permissions
        }


class Game:
    users: dict[str, User]
    room_name: str
    throw_exceptions: bool = False
    stream_url: str = DEFAULT_IFRAME_LINK
    chat: Chat

    def __init__(self, room_name: str, throw_exceptions: bool = False):
        self.room_name = room_name
        self.throw_exceptions = throw_exceptions
        self.users = dict()
        self.chat = Chat()

    def get_leaderboard(self) -> dict[str, list[dict]]:
        leaderboard = {
            'viewers': list(),
            'players': list(),
        }
        for username in self.get_players(only_online=False):
            user = self.users[username]
            leaderboard['players'].append({
                'username': user.username,
                'points': user.points,
                'is_online': user.is_online,
                'can_manage_users' : user.get_permission('can_manage_users'),
                'can_moderate_chat' : user.get_permission('can_moderate_chat'),
            })
        for username in self.get_viewers(only_online=False):
            user = self.users[username]
            leaderboard['viewers'].append({
                'username': user.username,
                'is_online': user.is_online,
                'can_manage_users': user.get_permission('can_manage_users'),
                'can_moderate_chat': user.get_permission('can_moderate_chat'),
            })
        leaderboard['players'] = sorted(leaderboard['players'], key=lambda d: d['points'], reverse=True)
        return leaderboard

    def get_players(self, only_online: bool = True) -> list[str]:
        return [username for username, user in self.users.items() if self.is_player(user) and (not only_online or only_online and user.is_online)]

    def get_viewers(self, only_online: bool = True) -> list[str]:
        return [username for username, user in self.users.items() if self.is_viewer(user) and (not only_online or only_online and user.is_online)]

    def get_with_permission(self, permission: str, only_online: bool = True) -> list[str]:
        return [username for username, user in self.users.items() if user.get_permission(permission) and (not only_online or only_online and user.is_online)]

    def is_admin(self, username: str or User) -> bool:
        if isinstance(username, User):
            return username.get_permission('can_change_leaderboard')
        return self.is_admin(self.users.get(username, User('')))

    def is_player(self, username: str or User) -> bool:
        if isinstance(username, User):
            return username.get_permission('can_play')
        return self.is_player(self.users.get(username, User('')))

    def is_viewer(self, username: str or User) -> bool:
        return not self.is_player(username)

    def get_user(self, username: str) -> dict:
        user = self.users.get(username)
        if user is None:
            self.__throw_if_allowed(UserManagementError, 'Tried to get info about non-existent user')
            return {}
        user_info = user.json()
        if self.is_player(user):
            user_info['submissions-left'] = MAX_SUBMISSION_COUNT - len(user_info['submissions'])
        return user_info

    def add_user(self, username: str, permissions: dict[str, bool] = None, points: float or None = None):
        if self.users.get(username) is None:
            user = User(username=username, permissions=permissions, points=points)
            self.users[username] = user
        else:  # if user already exists
            if self.is_player(self.users[username]):
                self.users[username].change_permissions({'can_check_submissions': False})

        self.users[username].change_permissions({'is_online': True})

    def user_can_join(self, username: str):
        if self.users.get(username) is None:
            return True
        return not self.users[username].is_online  # if player with same username online -> don't allow that

    def change_permissions(self, username: str, permissions: dict[str, bool] = None):
        if self.users.get(username) is None:
            return
        self.users[username].change_permissions(permissions=permissions)

    def remove_user(self, username: str):
        if self.users.get(username):
            self.users[username].change_permissions(permissions={'is_online': False})

    def update_leaderboard(self, modification: dict[str, int], mode: str = 'add'):
        assert mode in {'add', 'set'}, 'Invalid mode type'

        for username, score in modification.items():
            if not self.users.get(username):  # TODO: add warning
                self.add_user(username, permissions=PLAYER_PERMISSIONS)
            if self.is_player(username):
                self.users[username].points = float(score if mode == 'set' else self.users[username].points + score)
            else:
                self.__throw_if_allowed(UserManagementError, 'Attempting to set score for non-player. You sure what you are doing?')

    def set_leaderboard(self, leaderboard: dict[str, float]):
        for username, score in leaderboard.items():
            if not self.users.get(username):  # TODO: add warning
                self.add_user(username, permissions=PLAYER_PERMISSIONS)

            if self.is_player(username):
                self.users[username].points = float(score)
            else:
                self.__throw_if_allowed(UserManagementError, 'Attempting to set score for non-player. You sure what you are doing?')

    def __throw_if_allowed(self, error: GameErrors, name: str):
        if self.throw_exceptions:
            raise error(name)

    def reset_submissions(self):
        for username, user in self.users.items():
            if self.is_player(user):
                self.users[username].clear_submissions()

    def add_submission(self, username: str, song_info: str, submitter: str):
        if not self.users.get(username):
            self.__throw_if_allowed(UserManagementError, 'Attempted to add submission to non-existent user')
            return
        if not self.is_player(username):
            self.__throw_if_allowed(UserManagementError, 'Attempted to add submission to non-player')
            return

        submission = Submission(
            song_title=song_info,
            submitter=submitter
        )
        self.users[username].add_submission(submission)  # TODO: add error-handling when max-submissions violated

    def score_submission(self, username: str, submission_id: int, score: float):
        if not self.users.get(username):
            self.__throw_if_allowed(UserManagementError, 'Attempted to score submission of non-existent user')
            return
        if not self.is_player(username):
            self.__throw_if_allowed(UserManagementError, 'Attempted to score submission to non-player')
            return
        if not isinstance(submission_id, int) or submission_id < 0 or submission_id >= len(self.users[username].get_submissions()):
            self.__throw_if_allowed(RuntimeError, 'Attempted to score non-existent submission (invalid id)')
            return
        self.users[username].submissions[submission_id].set_score(score)


    def get_submissions(self) -> list[dict]:
        submissions = []
        for username, user in self.users.items():
            if not user.get_submissions():
                continue
            submissions.append({
                'username': username,
                'submissions': user.json()['submissions']
            })
        submissions.sort(key=lambda usr: min([s['submit_time'] for s in usr['submissions']]))
        return submissions

    def get_user_submissions(self, username: str) -> list[dict]:
        if not self.users.get(username):
            self.__throw_if_allowed(UserManagementError, 'Attempted to get submissions of non-existent user')
            return
        if not self.is_player(username):
            self.__throw_if_allowed(UserManagementError, 'Attempted to get submissions of non-player')
            return
        return self.users[username].json()['submissions']

    def mute_user(self, username: str):
        if not self.users.get(username):
            self.__throw_if_allowed(UserManagementError, 'Attempted to get submissions of non-existent user')
            return
        self.users[username].change_permissions({'can_chat': False})

    def user_has_permission(self, username: str, permission: str) -> bool:
        if not self.users.get(username):
            return False
        return self.users[username].get_permission(permission)

    def get_user_permissions(self, username: str) -> dict[str, bool]:
        if not self.users.get(username):
            return {}
        return self.users[username].get_permissions()

