from flask import Flask, request, redirect, render_template_string
import json, os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "events.json"


def load_events():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_events(events):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)


# =========================
# 月カレンダー生成
# =========================
def build_month(year, month, events):
    first = datetime(year, month, 1)
    next_month = datetime(year + (month // 12), (month % 12) + 1, 1)

    days = (next_month - first).days

    cal = []

    for d in range(1, days + 1):
        date_str = f"{year}-{str(month).zfill(2)}-{str(d).zfill(2)}"

        day_events = [e for e in events if e["date"] == date_str]

        cal.append({
            "day": d,
            "events": day_events
        })

    return cal


# =========================
# UI
# =========================
HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;500;700&display=swap" rel="stylesheet">

<title>デートカレンダー</title>

<style>
body{
    margin:0;
    font-family:'Noto Sans JP', sans-serif;
    background:#fff7d6;
}

.container{
    max-width:800px;
    margin:auto;
    padding:14px;
}

h1{
    text-align:center;
}

/* ナビ */
.nav{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin:10px 0 15px;
}

.nav a{
    text-decoration:none;
    background:#333;
    color:white;
    padding:8px 12px;
    border-radius:10px;
    font-size:14px;
}

/* カレンダー */
.calendar{
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:4px;
}

.day{
    background:white;
    min-height:70px;
    border-radius:10px;
    padding:4px;
    font-size:10px;
    box-shadow:0 3px 10px rgba(0,0,0,0.05);
}

.date{
    font-weight:700;
}

.event{
    background:#333;
    color:white;
    font-size:9px;
    padding:2px 4px;
    border-radius:6px;
    margin-top:3px;
}

/* フォーム */
form{
    background:white;
    padding:14px;
    border-radius:14px;
    margin-bottom:15px;
}

input{
    width:100%;
    padding:10px;
    margin:6px 0;
    border-radius:10px;
    border:1px solid #ddd;
}

button{
    width:100%;
    padding:12px;
    border:none;
    background:#333;
    color:white;
    border-radius:10px;
}
</style>
</head>

<body>

<div class="container">

<h1>📅 {{year}}年 {{month}}月</h1>

<div class="nav">
    <a href="/?y={{prev_y}}&m={{prev_m}}">← 前月</a>
    <a href="/?y={{next_y}}&m={{next_m}}">次月 →</a>
</div>

<form action="/add" method="post">
    <input name="title" placeholder="イベント名" required>
    <input type="date" name="date" required>
    <input name="place" placeholder="場所（任意）">
    <button>追加</button>
</form>

<div class="calendar">
{% for d in calendar %}
<div class="day">
    <div class="date">{{d.day}}</div>

    {% for e in d.events %}
        <div class="event">{{e.title}}</div>
    {% endfor %}
</div>
{% endfor %}
</div>

</div>

</body>
</html>
"""


# =========================
# トップ
# =========================
@app.route("/")
def home():
    events = load_events()

    now = datetime.now()

    y = int(request.args.get("y", now.year))
    m = int(request.args.get("m", now.month))

    calendar = build_month(y, m, events)

    # 前月・次月
    prev_m = m - 1
    prev_y = y
    if prev_m == 0:
        prev_m = 12
        prev_y -= 1

    next_m = m + 1
    next_y = y
    if next_m == 13:
        next_m = 1
        next_y += 1

    return render_template_string(
        HTML,
        year=y,
        month=m,
        calendar=calendar,
        prev_y=prev_y,
        prev_m=prev_m,
        next_y=next_y,
        next_m=next_m
    )


# =========================
# 追加
# =========================
@app.route("/add", methods=["POST"])
def add():
    events = load_events()

    events.append({
        "title": request.form["title"],
        "date": request.form["date"],
        "place": request.form.get("place", "")
    })

    save_events(events)
    return redirect("/")


# =========================
# Render起動
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)