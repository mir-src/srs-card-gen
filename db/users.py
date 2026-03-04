from db.core import execute_insert, execute_write, fetch_one, fetch_all
from db.models import User
import bcrypt

def create_user(username: str, plain_text_password: str) -> int | None:
    password_bytes = plain_text_password.encode('utf-8')

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    sql = "INSERT INTO users (username, password_hash) VALUES (?,?)"
    return execute_insert(sql, (username, hashed_password.decode('utf-8')))

def verify_login(username: str, plain_text_password: str) -> User | None:
    user = fetch_one("SELECT * FROM users WHERE username = ?", (username,), User)

    if not user:
        return None
    
    password_bytes = plain_text_password.encode('utf-8')
    hash_bytes = user.password_hash.encode('utf-8')

    if bcrypt.checkpw(password_bytes, hash_bytes):
        return user
    else:
        return None

def delete_user(user_id: int) -> bool:
    return execute_write("DELETE FROM users WHERE id = ?", (user_id,))

def update_user(user_id: int, name: str) -> bool:
    return execute_write("UPDATE users SET name = ? WHERE id = ?", (name, user_id))

def get_user(user_id: int) -> User | None:
    return fetch_one("SELECT * FROM users WHERE id = ?", (user_id,), User)

def get_users() -> list | None:
    return fetch_all("SELECT * FROM users", (), User)
