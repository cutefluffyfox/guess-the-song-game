class GameErrors(RuntimeError):
    pass

class GameConfigError(GameErrors):
    pass


class GameRuleViolation(GameErrors):
    pass


class UserManagementError(GameErrors):
    pass
