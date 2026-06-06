import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

from db.cards import get_due_cards, Card, Deck 

def test_get_due_cards_respects_daily_limits(mocker):
    fixed_now = datetime(2026, 6, 6, 12, 0, 0, tzinfo=timezone.utc)
    
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now
            
    mocker.patch('db.cards.datetime', MockDatetime)
    mocker.patch('db.cards.get_start_of_day', return_value=fixed_now - timedelta(hours=8))

    deck = Deck(
        id=1, 
        user_id=1, 
        name="Japanese",
        learning_steps="1m 10m", 
        relearning_steps="1m",
        new_per_day=20,
        reviews_per_day=50 
    )
    
    # 3. Mock the Database Connection Context Manager
    mock_conn = MagicMock()
    
    # Create separate cursor mocks for the two sequential SELECT COUNT queries
    mock_cursor_new = MagicMock()
    mock_cursor_new.fetchone.return_value = {'c': 0}   # 0 new cards studied
    
    mock_cursor_review = MagicMock()
    mock_cursor_review.fetchone.return_value = {'c': 50} # 50 reviews studied (Limit Hit!)
    
    mock_conn.execute.side_effect = [mock_cursor_new, mock_cursor_review]
    
    mock_get_connection = mocker.patch('db.core.get_connection')
    mock_get_connection.return_value.__enter__.return_value = mock_conn

    mock_fetch_all = mocker.patch('db.cards.fetch_all')
    mock_fetch_all.side_effect = [
        [],  # learning_cards
        [],  # review_cards
        []   # new_cards
    ]

    result = get_due_cards(deck, deck.user_id, day_start=4)

    assert result == []
    
    review_call_args = mock_fetch_all.call_args_list[1][0] 
    assert review_call_args[1][2] == 0