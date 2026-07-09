"""
db.py
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "habit_tracker.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")


def get_connection():
    """Return a new sqlite3 connection with foreign keys enabled and
    rows accessible like dictionaries."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the database file + tables if they don't already exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


# ---------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------

def create_user(username, email, password_hash):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_user_by_username(username):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return row


def get_user_by_email(email):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def update_user_theme(user_id, theme):
    conn = get_connection()
    conn.execute("UPDATE users SET theme = ? WHERE id = ?", (theme, user_id))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------
# Entry helpers
# ---------------------------------------------------------------

def get_entry(user_id, entry_date):
    conn = get_connection()
    entry = conn.execute(
        "SELECT * FROM entries WHERE user_id = ? AND entry_date = ?",
        (user_id, entry_date),
    ).fetchone()
    emotions = []
    if entry:
        emotions = [
            r["emotion"]
            for r in conn.execute(
                "SELECT emotion FROM entry_emotions WHERE entry_id = ?", (entry["id"],)
            ).fetchall()
        ]
    conn.close()
    if not entry:
        return None
    data = dict(entry)
    data["emotions"] = emotions
    return data


def get_entries_for_month(user_id, year, month):
    """Return a dict keyed by day-number (int) -> entry dict, for a given month."""
    prefix = f"{year:04d}-{month:02d}-"
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM entries WHERE user_id = ? AND entry_date LIKE ? ORDER BY entry_date",
        (user_id, prefix + "%"),
    ).fetchall()
    result = {}
    for r in rows:
        day = int(r["entry_date"].split("-")[2])
        result[day] = dict(r)
    conn.close()
    return result


def get_all_entries(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM entries WHERE user_id = ? ORDER BY entry_date",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_entry(user_id, entry_date, mood, hobby, health, note, emotions):
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM entries WHERE user_id = ? AND entry_date = ?",
        (user_id, entry_date),
    ).fetchone()

    if existing:
        entry_id = existing["id"]
        conn.execute(
            """UPDATE entries
               SET mood = ?, hobby = ?, health = ?, note = ?, updated_at = datetime('now')
               WHERE id = ?""",
            (mood, hobby, health, note, entry_id),
        )
        conn.execute("DELETE FROM entry_emotions WHERE entry_id = ?", (entry_id,))
    else:
        cur = conn.execute(
            """INSERT INTO entries (user_id, entry_date, mood, hobby, health, note)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, entry_date, mood, hobby, health, note),
        )
        entry_id = cur.lastrowid

    for emo in emotions:
        conn.execute(
            "INSERT INTO entry_emotions (entry_id, emotion) VALUES (?, ?)",
            (entry_id, emo),
        )

    conn.commit()
    conn.close()
    return entry_id


# ---------------------------------------------------------------
# Focus Mode helpers
# ---------------------------------------------------------------

def add_focus_session(user_id, session_date, duration_seconds):
    conn = get_connection()
    conn.execute(
        "INSERT INTO focus_sessions (user_id, session_date, duration_seconds) VALUES (?, ?, ?)",
        (user_id, session_date, duration_seconds),
    )
    conn.commit()
    conn.close()


def get_focus_sessions_for_month(user_id, year, month):
    """Return dict day-number -> total focus seconds logged that day."""
    prefix = f"{year:04d}-{month:02d}-"
    conn = get_connection()
    rows = conn.execute(
        """SELECT session_date, SUM(duration_seconds) as total
           FROM focus_sessions
           WHERE user_id = ? AND session_date LIKE ?
           GROUP BY session_date""",
        (user_id, prefix + "%"),
    ).fetchall()
    conn.close()
    result = {}
    for r in rows:
        day = int(r["session_date"].split("-")[2])
        result[day] = r["total"]
    return result


def get_total_focus_seconds(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT SUM(duration_seconds) as total FROM focus_sessions WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return row["total"] or 0
