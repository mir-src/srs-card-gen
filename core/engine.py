import fsrs
from db.models import Card, Deck
from datetime import datetime, timezone, timedelta
from db.core import get_connection 
import copy

STATE_TO_FSRS = {
    'new': fsrs.State.Learning,
    'review': fsrs.State.Review,
    'learning': fsrs.State.Learning,
    'relearning': fsrs.State.Relearning
}

FSRS_TO_STATE = {
    fsrs.State.Learning: 'learning',
    fsrs.State.Review: 'review',
    fsrs.State.Relearning: 'relearning'
}

def ensure_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def map_to_fsrs(my_card: Card) -> fsrs.Card:
    f_card = fsrs.Card()

    # If it has no memory, treat it as a pristine card
    if my_card.state == 'new' or my_card.stability == 0.0:
        return f_card
    
    f_card.due = ensure_utc(my_card.due_date) or datetime.now(timezone.utc)
    f_card.last_review = ensure_utc(my_card.last_review_date)
    
    f_card.stability = my_card.stability if my_card.stability > 0 else None
    f_card.difficulty = my_card.difficulty if my_card.difficulty > 0 else None
    f_card.step = my_card.step
    f_card.state = STATE_TO_FSRS.get(my_card.state, fsrs.State.Learning)

    return f_card

def map_from_fsrs(my_card: Card, f_card: fsrs.Card) -> Card:
    my_card.due_date = f_card.due
    my_card.last_review_date = f_card.last_review

    my_card.stability = f_card.stability if f_card.stability is not None else 0.0
    my_card.difficulty = f_card.difficulty if f_card.difficulty is not None else 0.0

    my_card.step = f_card.step if f_card.step is not None else 0
    my_card.state = FSRS_TO_STATE.get(f_card.state, 'learning')

    return my_card

def process_review(my_card: Card, rating_value: int) -> Card:
    f = fsrs.Scheduler()

    now = datetime.now(timezone.utc)
    f_card = map_to_fsrs(my_card)
    rating_enum = fsrs.Rating(rating_value)

    new_f_card, review_log = f.review_card(f_card, rating_enum, now)

    updated_card = map_from_fsrs(my_card, new_f_card)
    return updated_card

def convert_steps(steps: str) -> list:
    if type(steps) != str:
        return [10]

    if not steps or not steps.strip():
        return [10]

    steps_to_list = steps.replace('m', '').split()
    try:
        return [int(n) for n in steps_to_list]
    except ValueError:
        return [10]

def update_due_date(step_number: int) -> datetime:
    if step_number >= 0:
        now = datetime.now(timezone.utc)
        converted_step_number = timedelta(minutes=step_number)
        new_due_date = now + converted_step_number
        return new_due_date
    else:
        now = datetime.now(timezone.utc)
        return now  

def has_failed_learning(card_id: int) -> bool:
    with get_connection() as conn:
        sql = """ 
        SELECT COUNT(id) as c
        FROM reviews
        WHERE card_id = ?
        AND rating = 1
        AND state_at_review IN ('new', 'learning')
        """
        row = conn.execute(sql, (card_id,)).fetchone()
        return row['c'] > 0 if row else False

def router(my_card: Card, deck: Deck, user_rating: int):
    learning_steps = convert_steps(deck.learning_steps) or [1, 10]
    relearning_steps = convert_steps(deck.relearning_steps) or [10]

    learning_index = len(learning_steps)
    relearning_index = len(relearning_steps)

    if my_card.state == 'new':
        if user_rating == 1:
            my_card.step = 0
            new_due_date = update_due_date(learning_steps[my_card.step])
            my_card.due_date = new_due_date
            my_card.state = 'learning'

        elif user_rating == 2:
            my_card.step += 0
            new_due_date = update_due_date(learning_steps[my_card.step])
            my_card.due_date = new_due_date
            my_card.state = 'learning'

        elif user_rating == 3:
            my_card.step += 1
            if my_card.step < learning_index:
                new_due_date = update_due_date(learning_steps[my_card.step])
                my_card.due_date = new_due_date
                my_card.state = 'learning'

            else: 
                my_card = process_review(my_card=my_card, rating_value=user_rating)
                my_card.state = 'review'
                
                if has_failed_learning(my_card.id):
                    my_card.due_date = datetime.now(timezone.utc) + timedelta(days=1)
                
                return my_card
        else:
            my_card = process_review(my_card=my_card, rating_value=user_rating)
            return my_card

    elif my_card.state == 'learning':
        if my_card.step > learning_index:
            my_card.step = 0

        if user_rating == 1:
            my_card.step = 0
            new_due_date = update_due_date(learning_steps[my_card.step])
            my_card.due_date = new_due_date

        elif user_rating == 2:
            my_card.step += 0
            new_due_date = update_due_date(learning_steps[my_card.step])
            my_card.due_date = new_due_date
        
        elif user_rating == 3:
            my_card.step += 1
            if my_card.step < learning_index:
                new_due_date = update_due_date(learning_steps[my_card.step])
                my_card.due_date = new_due_date
            
            else: 
                my_card = process_review(my_card=my_card, rating_value=user_rating)
                my_card.state = 'review'
          
                if has_failed_learning(my_card.id):
                    my_card.due_date = datetime.now(timezone.utc) + timedelta(days=1)
                
                return my_card
        else: # Easy (4)
            my_card = process_review(my_card=my_card, rating_value=user_rating)
            my_card.state = 'review'
            return my_card

    elif my_card.state == 'relearning':
        if my_card.step > relearning_index:
            my_card.step = 0

        if user_rating == 1:
            my_card.step = 0
            new_due_date = update_due_date(relearning_steps[my_card.step])
            my_card.due_date = new_due_date
        elif user_rating == 2:
            my_card.step += 0
            new_due_date = update_due_date(relearning_steps[my_card.step])
            my_card.due_date = new_due_date
        elif user_rating == 3:
            my_card.step += 1
            if my_card.step < relearning_index:
                new_due_date = update_due_date(relearning_steps[my_card.step])
                my_card.due_date = new_due_date
            else:
                my_card = process_review(my_card=my_card, rating_value=user_rating)
                my_card.state = 'review'
                return my_card
        else:
            my_card = process_review(my_card=my_card, rating_value=user_rating)
            my_card.state = 'review'
            return my_card

    elif my_card.state == 'review':
        if user_rating == 1:
            my_card = process_review(my_card=my_card, rating_value=user_rating)
            my_card.step = 0
            new_due_date = update_due_date(relearning_steps[my_card.step])
            my_card.due_date = new_due_date
            my_card.state = 'relearning'

            my_card.lapses += 1
            if my_card.lapses >= deck.leech_threshold:
                my_card.is_leech = True
                my_card.is_suspended = True
        else:
            return process_review(my_card=my_card, rating_value=user_rating)
            
    return my_card

def get_intervals(current_card: Card, deck: Deck) -> list:
    intervals = []
    now = datetime.now(timezone.utc)

    for i in range(1, 5):
        card_copy = copy.deepcopy(current_card)
        routed_card = router(card_copy, deck, i)
        delta = routed_card.due_date - now
        minutes = delta.total_seconds() / 60
        if minutes < 60:
            intervals.append(f"{max(1, int(minutes))}m")
        elif minutes < 1440:
            intervals.append(f"{int(minutes // 60)}h")
        elif delta.days < 30:
            intervals.append(f"{delta.days}d")
        elif delta.days < 365:
            intervals.append(f"{delta.days // 30}mo")
        else:
            intervals.append(f"{delta.days // 365}y")

    return intervals

def get_start_of_day(day_start: int):
    now = datetime.now(timezone.utc)
    shifted_time = now - timedelta(hours=day_start)
    shifted_time = shifted_time.replace(hour=0, minute=0, second=0, microsecond=0)
    shifted_time += timedelta(hours=day_start)
    return shifted_time



