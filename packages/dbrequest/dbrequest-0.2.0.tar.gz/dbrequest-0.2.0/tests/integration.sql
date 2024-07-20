create table IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    is_sign_in INTEGER DEFAULT 0,
    datetime INT DEFAULT NULL,
    ratio REAL DEFAULT 0,
    hash BLOB,
    custom TEXT
);