
from user import User





def get_users() -> tuple:
    """Return tuple of User's class objects"""
    return tuple(
            [User(name) for name in users_to_parse]
        )





