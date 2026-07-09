# My Life Journal

A web-based personal journal, mood tracker, and focus companion built with
**Python (Flask)** and **SQLite**. Users sign up, log in, and land on a
**View** page with a monthly calendar. Tapping any day opens a form to record
mood (5 options), emotions (20 options), a hobby, a health check-in, and a
written note — with mood-based hobby suggestions after saving. A slide-out
side menu gives access to a monthly **Summary**, **Mood Flow** analytics,
**Streak** tracking, **Themes**, and **Settings**. The home page also
surfaces a rotating **Daily Motivation** note and a **Focus Mode** timer
whose sessions feed into the analytics.

## Features

**Signup / Login** — password-hashed auth using Flask sessions
**Slide-out side menu** — View, Mood Flow, Streaks, Themes, Settings, Log Out
**Interactive monthly calendar** — click any day to log an entry
**5 mood options**, **20 emotions**, **hobby chips**, **health chips**,
**free-text note** — everything is click-to-select except the note
**Smart recommendations** — suggested activities based on your logged mood
**Monthly Summary view** — pick a year/month to see a journal digest, hobby counts, and a suggestions summary for that period
**Mood Flow analytics** — chart-based (no emojis), plus a Focus Time chart
**Streak Analytics** — current streak & longest streak of logged days
**Daily Motivation** — a new rotating note shown each day
**Focus Mode** — set an HH:MM:SS timer; completed sessions are logged and
  shown in analytics
**5 themes** (Ocean, Sunset, Forest, Midnight, Sakura) — switch anytime
**SQLite database** — all data saved locally, no external services, no scraping

## Tech Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Backend    | Python 3, Flask                      |
| Database   | SQLite (raw `sqlite3`, no ORM)       |
| Frontend   | HTML (Jinja2 templates), CSS, vanilla JS |

## Project Structure

```
my-life-journal/
├── backend/
│   ├── app.py     
│   ├── db.py  
│   ├── analytics.py 
│   └── requirements.txt
├── frontend/
│   ├── templates/         
│   └── static/
│       ├── css/           
│       └── js/            
├── database/
│   └── schema.sql         
├── .gitignore
└── README.md
```

## Running Locally

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd my-life-journal

# 2. create a virtual environment
python3 -m venv venv
source venv/bin/activate      

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Run the app
python backend/app.py
```

Then open **http://127.0.0.1:5000** in your browser. The SQLite database file is
created automatically at `database/habit_tracker.db` on first run.

## Git Branch Workflow

This repo is organized into three long-lived branches:

- **`develop/frontend`** — HTML templates, CSS, JavaScript (`frontend/`)
- **`develop/backend`** — Flask routes, business logic, analytics (`backend/`)
- **`develop/database`** — schema design (`database/`)

Work happens on each branch for its respective layer, then gets merged into
`main` once tested. `main` is always the runnable, up-to-date version of the
app.

## License
Built as an OSSD course project. Free to use and adapt for learning purposes.
