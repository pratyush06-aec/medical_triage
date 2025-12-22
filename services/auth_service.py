from database.db import create_user, authenticate_user

def register(email: str, password: str):
    user = create_user(email, password)
    if not user:
        return None
    return user


def login(email: str, password: str):
    user_id = authenticate_user(email, password)
    return user_id
