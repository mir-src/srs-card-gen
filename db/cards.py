from db.core import execute_write, execute_insert, fetch_one, fetch_all
from db.models import Card
from datetime import datetime, timezone, timedelta

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
            state = ?,
            step = ?
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
        card.step,
        card.id))

def get_card(card_id: int) -> Card | None:
    return fetch_one("SELECT * FROM cards WHERE id = ?", (card_id,), Card)

def get_cards(deck_id: int) -> list | None:
    return fetch_all("SELECT * FROM cards WHERE deck_id = ?", (deck_id,), Card)

def get_due_cards(deck_id: int):
    learn_ahead_time = datetime.now(timezone.utc) + timedelta(minutes=20)
    sql = """
    SELECT * FROM cards
    WHERE deck_id = ? AND (due_date <= ? OR state = 'new')
    ORDER BY 
        CASE state
            WHEN 'review' THEN 0     -- Overdue reviews first
            WHEN 'relearning' THEN 1 -- Forgotten cards next
            WHEN 'new' THEN 2        -- Brand new cards third
            WHEN 'learning' THEN 3   -- Current learning cards last
            ELSE 4
        END ASC,
        due_date ASC                 -- Then sort by time within those groups
    """
    return fetch_all(sql, (deck_id, learn_ahead_time,), Card)

