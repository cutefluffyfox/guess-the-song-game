from datetime import datetime

from scripts.chat import Chat
from scripts.errors import GameRuleViolation, UserManagementError, GameErrors
from scripts.game_rules import MAX_SUBMISSION_COUNT, POSSIBLE_SUBMITTERS, DEFAULT_IFRAME_LINK


class Submission:
    song_title: str
    submitter: str
    score: float
    submit_time: datetime
    score_time: datetime
    processed: bool

    def __init__(self, song_title: str, submitter: str):
        if submitter and submitter not in POSSIBLE_SUBMITTERS:
            raise GameRuleViolation(f'Invalid submitter username')
        self.song_title = song_title
        self.submitter = submitter
        self.submit_time = datetime.now()
        self.processed = False


    def set_score(self, score: float):
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
    is_online: bool = False
    username: str
    color: str

    def __init__(self, username: str, color: str or None = None):
        from random import choice
        self.username = username
        self.is_online = False
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

    def json(self) -> dict:
        return {'username': self.username, 'color': self.color}

    @staticmethod
    def __from_hex(color: str) -> str:
        color = color.lstrip('#').strip()
        return f"rgb({int(color[0:2], 16)}, {int(color[2:4], 16)}, {int(color[4:6], 16)});"


class Viewer(User):
    pass


class Player(User):
    points: float = 0.0
    submissions: list[Submission]

    def __init__(self, username: str, points: float, color: str or None = None):
        super().__init__(username=username, color=color)
        self.points = points
        self.submissions = list()

    def add_submission(self, submission: Submission):
        if len(self.submissions) >= MAX_SUBMISSION_COUNT:
            raise GameRuleViolation(f'User violated amount of submissions')
        self.submissions.append(submission)
        self.submissions.sort(key=lambda s: s.submit_time)

    def get_submissions(self):
        self.submissions.sort(key=lambda s: s.submit_time)
        return self.submissions

    def clear_submissions(self):
        self.submissions.clear()

    def json(self):
        self.submissions.sort(key=lambda s: s.submit_time)
        return {
            'username': self.username,
            'color': self.color,
            'points': self.points,
            'submissions': [submission.json() for submission in self.submissions]
        }


class Moderator(User):
    pass


class Admin(Moderator):
    pass


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

    def get_leaderboard(self) -> list[dict]:
        leaderboard = list()
        for username in self.get_players(only_online=False):
            user = self.users[username]
            leaderboard.append({
                'username': user.username,
                'points': user.points,
                'is_online': user.is_online
            })
        return leaderboard

    def get_submissions(self) -> dict[str, list[dict]]:
        submissions = dict()
        for username in self.get_players():
            submissions[username] = self.users[username].json()['submissions']
        return submissions

    def get_players(self, only_online: bool = True) -> list[str]:
        return [username for username, user in self.users.items() if isinstance(user, Player) and (not only_online or only_online and user.is_online)]

    def get_viewers(self, only_online: bool = True) -> list[str]:
        return [username for username, user in self.users.items() if isinstance(user, Viewer) and (not only_online or only_online and user.is_online)]

    def get_admins(self, only_online: bool = True) -> list[str]:
        return [username for username, user in self.users.items() if isinstance(user, Admin) and (not only_online or only_online and user.is_online)]

    def is_admin(self, username: str) -> bool:
        return isinstance(self.users.get(username, Viewer('')), Admin)

    def is_player(self, username: str) -> bool:
        return isinstance(self.users.get(username, Viewer('')), Player)

    def get_user(self, username: str) -> dict:
        user = self.users.get(username)
        if user is None:
            self.__throw_if_allowed(UserManagementError, 'Tried to get info about non-existent user')
            return {}
        return user.json()

    def get_player(self, username: str) -> dict:
        user = self.users.get(username)
        if user is None:
            self.__throw_if_allowed(UserManagementError, 'Tried to get info about non-existent user')
            return {}
        if not isinstance(user, Player):
            self.__throw_if_allowed(UserManagementError, 'Tried to get submission info about non-player')
            return {}
        user_info = user.json()
        user_info['submissions-left'] = MAX_SUBMISSION_COUNT - len(user_info['submissions'])
        return user_info

    def add_admin(self, username: str):
        if any(isinstance(user, Admin) for user in self.users.values() if user.is_online):  # check whether there is active admin already
            self.__throw_if_allowed(UserManagementError, 'Tried to add an admin, however it already exists and online')
            return
        if self.users.get(username) is None:
            admin = Admin(username=username)
            admin.is_online = True
            self.users[username] = admin
        elif isinstance(self.users[username], Admin):
            self.users[username].is_online = True
        else:
            self.__throw_if_allowed(UserManagementError, 'Tried to add admin, however non-admin with such nickname already exists')

    def add_viewer(self, username: str):
        if self.users.get(username) is None:
            viewer = Viewer(username=username)
            viewer.is_online = True
            self.users[username] = viewer
        elif isinstance(self.users[username], Viewer):
            self.users[username].is_online = True
        else:
            self.__throw_if_allowed(UserManagementError, 'Tried to add player, however non-viewer with such nickname already exists')

    def add_player(self, username: str):
        if self.users.get(username) is None:
            player = Player(username=username, points=0.0)
            player.is_online = True
            self.users[username] = player
        elif isinstance(self.users[username], Player):
            self.users[username].is_online = True
        else:
            self.__throw_if_allowed(UserManagementError, 'Tried to add player, however non-player with such nickname already exists')

    def remove_user(self, username: str):
        if self.users.get(username):
            self.users[username].is_online = False

    def update_leaderboard(self, modification: dict[str, int], mode: str = 'add'):
        assert mode in {'add', 'set'}, 'Invalid mode type'

        for username, score in modification.items():
            if not self.users.get(username):  # TODO: add warning
                self.add_player(username)
            if isinstance(self.users[username], Player):
                self.users[username].points = float(score if mode == 'set' else self.users[username].points + score)
            else:
                self.__throw_if_allowed(UserManagementError, 'Attempting to set score for non-player. You sure what you are doing?')

    def set_leaderboard(self, leaderboard: dict[str, float]):
        for username, score in leaderboard.items():
            if not self.users.get(username):  # TODO: add warning
                self.add_player(username)

            if isinstance(self.users[username], Player):
                self.users[username].points = float(score)
            else:
                self.__throw_if_allowed(UserManagementError, 'Attempting to set score for non-player. You sure what you are doing?')

    def __throw_if_allowed(self, error: GameErrors, name: str):
        if self.throw_exceptions:
            raise error(name)

    def reset_submissions(self):
        for username, user in self.users.items():
            if isinstance(user, Player):
                self.users[username].clear_submissions()

    def add_submission(self, username: str, song_info: str, submitter: str):
        if not self.users.get(username):
            self.__throw_if_allowed(UserManagementError, 'Attempted to add submission to non-existent user')
            return
        if not isinstance(self.users[username], Player):
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
        if not isinstance(self.users[username], Player):
            self.__throw_if_allowed(UserManagementError, 'Attempted to score submission to non-player')
            return
        if not isinstance(submission_id, int) or submission_id < 0 or submission_id >= len(self.users[username].get_submissions()):
            self.__throw_if_allowed(RuntimeError, 'Attempted to score non-existent submission (invalid id)')
            return
        self.users[username].submissions[submission_id].set_score(score)

    def get_user_submissions(self, username: str) -> list[dict]:
        if not self.users.get(username):
            self.__throw_if_allowed(UserManagementError, 'Attempted to get submissions of non-existent user')
            return
        if not isinstance(self.users[username], Player):
            self.__throw_if_allowed(UserManagementError, 'Attempted to get submissions of non-player')
            return
        return self.users[username].json()['submissions']

