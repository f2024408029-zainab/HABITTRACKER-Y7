"""
app.py
"""

import calendar as pycalendar
from datetime import date, datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

import db
import analytics

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
)
app.secret_key = "dev-secret-key-change-this-in-production"  # OK for local/OSSD demo use

THEMES = ["ocean", "sunset", "forest", "midnight", "sakura"]


# ---------------------------------------------------------------
# Helpers

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def current_user():
    if "user_id" not in session:
        return None
    return db.get_user_by_id(session["user_id"])


# ---------------------------------------------------------------
# Auth routes

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("signup.html")

        if db.get_user_by_username(username):
            flash("That username is already taken.", "error")
            return render_template("signup.html")

        if db.get_user_by_email(email):
            flash("An account with that email already exists.", "error")
            return render_template("signup.html")

        password_hash = generate_password_hash(password)
        user_id = db.create_user(username, email, password_hash)
        session["user_id"] = user_id
        flash("Account created! Welcome aboard.", "success")
        return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = db.get_user_by_username(username)
        if user is None:
            user = db.get_user_by_email(username.lower())

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username/email or password.", "error")
            return render_template("login.html")

        session["user_id"] = user["id"]
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------
# Dashboard / calendar

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()

    year = request.args.get("year", type=int) or date.today().year
    month = request.args.get("month", type=int) or date.today().month

    cal = pycalendar.Calendar(firstweekday=6)  # Sunday-first calendar
    month_days = cal.monthdayscalendar(year, month)  # weeks of [0 padded days]
    entries_by_day = db.get_entries_for_month(user["id"], year, month)

    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month % 12 + 1
    next_year = year + 1 if month == 12 else year

    return render_template(
        "dashboard.html",
        user=user,
        month_days=month_days,
        entries_by_day=entries_by_day,
        year=year,
        month=month,
        month_name=pycalendar.month_name[month],
        prev_month=prev_month, prev_year=prev_year,
        next_month=next_month, next_year=next_year,
        today=date.today().isoformat(),
        moods=analytics.MOODS,
        themes=THEMES,
    )


@app.route("/day/<entry_date>")
@login_required
def day_detail(entry_date):
    """Returns the day-entry modal content as HTML (used via fetch by JS)."""
    user = current_user()
    entry = db.get_entry(user["id"], entry_date)
    recommendations = analytics.recommend_hobbies(entry["mood"] if entry else None)
    return render_template(
        "_day_modal.html",
        entry_date=entry_date,
        entry=entry,
        moods=analytics.MOODS,
        emotions_list=analytics.EMOTIONS,
        health_options=analytics.HEALTH_OPTIONS,
        hobby_options=analytics.HOBBY_OPTIONS,
        recommendations=recommendations,
    )


@app.route("/day/<entry_date>", methods=["POST"])
@login_required
def save_day(entry_date):
    user = current_user()
    mood = request.form.get("mood", type=int)
    hobby = request.form.get("hobby", "").strip()
    health = request.form.get("health", "").strip()
    note = request.form.get("note", "").strip()
    emotions = request.form.getlist("emotions")

    db.upsert_entry(user["id"], entry_date, mood, hobby, health, note, emotions)
    recommendations = analytics.recommend_hobbies(mood)
    return jsonify({"status": "ok", "recommendations": recommendations})


# ---------------------------------------------------------------
# Bottom pages: profile, mood flow, streaks, and setting he 4 options

@app.route("/profile")
@login_required
def profile():
    user = current_user()
    entries = db.get_all_entries(user["id"])
    streaks = analytics.calculate_streaks(entries)
    return render_template("profile.html", user=user, streaks=streaks, total_entries=len(entries))


@app.route("/mood-flow")
@login_required
def mood_flow():
    user = current_user()
    year = request.args.get("year", type=int) or date.today().year
    month = request.args.get("month", type=int) or date.today().month
    entries = db.get_all_entries(user["id"])
    flow = analytics.monthly_mood_flow(entries, year, month)
    summary = analytics.mood_summary(entries)
    return render_template(
        "mood_flow.html", user=user, flow=flow, year=year, month=month,
        month_name=pycalendar.month_name[month], moods=analytics.MOODS, summary=summary,
    )


@app.route("/streaks")
@login_required
def streaks():
    user = current_user()
    entries = db.get_all_entries(user["id"])
    streak_data = analytics.calculate_streaks(entries)
    return render_template(
        "streaks.html", user=user, streaks=streak_data, entries=entries, moods=analytics.MOODS
    )


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = current_user()
    if request.method == "POST":
        theme = request.form.get("theme")
        if theme in THEMES:
            db.update_user_theme(user["id"], theme)
            flash("Theme updated!", "success")
        return redirect(url_for("settings"))
    return render_template("settings.html", user=user, themes=THEMES)


# ---------------------------------------------------------------
# Entry point

if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
