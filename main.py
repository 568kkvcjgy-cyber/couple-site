from flask import Flask, request, redirect, render_template, session
import sqlite3
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "change-this-secret"

DB_FILE = "events.db"


# =========================
# 認証
# =========================
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not session.get("auth"):
            return redirect("/login")
        return f(*args, **kwargs)
    return wrap


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == "0212":
            session["auth"] = True
            return redirect("/")
        return "パスワードが違います"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================
# DB初期化
# =========================
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            place TEXT,
            memo TEXT
        )
        """)
        conn.commit()


init_db()


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# データ
# =========================
def load_events():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM events ORDER BY date")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_event(event_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM events WHERE id=?", (event_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# =========================
# カレンダー
# =========================
def build_month(year, month, events):
    first = datetime(year, month, 1)
    next_month = datetime(year + (month // 12), (month % 12) + 1, 1)

    days = (next_month - first).days

    cal = []
    for d in range(1, days + 1):
        date_str = f"{year}-{month:02d}-{d:02d}"

        day_events = [e for e in events if e["date"] == date_str]

        cal.append({
            "day": d,
            "events": day_events
        })

    return cal


# =========================
# HOME
# =========================
@app.route("/")
@login_required
def home():
    events = load_events()

    now = datetime.now()
    y = int(request.args.get("y", now.year))
    m = int(request.args.get("m", now.month))

    calendar = build_month(y, m, events)

    py, pm = (y, m - 1) if m > 1 else (y - 1, 12)
    ny, nm = (y, m + 1) if m < 12 else (y + 1, 1)

    return render_template(
        "index.html",
        year=y,
        month=m,
        calendar=calendar,
        py=py, pm=pm,
        ny=ny, nm=nm,
        detail=None
    )


# =========================
# 詳細
# =========================
@app.route("/event/<int:event_id>")
@login_required
def event(event_id):
    events = load_events()
    target = get_event(event_id)

    if not target:
        return "Not found", 404

    now = datetime.now()
    y, m = now.year, now.month

    calendar = build_month(y, m, events)

    py, pm = (y, m - 1) if m > 1 else (y - 1, 12)
    ny, nm = (y, m + 1) if m < 12 else (y + 1, 1)

    return render_template(
        "index.html",
        year=y,
        month=m,
        calendar=calendar,
        py=py, pm=pm,
        ny=ny, nm=nm,
        detail=target
    )


# =========================
# 追加
# =========================
@app.route("/add", methods=["POST"])
@login_required
def add():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO events (title, date, place, memo)
        VALUES (?, ?, ?, ?)
    """, (
        request.form["title"],
        request.form["date"],
        request.form.get("place", ""),
        request.form.get("memo", "")
    ))

    conn.commit()
    conn.close()

    return redirect("/")


# =========================
# 編集
# =========================
@app.route("/edit/<int:event_id>", methods=["GET", "POST"])
@login_required
def edit(event_id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        cur.execute("""
            UPDATE events
            SET title=?, date=?, place=?, memo=?
            WHERE id=?
        """, (
            request.form["title"],
            request.form["date"],
            request.form.get("place", ""),
            request.form.get("memo", ""),
            event_id
        ))

        conn.commit()
        conn.close()
        return redirect(f"/event/{event_id}")

    cur.execute("SELECT * FROM events WHERE id=?", (event_id,))
    event = cur.fetchone()
    conn.close()

    if not event:
        return "Not found", 404

    return render_template("edit.html", event=dict(event))


# =========================
# 削除
# =========================
@app.route("/delete/<int:event_id>")
@login_required
def delete(event_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM events WHERE id=?", (event_id,))

    conn.commit()
    conn.close()

    return redirect("/")


# =========================
# 起動（Render対応）
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
