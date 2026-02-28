import fsrs
from db.models import Card, Deck
from datetime import datetime, timezone, timedelta

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

# To finish later
"""def convert_steps(steps: str) -> list:
    steps_to_list = steps.replace('m', '').split()
    make_int_list = [int(n) for n in steps_to_list]
    return make_int_list 

def update_due_date(step_number: int) -> datetime:
    now = datetime.now(timezone.utc)
    converted_step_number = timedelta(minutes=step_number)
    new_due_date = now + converted_step_number
    return new_due_date

def router(my_card: Card, deck: Deck, user_rating: int):
    learning_steps = convert_steps(deck.learning_steps)
    relearning_steps = convert_steps(deck.relearning_steps)
    learning_index = len(learning_steps)
    relearning_index = len(relearning_steps)

    if my_card.state == 'new':
        if user_rating == 1:
            my_card.step = 0
            my_card.state = 'learning'
            new_due_date = update_due_date(learning_steps[my_card.step])
            my_card.due_date = new_due_date


        elif user_rating == 2:
            my_card.step += 0
            my_card.state = 'learning'
            new_due_date = update_due_date(learning_steps[my_card.step])
            my_card.due_date = new_due_date

        elif user_rating == 3:
            my_card.step += 1
            if my_card.step != learning_index:
                new_due_date = update_due_date(learning_steps[my_card.step])
                my_card.due_date = new_due_date
            elif my_card.step == learning_index:
                my_card.state = 'review'
                return process_review(my_card=my_card, rating_value=user_rating)
        else:
            my_card.state = 'review'
            return process_review(my_card=my_card, rating_value=user_rating)

    elif my_card.state == 'learning':
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
            if my_card.step != learning_index:
                new_due_date = update_due_date(learning_steps[my_card.step])
                my_card.due_date = new_due_date
            if my_card.step >= learning_index:
                my_card.state = 'review'
                return process_review(my_card=my_card, rating_value=user_rating)
        else:
            my_card.state = 'review'
            return process_review(my_card=my_card, rating_value=user_rating)

    elif my_card.state == 'relearning':
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
            my_card.state = 'review'
            return process_review(my_card=my_card, rating_value=user_rating)
        else:
            my_card.state = 'review'
            return process_review(my_card=my_card, rating_value=user_rating)

    elif my_card.state == 'review':
        if user_rating == 1:
            my_card.step = 0
            new_due_date = update_due_date(relearning_steps[my_card.step])
            my_card.due_date = new_due_date
            my_card.state = 'relearning'
        else:
            if my_card.step == relearning_index:
                return process_review(my_card=my_card, rating_value=user_rating) 
            else:
                my_card.state = 'relearning'
    return my_card
"""