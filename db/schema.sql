CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    password_hash TEXT NOT NULL
);
CREATE TABLE decks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, 
    user_id INTEGER NOT NULL,
    learning_steps TEXT NOT NULL DEFAULT '1 10',
    relearning_steps TEXT NOT NULL DEFAULT '10',
    new_per_day INTEGER DEFAULT 20,
    reviews_per_day INTEGER DEFAULT 200,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id INTEGER NOT NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    creation_date TIMESTAMP NOT NULL,
    last_review_date TIMESTAMP,
    due_date TIMESTAMP,
    stability REAL DEFAULT 0.0,
    difficulty REAL DEFAULT 0.0,
    card_type TEXT NOT NULL
        CHECK (card_type IN ('basic', 'cloze', 'type')),
    is_leech INTEGER NOT NULL DEFAULT 0,
    is_suspended INTEGER NOT NULL DEFAULT 0,
    state TEXT NOT NULL
        CHECK(state IN ('new', 'learning', 'relearning', 'review')),
    step INTEGER DEFAULT 0
        CHECK(step >= 0),
    elapsed_days INTEGER DEFAULT 0
        CHECK(elapsed_days >= 0),
    scheduled_days INTEGER DEFAULT 0
        CHECK(scheduled_days >= 0),
    audio_front TEXT NOT NULL,
    audio_back TEXT NOT NULL,
    cloze_text TEXT NOT NULL,
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    deck_id INTEGER NOT NULL,
    rating INTEGER NOT NULL
        CHECK (rating BETWEEN 1 and 4),
    response_time REAL NOT NULL,
    review_datetime TIMESTAMP NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);
CREATE TABLE media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    media_type TEXT NOT NULL
        CHECK(media_type IN ('audio', 'image')),
    path TEXT NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);
