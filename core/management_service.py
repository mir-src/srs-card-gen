import os
from db.cards import delete_card, get_card, update_card
from db.decks import delete_deck
from db.users import delete_user
from db.core import fetch_all 
from db.models import Media

def safe_delete_user(user_id: int) -> bool:
    sql = """
        SELECT m.* FROM media m
        JOIN cards c ON m.card_id = c.id
        JOIN decks d ON c.deck_id = d.id
        WHERE d.user_id = ?
    """
    
    media_files = fetch_all(sql, (user_id,), Media)

    for media in media_files:
        if os.path.exists(media.path):
            os.remove(media.path)

    return delete_user(user_id)

def safe_delete_deck(deck_id: int) -> bool:
    sql = """
        SELECT m.* FROM media m
        JOIN cards c ON m.card_id = c.id
        WHERE c.deck_id = ?
    """
    
    media_files = fetch_all(sql, (deck_id,), Media)

    for media in media_files:
        if os.path.exists(media.path):
            os.remove(media.path)

    return delete_deck(deck_id)

def edit_card_text(card_id: int, new_front: str, new_back: str) -> bool:
    card = get_card(card_id)
    if not card:
        return False
    
    if card.front != new_front:
        sql = """
            SELECT * FROM media WHERE card_id = ?
        """
        media_files = fetch_all(sql, (card_id,), Media)
        for media in media_files:
            if os.path.exists(media.path):
                os.remove(media.path)
    
    card.front = new_front
    card.back = new_back

    return update_card(card)
