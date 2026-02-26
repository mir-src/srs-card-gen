from db.core import execute_insert, execute_write, fetch_one, fetch_all
from db.models import User

def create_user(name: str) -> int | None:
    return execute_insert("INSERT INTO users (name) VALUES (?)", (name,))

def delete_user(user_id: int) -> bool:
    return execute_write("DELETE FROM users WHERE id = ?", (user_id,))

def update_user(user_id: int, name: str) -> bool:
    return execute_write("UPDATE users SET name = ? WHERE id = ?", (name, user_id))

def get_user(user_id: int) -> User | None:
    return fetch_one("SELECT * FROM users WHERE id = ?", (user_id,), User)

def get_users() -> list | None:
    return fetch_all("SELECT * FROM users", (), User)
