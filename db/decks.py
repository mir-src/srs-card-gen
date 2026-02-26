from db.core import execute_insert, execute_write, fetch_one, fetch_all
from db.models import Deck

def create_deck(user_id: int, name: str) -> int | None:
    return execute_insert("INSERT INTO decks (name, user_id) VALUES (?, ?)", (name, user_id))

def delete_deck(deck_id: int) -> bool:
    return execute_write("DELETE FROM decks WHERE id = ?", (deck_id,))

def update_deck(deck_id: int, name: str) -> bool:
    return execute_write("UPDATE decks SET name = ? WHERE id = ?", (name, deck_id))

def get_deck(deck_id: int) -> Deck | None:
    return fetch_one("SELECT * FROM decks WHERE id = ?", (deck_id,), Deck)

def get_decks(user_id: int) -> list | None:
    return fetch_all("SELECT * FROM decks WHERE user_id = ?", (user_id,), Deck)



