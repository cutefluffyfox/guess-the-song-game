import os
import pickle
from datetime import datetime, timedelta

from scripts.game import Game
from scripts.game_rules import SAVES_PATH, MAXIMUM_SAVES_AMOUNT, SAVE_IDLE_INTERVAL_SECONDS


os.makedirs(SAVES_PATH, exist_ok=True)
LAST_SAVE = datetime.now() - timedelta(days=1)


def get_oldest_file(path: str) -> str:
    return min([os.path.join(path, basename) for basename in os.listdir(path)], key=os.path.getctime)


def get_latest_file(path: str) -> str:
    return max([os.path.join(path, basename) for basename in os.listdir(path)], key=os.path.getctime)


def load_or_create(try_to_load: bool = True, room_name: str = 'main') -> Game:
    if not try_to_load or len(os.listdir(SAVES_PATH)) == 0:
        return Game(room_name, throw_exceptions=False)


    with open(get_latest_file(SAVES_PATH), 'rb') as save:
        game: Game = pickle.load(save)
    return game


def save_game(game: Game, bypass_time_constraint: bool = False):
    # if save is done too fast
    if not bypass_time_constraint and (datetime.now() - LAST_SAVE).seconds < SAVE_IDLE_INTERVAL_SECONDS:
        return

    while MAXIMUM_SAVES_AMOUNT < len(os.listdir(SAVES_PATH)):
        os.remove(get_oldest_file(SAVES_PATH))

    str_time = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
    with open(os.path.join(SAVES_PATH, f'game-{str_time}.pickle'), 'wb') as save:
        pickle.dump(game, save)
