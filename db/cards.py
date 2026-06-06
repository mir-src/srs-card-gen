from db.core import execute_write, execute_insert, fetch_one, fetch_all, get_connection
from core.engine import get_start_of_day
from db.models import Card, Deck, Review
from datetime import datetime, timezone, timedelta

def create_card(deck_id: int, front: str = '', back = '', audio_front: str = '', audio_back: str = '', cloze_text: str = '', card_type: str = 'basic'):
    now = datetime.now(timezone.utc)
    creation_date = now
    due_date = now
    step = 0
    lapses = 0
    state = 'new'
    return execute_insert("""
        INSERT INTO cards
        (deck_id,
        front,
        back,
        audio_front,
        audio_back,
        cloze_text,
        creation_date,
        due_date,
        card_type,
        state,
        step,
        lapses)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """,(
        deck_id,
        front,
        back,
        audio_front,
        audio_back,
        cloze_text,
        creation_date,
        due_date,
        card_type,
        state,
        step,
        lapses
    )
    )

def delete_card(card_id: int) -> bool:
    return execute_write("DELETE FROM cards WHERE id = ?", (card_id,))

def update_card(card: Card) -> bool:
    print(f"DEBUG: Updating Card {card.id} - State: {card.state}, Due: {card.due_date}")
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
            step = ?,
            lapses = ?
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
        card.lapses,
        card.id))

def get_card(card_id: int) -> Card | None:
    return fetch_one("SELECT * FROM cards WHERE id = ?", (card_id,), Card)

def get_cards(deck_id: int) -> list | None:
    return fetch_all("SELECT * FROM cards WHERE deck_id = ?", (deck_id,), Card)

def get_due_cards(deck: Deck, user_id: int, day_start: int) -> list:
    learn_ahead_time = datetime.now(timezone.utc) + timedelta(minutes=20)
    start_time = get_start_of_day(day_start) or 4
    
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
        "SELECT * FROM cards WHERE deck_id = ? AND state IN ('learning', 'relearning') AND IFNULL(is_suspended, 0) = 0 AND due_date <= ?",
        (deck.id, learn_ahead_time), Card) or []
    
    review_cards = fetch_all(
        "SELECT * FROM cards WHERE deck_id = ? AND state = 'review' AND IFNULL(is_suspended, 0) = 0 AND due_date <= ? ORDER BY due_date ASC LIMIT ?", 
        (deck.id, learn_ahead_time, remaining_reviews), Card) or []
    
    new_cards = fetch_all(
        "SELECT * FROM cards WHERE deck_id = ? AND state = 'new' AND IFNULL(is_suspended, 0) = 0 ORDER BY id ASC LIMIT ?",
        (deck.id, remaining_new), Card) or []
    
    current_time = datetime.now(timezone.utc)
    
    overdue_learning = []
    future_learning = []
    
    for c in learning_cards:
        c_due = c.due_date.replace(tzinfo=timezone.utc) if c.due_date.tzinfo is None else c.due_date
        
        if c_due <= current_time:
            overdue_learning.append(c)
        else:
            future_learning.append(c)
            
    overdue_learning.sort(key=lambda c: c.due_date)
    future_learning.sort(key=lambda c: c.due_date)
    
    return overdue_learning + review_cards + new_cards + future_learning

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
