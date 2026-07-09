"""
analytics.py
------------
Python helper functions for:
  1. Streak calculation (current streak + longest streak of logged days)
  2. Monthly mood-flow data (for the chart on the dashboard)
  3. Mood -> hobby recommendation engine
"""

from datetime import date, datetime, timedelta

MOODS = {
    5: {"label": "Great", "emoji": "😄"},
    4: {"label": "Good", "emoji": "🙂"},
    3: {"label": "Okay", "emoji": "😐"},
    2: {"label": "Low", "emoji": "🙁"},
    1: {"label": "Awful", "emoji": "😢"},
}

EMOTIONS = [
    "Happy", "Excited", "Grateful", "Calm", "Confident",
    "Proud", "Loved", "Hopeful", "Relaxed", "Content",
    "Anxious", "Stressed", "Sad", "Angry", "Tired",
    "Lonely", "Overwhelmed", "Bored", "Frustrated", "Nervous",
]

HOBBY_SUGGESTIONS = {
    5: ["Go for a run", "Try a new recipe", "Call a friend", "Start a creative project", "Dance to your favorite playlist"],
    4: ["Read a book", "Go for a walk outside", "Journal about your day", "Learn something new online", "Tidy up your space"],
    3: ["Take a short walk", "Listen to a podcast", "Stretch for 10 minutes", "Do a puzzle", "Sketch or doodle"],
    2: ["Try deep breathing for 5 minutes", "Listen to calming music", "Write down 3 things you're grateful for", "Take a warm shower", "Reach out to someone you trust"],
    1: ["Practice slow breathing", "Wrap yourself in a blanket and rest", "Talk to someone you trust", "Write your thoughts down freely", "Step outside for fresh air"],
}

HEALTH_OPTIONS = [
    "Drank enough water", "Slept 7+ hours", "Exercised", "Ate a balanced meal",
    "Took a break from screens", "Meditated",
]

HOBBY_OPTIONS = [
    "Reading", "Gaming", "Painting/Drawing", "Music", "Cooking/Baking",
    "Sports", "Gardening", "Photography", "Writing", "Gym/Workout",
]

# ---------------------------------------------------------------
# Daily motivation notes — a short rotating list. A new one is
# shown each calendar day, deterministically based on day-of-year,
# so it's the same note all day but changes tomorrow.
# ---------------------------------------------------------------
DAILY_MOTIVATION_NOTES = [
    "Small steps every day add up to big change.",
    "You don't have to be perfect, you just have to show up.",
    "Progress, not perfection.",
    "Be proud of how far you've come.",
    "One honest entry today is better than a perfect one you never write.",
    "Rest is productive too.",
    "Your feelings are valid, whatever they are today.",
    "Consistency beats intensity.",
]


def get_daily_motivation(for_date=None):
    """Deterministically rotate through the notes list, one per calendar day."""
    d = for_date or date.today()
    index = d.timetuple().tm_yday % len(DAILY_MOTIVATION_NOTES)
    return DAILY_MOTIVATION_NOTES[index]


def recommend_hobbies(mood):
    """Return a list of suggested activities based on a 1-5 mood score."""
    if mood is None:
        return []
    mood = int(mood)
    return HOBBY_SUGGESTIONS.get(mood, [])


def calculate_streaks(entries):
    """
    entries: list of dicts with 'entry_date' keys (format YYYY-MM-DD),
             representing days the user logged *something*.
    Returns dict with current_streak and longest_streak (in days).
    """
    if not entries:
        return {"current_streak": 0, "longest_streak": 0}

    dates = sorted({datetime.strptime(e["entry_date"], "%Y-%m-%d").date() for e in entries})

    longest = 1
    run = 1
    for i in range(1, len(dates)):
        if dates[i] - dates[i - 1] == timedelta(days=1):
            run += 1
            longest = max(longest, run)
        else:
            run = 1

    # current streak: count backwards from today (or yesterday, so a user
    # who hasn't logged *today yet* doesn't lose their streak)
    today = date.today()
    date_set = set(dates)
    current = 0
    cursor = today
    if today not in date_set:
        cursor = today - timedelta(days=1)
    while cursor in date_set:
        current += 1
        cursor -= timedelta(days=1)

    return {"current_streak": current, "longest_streak": longest}


def monthly_mood_flow(entries, year, month):
    """
    Returns a list of {day, mood} dicts (mood may be None) for every day
    of the given month, sorted ascending -- handy for line-chart plotting.
    """
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    mood_by_day = {}
    for e in entries:
        d = datetime.strptime(e["entry_date"], "%Y-%m-%d").date()
        if d.year == year and d.month == month:
            mood_by_day[d.day] = e["mood"]

    return [{"day": d, "mood": mood_by_day.get(d)} for d in range(1, days_in_month + 1)]


def mood_summary(entries):
    """Count how many times each mood (1-5) appears across all entries."""
    counts = {m: 0 for m in MOODS}
    for e in entries:
        if e.get("mood"):
            counts[int(e["mood"])] = counts.get(int(e["mood"]), 0) + 1
    return counts


def build_month_summary(entries, year, month):
    """
    Build the data needed for the 'Summary' view: a plain-text digest of
    the month's notes, a count of hobbies logged, and a de-duplicated list
    of hobby suggestions that were relevant that month (based on moods logged).
    """
    month_entries = [
        e for e in entries
        if e["entry_date"].startswith(f"{year:04d}-{month:02d}-")
    ]
    month_entries.sort(key=lambda e: e["entry_date"])

    # Text digest: one line per day that has a note
    lines = []
    for e in month_entries:
        if e.get("note"):
            mood_label = MOODS[int(e["mood"])]["label"] if e.get("mood") else "No mood logged"
            lines.append(f"{e['entry_date']} ({mood_label}): {e['note']}")
    digest_text = "\n".join(lines) if lines else "No journal notes recorded for this month yet."

    # Hobby counts
    hobby_counts = {}
    for e in month_entries:
        if e.get("hobby"):
            hobby_counts[e["hobby"]] = hobby_counts.get(e["hobby"], 0) + 1

    # Suggestions: union of recommendations for every distinct mood logged this month
    moods_logged = {int(e["mood"]) for e in month_entries if e.get("mood")}
    suggestions = []
    for m in sorted(moods_logged, reverse=True):
        for s in recommend_hobbies(m):
            if s not in suggestions:
                suggestions.append(s)

    return {
        "digest_text": digest_text,
        "hobby_counts": hobby_counts,
        "suggestions": suggestions,
        "entry_count": len(month_entries),
    }


def format_duration(total_seconds):
    """Format a number of seconds as H:MM:SS for display."""
    total_seconds = int(total_seconds or 0)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h}:{m:02d}:{s:02d}"
