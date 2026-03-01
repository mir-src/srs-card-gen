from db.core import execute_write, execute_insert, fetch_one, fetch_all
from db.models import Card
from datetime import datetime, timezone

def create_card(deck_id: int, front: str, back: str, card_type: str = 'basic', state: str = 'new'):
    now = datetime.now()
    creation_date = now
    due_date = now
    return execute_insert("""
        INSERT INTO cards
        (deck_id,
        front,
        back,
        card_type,
        state,
        creation_date,
        due_date)
        VALUES (?,?,?,?,?,?,?)
    """,(
        deck_id,
        front,
        back,
        card_type,
        state,
        creation_date,
        due_date
    )
    )

def delete_card(card_id: int) -> bool:
    return execute_write("DELETE FROM cards WHERE id = ?", (card_id,))

def update_card(card: Card) -> bool:
    return execute_write("""
        UPDATE cards
        SET front = ?, 
            back = ?, 
            due_date = ?, 
            last_review_date = ?, 
            stability = ?, 
            difficulty = ?, 
            is_leech = ?, 
            is_suspended = ?, 
            state = ?
        WHERE id = ?
    """
    ,(
        card.front, 
        card.back, 
        card.due_date, 
        card.last_review_date, 
        card.stability, 
        card.difficulty, 
        card.is_leech, 
        card.is_suspended, 
        card.state, 
        card.id))

def get_card(card_id: int) -> Card | None:
    return fetch_one("SELECT * FROM cards WHERE id = ?", (card_id,), Card)

def get_cards(deck_id: int) -> list | None:
    return fetch_all("SELECT * FROM cards WHERE deck_id = ?", (deck_id,), Card)

def get_due_cards(deck_id: int):
    now = datetime.now(timezone.utc)
    sql = """
    SELECT * FROM cards
    WHERE deck_id = ? AND (due_date <= ? OR state = 'new')
    ORDER BY
        CASE state
            WHEN 'learning' THEN 0
            WHEN 'relearning' THEN 1
            WHEN 'review' THEN 2
            ELSE 3
        END ASC,
        due_date ASC
    """
    return fetch_all(sql, (deck_id, now,), Card)

