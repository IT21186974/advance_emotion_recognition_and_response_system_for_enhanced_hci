import bcrypt
from database import get_user, create_user

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode()

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"bcrypt verification error: {e}")
        return False

def register_user(username: str, password: str):
    try:
        if get_user(username):
            return False  # User exists
        hashed = hash_password(password)
        create_user(username, hashed)
        return True
    except Exception as e:
        print(f"Error in register_user: {e}")
        return False

def authenticate_user(username: str, password: str) -> bool:
    try:
        user = get_user(username)
        if not user:
            return False
        return verify_password(password, user.hashed_password)
    except Exception as e:
        print(f"Error in authenticate_user: {e}")
        return False
