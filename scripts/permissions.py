AUTOMATIC_DRIVEN_PERMISSIONS = {
    'is_online', 'is_on_the_leaderboard',
}

BASE_PERMISSIONS: dict[str, bool] = {
    'is_online':              False,
    'is_on_the_leaderboard':  True,

    'can_chat':               True,
    'can_play':               False,
    'can_change_stream':      False,
    'can_moderate_chat':      False,
    'can_check_submissions':  False,
    'can_change_leaderboard': False,
    'can_manage_users':       False,
}


VIEWER_PERMISSIONS: dict[str, bool] = {
    'is_online':              False,
    'is_on_the_leaderboard':  True,

    'can_chat':               True,
    'can_play':               False,
    'can_change_stream':      False,
    'can_moderate_chat':      False,
    'can_check_submissions':  False,
    'can_change_leaderboard': False,
    'can_manage_users':       False,
}


PLAYER_PERMISSIONS: dict[str, bool] = {
    'is_online':              False,
    'is_on_the_leaderboard':  True,

    'can_chat':               True,
    'can_play':               True,
    'can_change_stream':      False,
    'can_moderate_chat':      False,
    'can_check_submissions':  False,
    'can_change_leaderboard': False,
    'can_manage_users':       False,
}


ADMIN_PERMISSIONS: dict[str, bool] = {
    'is_online':              False,
    'is_on_the_leaderboard':  False,

    'can_chat':               True,
    'can_play':               False,
    'can_change_stream':      True,
    'can_moderate_chat':      True,
    'can_check_submissions':  True,
    'can_change_leaderboard': True,
    'can_manage_users':       True,
}


