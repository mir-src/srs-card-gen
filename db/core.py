import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "app.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

# Connection
def get_connection():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Initialize
def initialize_database():
    with get_connection() as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        tables_exist = cursor.fetchone()

        if tables_exist:
            return
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

# DatabaseWriteError
class DatabaseWriteError(Exception):
    pass

# Write Helper
def execute_write(sql: str, params: tuple = ()) -> bool:
    try:
        with get_connection() as conn:
            conn.execute(sql, params)
            return True
    except Exception as e:
        print(f"DEBUG SQL ERROR: {e}") 
        raise DatabaseWriteError(f"Failed to insert: {e}")

# Insert Helper
def execute_insert(sql: str, params: tuple = ()) -> int | None:
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, params)
            return cursor.lastrowid if cursor else None
    except sqlite3.IntegrityError:
        raise DatabaseWriteError("Failed to insert into database.")

# fecth_one Helper
def fetch_one(sql: str, params: tuple, model_class):
    with get_connection() as conn:
        cursor = conn.execute(sql,params)
        row = cursor.fetchone()
        return model_class(**dict(row)) if row else None
    
# fetch_all Helper
def fetch_all(sql: str, params: tuple, model_class) -> list:
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        objects = [model_class(**dict(row)) for row in rows]
        return objects
    