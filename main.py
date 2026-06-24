from flask import Flask, request, redirect, render_template_string, session
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

    return """
    <div style="font-family:sans-serif;text-align:center;margin-top:100px;">
        <h2>ログイン</h2>
        <form method="post">
            <input type="password" name="password" placeholder="パスワード">
            <br><br>
            <button>ログイン</button>
        </form>
    </div>
    """


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
# データ取得
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
    cur.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# =========================
# カレンダー生成
# =========================
def build_month(year, month, events):
    first = datetime(year, month, 1)
    next_month = datetime(year + (month // 12), (month % 12) + 1, 1)

    days = (next_month - first).days

    cal = []
    for d in range(1, days + 1):
        date_str = f"{year}-{month:02d}-{d:02d}"

        day_events = [
            e for e in events if e["date"] == date_str
        ]

        cal.append({
            "day": d,
            "events": day_events
        })

    return cal


# =========================
# UIテンプレート
# =========================
HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>デートカレンダー</title>

<style>
body{
    margin:0;
    font-family:sans-serif;
    background:#fff7d6;
}

.container{
    max-width:900px;
    margin:auto;
    padding:12px;
}

h1{
    text-align:center;
    font-size:18px;
}

.nav{
    display:flex;
    justify-content:space-between;
    margin:10px 0;
}

.nav a{
    background:#333;
    color:white;
    padding:8px 10px;
    border-radius:8px;
    text-decoration:none;
    font-size:13px;
}

.calendar{
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:3px;
}

.day{
    background:white;
    min-height:60px;
    border-radius:8px;
    padding:4px;
    font-size:10px;
}

.date{
    font-weight:bold;
}

.event{
    display:block;
    background:#333;
    color:white;
    font-size:9px;
    padding:2px 4px;
    margin-top:2px;
    border-radius:6px;
    text-decoration:none;
}

.card{
    background:white;
    padding:10px;
    border-radius:10px;
    margin-top:10px;
}

.detail{
    background:white;
    padding:10px;
    margin-top:10px;
    border-radius:10px;
}
</style>

</head>

<body>

<div class="container">

<h1>📅 {{year}}年 {{month}}月</h1>

<div class="nav">
    <a href="/?y={{py}}&m={{pm}}">← 前月</a>
    <a href="/?y={{ny}}&m={{nm}}">次月 →</a>
</div>

<!-- 追加 -->
<div class="card">
<form action="/add" method="post">
    <input name="title" placeholder="イベント名" required>
    <input type="date" name="date" required>
    <input name="place" placeholder="場所（任意）">
    <input name="memo" placeholder="メモ（任意）">
    <button>追加</button>
</form>
</div>

<!-- カレンダー -->
<div class="calendar">
{% for d in calendar %}
<div class="day">
    <div class="date">{{d.day}}</div>

    {% for e in d.events %}
        <a class="event" href="/event/{{e.id}}">
            {{e.title}}
        </a>
    {% endfor %}
</div>
{% endfor %}
</div>

<!-- 詳細 -->
{% if detail %}
<div class="detail">
    <h3>{{detail.title}}</h3>

    <p>📅 {{detail.date}}</p>
    <p>📍 {{detail.place or "未設定"}}</p>
    <p>📝 {{detail.memo or "なし"}}</p>

    <a href="/edit/{{detail.id}}">✏️ 編集</a>
    <a href="/delete/{{detail.id}}" onclick="return confirm('削除する？')">🗑 削除</a>

    <br><br>
    <a href="/">閉じる</a>
</div>
{% endif %}

</div>

</body>
</html>
"""


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

    return render_template_string(
        HTML,
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

    return render_template_string(
        HTML,
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

    return f"""
    <form method="post" style="padding:20px;">
        <input name="title" value="{event['title']}">
        <input name="date" type="date" value="{event['date']}">
        <input name="place" value="{event['place'] or ''}">
        <input name="memo" value="{event['memo'] or ''}">
        <button>保存</button>
    </form>
    """


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
# 起動
# =========================
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
