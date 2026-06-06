from db.core import execute_insert, execute_write, fetch_one, fetch_all, get_connection
from db.models import User
import bcrypt

def create_user(user: str, plain_text_password: str, day_start_hour: int = 4) -> int | None:
    password_bytes = plain_text_password.encode('utf-8')

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    sql = "INSERT INTO users (name, password_hash, day_start_hour) VALUES (?,?,?)"
    return execute_insert(sql, (user, hashed_password.decode('utf-8'), day_start_hour))

def update_user_day_start(id: str, new_day_start: int):
    sql = "UPDATE users SET day_start_hour = ? WHERE id = ?"
    return execute_write(sql, (new_day_start, id, ))

def get_day_start(id: str):
    with get_connection() as conn:
        cursor = conn.execute("SELECT day_start_hour FROM users WHERE id = ?", (id,)) 
        row = cursor.fetchone() 

        if row and "day_start_hour" in dict(row):
            return dict(row)["day_start_hour"]

        return 4

def verify_login(name: str, plain_text_password: str) -> User | None:
    user = fetch_one("SELECT * FROM users WHERE name = ?", (name,), User) 

    if not user:
        return None
    
    password_bytes = plain_text_password.encode('utf-8')
    hash_bytes = user.password_hash.encode('utf-8')

    if bcrypt.checkpw(password_bytes, hash_bytes):
        return user
    else:
        return None
    
def update_password(user_id: int, new_hashed_password: str = ''):
    sql = """
    UPDATE users
    SET password_hash = ?
    WHERE id = ?
    """
    return execute_write(sql, (new_hashed_password, user_id))

def delete_user(user_id: int) -> bool:
    return execute_write("DELETE FROM users WHERE id = ?", (user_id,))

def update_user(user_id: int, name: str) -> bool:
    return execute_write("UPDATE users SET name = ? WHERE id = ?", (name, user_id))

def get_user(user_id: int) -> User | None:
    return fetch_one("SELECT * FROM users WHERE id = ?", (user_id,), User)

def get_users() -> list | None:
    return fetch_all("SELECT * FROM users", (), User)
