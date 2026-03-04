from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class Card:
    # CONTENT
    id: int
    deck_id: int
    front: str
    back: str
    audio_front: str
    audio_back: str
    
    cloze_text: str = ''

    # TIMESTAMPS
    creation_date: datetime = field(default_factory=datetime.now)
    last_review_date: Optional[datetime] = None
    due_date: datetime = field(default_factory=datetime.now)

    stability: float = 0.0
    difficulty: float = 0.0

    card_type: str = 'basic' # 'cloze', 'type', 'basic'

    is_leech: bool = False
    is_suspended: bool = False

    state: str = 'new' # 'new', 'learning', 'relearning', 'review'

    step: int = 0
    
    elapsed_days: int = 0
    scheduled_days: int = 0


@dataclass
class Deck:
    id: int
    name: str
    user_id: int
    learning_steps: str = '1m 10m'
    relearning_steps: str = '10m'
    new_per_day: int = 20
    reviews_per_day: int = 200

@dataclass
class User:
    id: int
    name: str
    password_hash: str

@dataclass(frozen=True)
class Review:
    id: int
    card_id: int
    user_id: int
    deck_id: int
    rating: int
    response_time: float
    review_datetime: datetime = field(default_factory=datetime.now)
    state_at_review: str = ''

@dataclass
class Media:
    id: int
    card_id: int
    media_type: str
    path: str



