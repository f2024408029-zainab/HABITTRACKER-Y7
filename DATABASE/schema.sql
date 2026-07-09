-- ============================================================
-- daily journal with Streak Analytics
-- Database Schema (SQLite)
-- ============================================================

PRAGMA foreign_keys = ON;

-- Registered users (signup/login)
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    theme         TEXT NOT NULL DEFAULT 'ocean',   -- one of 5 preset themes
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- One entry per user per calendar day. mood is 1-5 (1 = Awful ... 5 = Great)
CREATE TABLE IF NOT EXISTS entries (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entry_date   TEXT NOT NULL,                     -- format YYYY-MM-DD
    mood         INTEGER CHECK (mood BETWEEN 1 AND 5),
    hobby        TEXT DEFAULT '',
    health       TEXT DEFAULT '',
    note         TEXT DEFAULT '',
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, entry_date)
);

-- Emotions picked for that day's entry (multi-select from list of 20)
CREATE TABLE IF NOT EXISTS entry_emotions (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id  INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    emotion   TEXT NOT NULL
);

-- Focus Mode sessions: user selects HH:MM:SS, session length is logged per day
CREATE TABLE IF NOT EXISTS focus_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_date    TEXT NOT NULL,               -- format YYYY-MM-DD
    duration_seconds INTEGER NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_focus_user_date ON focus_sessions(user_id, session_date);

CREATE INDEX IF NOT EXISTS idx_entries_user_date ON entries(user_id, entry_date);
CREATE INDEX IF NOT EXISTS idx_entry_emotions_entry ON entry_emotions(entry_id);
