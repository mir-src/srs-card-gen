import fsrs
from db.models import Card
from datetime import datetime, timezone

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

def map_to_fsrs(my_card: Card) -> fsrs.Card:
    f_card = fsrs.Card()

    if my_card.state == 'new':
        return f_card
    
    f_card.due = my_card.due_date
    f_card.stability = my_card.stability if my_card.stability > 0 else None
    f_card.difficulty = my_card.difficulty if my_card.difficulty > 0 else None
    f_card.step = my_card.step
    f_card.state = STATE_TO_FSRS.get(my_card.state, fsrs.State.Learning)
    f_card.last_review = my_card.last_review_date

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

    new_f_card, review_log = f.review_card(f_card, rating_enum)

    updated_card = map_from_fsrs(my_card, new_f_card)
    return updated_card
