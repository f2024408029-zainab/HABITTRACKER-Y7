# 🌱 Smart Habit Tracker with Streak Analytics

A web-based habit, mood & wellness tracker built with **Python (Flask)** and **SQLite**.
Users sign up, log in, and get a dashboard with an interactive monthly calendar. Tapping
any day opens a form to record: mood (5 options) → emotions (20 options) → hobby →
health check-in → a written note. Based on the selected mood, the app recommends
relevant hobbies/activities. A bottom navigation bar gives access to your **Profile**,
**Monthly Mood Flow** chart, **Streak Analytics**, and **Settings** (with 5 selectable
color themes).

## ✨ Features

- **Signup / Login** — password-hashed auth using Flask sessions
- **Interactive monthly calendar** — click any day to open the entry form
- **5 mood options**, **20 emotions**, **hobby chips**, **health chips**,
**free-text note** — everything is click-to-select except the note
- **Smart recommendations** — suggested activities based on your logged mood
- **Profile page** — shows username, user ID, total entries
- **Monthly Mood Flow** — bar-chart visualization of mood across the month
- **Streak Analytics** — current streak & longest streak of logged days
- **5 themes** (Ocean, Sunset, Forest, Midnight, Sakura) — switch anytime in Settings
- **SQLite database** — all data saved locally, no external services, no scraping

## 🛠️ Tech Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Backend    | Python 3, Flask                      |
| Database   | SQLite (raw `sqlite3`, no ORM)       |
| Frontend   | HTML (Jinja2 templates), CSS, vanilla JS |

## 📁 Project Structure

```
smart-habit-tracker/
├── backend/
│   ├── app.py            # Flask routes (auth, dashboard, entries, analytics pages)
│   ├── db.py             # All database access functions
│   ├── analytics.py      # Streak calculation + mood/emotion/hobby data + recommendations
│   └── requirements.txt
├── frontend/
│   ├── templates/        # Jinja2 HTML templates
│   └── static/
│       ├── css/          # style.css + themes.css
│       └── js/           # calendar.js + main.js
├── database/
│   └── schema.sql        # SQLite schema (users, entries, entry_emotions)
├── .gitignore
└── README.md
```

## 🚀 Running Locally

Install dependencies
pip install -r backend/requirements.txt

Run the app
python backend/app.py
```

Then open **http://127.0.0.1:5000** in your browser. The SQLite database file is
created automatically at `database/habit_tracker.db` on first run.

## 🌿 Git Branch Workflow

This repo is organized (per the OSSD project workflow) into three long-lived branches:

- **`frontend`** — HTML templates, CSS, JavaScript (`frontend/`)
- **`backend`** — Flask routes, business logic, analytics (`backend/`)
- **`database`** — schema design and any database migration scripts (`database/`)

Work happens on each branch for its respective layer, then gets merged into `main`
once tested. See the commands below to recreate this branch setup.