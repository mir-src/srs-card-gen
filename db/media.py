from db.core import execute_insert

def create_media(card_id: int, media_type: str, path: str) -> int | None:
    
    return execute_insert(
        "INSERT INTO media (card_id, media_type, path) VALUES (?,?,?)",
        (card_id, media_type, path)
    ) 

