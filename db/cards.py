from db.core import execute_write, execute_insert, fetch_one, fetch_all, get_connection
from core.engine import get_start_of_day
from db.models import Card, Deck, Review
from datetime import datetime, timezone, timedelta

def create_card(deck_id: int, front: str, back: str, card_type: str = 'basic', state: str = 'new', audio_front: str = '', audio_back: str = '', cloze_text: str = ''):
    now = datetime.now(timezone.utc)
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
        due_date,
        audio_front,
        audio_back,
        cloze_text)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """,(
        deck_id,
        front,
        back,
        card_type,
        state,
        creation_date,
        due_date,
        audio_front,
        audio_back,
        cloze_text
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

def get_due_cards(deck: Deck, user_id: int):
    learn_ahead_time = datetime.now(timezone.utc) + timedelta(minutes=20)
    start_time = get_start_of_day(4)
    
    from db.core import get_connection
    with get_connection() as conn:
        n_row = conn.execute(
            "SELECT COUNT(DISTINCT card_id) as c FROM reviews WHERE deck_id = ? AND user_id = ? AND review_datetime >= ? AND state_at_review = 'new'", 
            (deck.id, user_id, start_time)).fetchone()

        r_row = conn.execute(
            "SELECT COUNT(DISTINCT card_id) as c FROM reviews WHERE deck_id = ? AND user_id = ? AND review_datetime >= ? AND state_at_review != 'new'", 
            (deck.id, user_id, start_time)).fetchone()
        
        new_studied_today = n_row['c'] if n_row else 0
        reviews_studied_today = r_row['c'] if r_row else 0

    remaining_new = max(0, deck.new_per_day - new_studied_today)
    remaining_reviews = max(0, deck.reviews_per_day - reviews_studied_today)

    learning_cards = fetch_all(
        "SELECT * FROM cards WHERE deck_id = ? AND state IN ('learning', 'relearning') AND due_date <= ?",
        (deck.id, learn_ahead_time), Card) or []
    
    review_cards = fetch_all(
        "SELECT * FROM cards WHERE deck_id = ? AND state = 'review' AND due_date <= ? LIMIT ?", 
        (deck.id, learn_ahead_time, remaining_reviews), Card) or []
    
    new_cards = fetch_all(
        "SELECT * FROM cards WHERE deck_id = ? AND state = 'new' LIMIT ?",
        (deck.id, remaining_new), Card) or []
    
    current_time = datetime.now(timezone.utc)
    
    # 1. Overdue stuff first, 2. New cards second, 3. Future learn-ahead cards last
    def get_priority(c):
        # We handle naive vs aware datetimes safely just in case
        c_due = c.due_date.replace(tzinfo=timezone.utc) if c.due_date.tzinfo is None else c.due_date
        
        if c.state == 'new':
            return 1 # Priority 2: New
        elif c_due <= current_time:
            return 0 # Priority 1: Overdue
        else:
            return 2 # Priority 3: Learn-ahead (future)

    queue = learning_cards + review_cards + new_cards
    
    # Sort primarily by the priority tier, and secondarily by exact due date
    queue.sort(key=lambda c: (get_priority(c), c.due_date))

    return queue

def log_review(card_id: int, user_id: int, deck_id: int, rating: int, response_time: float, state_at_review: str = ''):
    review_datetime = datetime.now(timezone.utc)
    sql = """
    INSERT INTO reviews
    (card_id,
    user_id,
    deck_id,
    rating,
    review_datetime,
    response_time,
    state_at_review)
    VALUES (?,?,?,?,?,?,?)
    """
    return execute_insert(sql, (card_id, user_id, deck_id, rating, review_datetime, response_time, state_at_review))
