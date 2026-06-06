import pytest
from datetime import datetime, timezone, timedelta
import fsrs
from unittest.mock import MagicMock

# IMPORT
from core.engine import (
    STATE_TO_FSRS, FSRS_TO_STATE, ensure_utc, map_to_fsrs, map_from_fsrs,
    process_review, convert_steps, update_due_date, has_failed_learning,
    router, get_intervals, get_start_of_day
)

# Dummy Card Model
class Card:
    def __init__(self, id=1, state='new', stability=0.0, difficulty=0.0, step=0, due_date=None, last_review_date=None, lapses=0):
        self.id = id
        self.state = state
        self.stability = stability
        self.difficulty = difficulty
        self.step = step
        self.due_date = due_date
        self.last_review_date = last_review_date
        self.lapses = lapses
        self.is_leech = False
        self.is_suspended = False

# Dummy Deck
class Deck:
    def __init__(self, learning_steps="1m 10m", relearning_steps="10m", leech_threshold=8):
        self.learning_steps = learning_steps
        self.relearning_steps = relearning_steps
        self.leech_threshold = leech_threshold

# --- TESTS ---

def test_ensure_utc():
    assert ensure_utc(None) is None
    
    naive_dt = datetime(2026, 6, 6, 12, 0, 0)
    aware_dt = ensure_utc(naive_dt)
    assert aware_dt.tzinfo == timezone.utc
    
    # Test already aware datetime
    already_aware = datetime(2026, 6, 6, 12, 0, 0, tzinfo=timezone.utc)
    assert ensure_utc(already_aware) == already_aware

def test_convert_steps():
    assert convert_steps("1m 10m") == [1, 10]
    assert convert_steps("10") == [10]
    assert convert_steps("1 10 1440") == [1, 10, 1440]
    assert convert_steps("") == [10]
    assert convert_steps(None) == [10]
    assert convert_steps("invalid_string") == [10]  

def test_map_to_fsrs_new_card():
    my_card = Card(state='new', stability=0.0)
    f_card = map_to_fsrs(my_card)
    
    assert f_card.state == fsrs.State.Learning
    assert f_card.stability is None

# Database TESTS

def test_has_failed_learning(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_cursor.fetchone.return_value = {'c': 1}
    mock_conn.execute.return_value = mock_cursor
    
    mock_get_conn = mocker.patch('core.engine.get_connection')
    mock_get_conn.return_value.__enter__.return_value = mock_conn

    result = has_failed_learning(1)
    
    assert result is True
    mock_conn.execute.assert_called_once()

# Router TESTS

def test_router_new_card_rating_1(mocker):
    fixed_now = datetime(2026, 6, 6, 12, 0, 0, tzinfo=timezone.utc)
    
    mocker.patch('core.engine.datetime')
    mocker.patch('core.engine.update_due_date', return_value=fixed_now + timedelta(minutes=1))

    my_card = Card(state='new', step=0)
    deck = Deck(learning_steps="1m 10m")
    
    updated_card = router(my_card, deck, user_rating=1)
    
    assert updated_card.state == 'learning'
    assert updated_card.step == 0
    assert updated_card.due_date == fixed_now + timedelta(minutes=1)

def test_router_review_card_rating_1_leech(mocker):
    mocker.patch('core.engine.process_review', side_effect=lambda my_card, rating_value: my_card)
    mocker.patch('core.engine.update_due_date', return_value=datetime.now(timezone.utc))
    
    my_card = Card(state='review', lapses=7)
    deck = Deck(leech_threshold=8)
    
    updated_card = router(my_card, deck, user_rating=1)
    
    assert updated_card.state == 'relearning'
    assert updated_card.lapses == 8
    assert updated_card.is_leech is True
    assert updated_card.is_suspended is True

# Interval TESTS

def test_get_intervals(mocker):
    my_card = Card(state='new', step=0)
    deck = Deck()
    
    now = datetime(2026, 6, 6, 12, 0, 0, tzinfo=timezone.utc)
    
    mocker.patch('core.engine.datetime')
    import core.engine
    core.engine.datetime.now.return_value = now
    
    def mock_router(card, deck, rating):
        if rating == 1:
            card.due_date = now + timedelta(minutes=5)
        elif rating == 2:
            card.due_date = now + timedelta(hours=5)
        elif rating == 3:
            card.due_date = now + timedelta(days=5)
        else:
            card.due_date = now + timedelta(days=40)
        return card

    mocker.patch('core.engine.router', side_effect=mock_router)
    
    intervals = get_intervals(my_card, deck)
    
    assert intervals == ['5m', '5h', '5d', '1mo']