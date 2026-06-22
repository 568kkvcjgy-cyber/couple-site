from flask import Flask, request, redirect, render_template_string, session
import json, os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "change-this-secret"

DATA_FILE = "events.json"


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
        if request.form["password"] == "1234":
            session["auth"] = True
            return redirect("/")
        return "パスワード違う"

    return """
    <div style="font-family:sans-serif;padding:40px;text-align:center;">
        <h2>ログイン</h2>
        <form method="post">
            <input name="password" type="password" placeholder="パスワード">
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
# データ
# =========================
def load_events():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_events(events):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)


# =========================
# カレンダー
# =========================
def build_month(year, month, events):
    first = datetime(year, month, 1)
    next_month = datetime(year + (month // 12), (month % 12) + 1, 1)

    days = (next_month - first).days

    cal = []
    for d in range(1, days + 1):
        date_str = f"{year}-{str(month).zfill(2)}-{str(d).zfill(2)}"

        day_events = [
            {"i": i, **e}
            for i, e in enumerate(events)
            if e["date"] == date_str
        ]

        cal.append({"day": d, "events": day_events})

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
    max-width:900px;
    margin:auto;
    padding:12px;
    box-sizing:border-box;
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

/* カレンダー */
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
    overflow:hidden;
}

.date{
    font-weight:bold;
}

.event{
    background:#333;
    color:white;
    font-size:9px;
    padding:2px 4px;
    border-radius:6px;
    margin-top:2px;
    display:block;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

/* フォーム */
form{
    background:white;
    padding:10px;
    border-radius:10px;
    margin-bottom:10px;
}

input{
    width:100%;
    padding:8px;
    margin:4px 0;
    border:1px solid #ddd;
    border-radius:8px;
    box-sizing:border-box;
}

button{
    width:100%;
    padding:10px;
    border:none;
    background:#333;
    color:white;
    border-radius:8px;
}

/* 詳細 */
.detail{
    background:white;
    margin-top:10px;
    padding:10px;
    border-radius:10px;
}

/* カード */
.card{
    background:white;
    padding:10px;
    border-radius:10px;
    margin-top:10px;
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
        <a class="event" href="/event/{{e.i}}">
            {{e.title}}
        </a>
    {% endfor %}
</div>
{% endfor %}
</div>

{% if detail %}
<div class="detail">
    <h3>{{detail.title}}</h3>
    <p>📅 {{detail.date}}</p>
    <p>📍 {{detail.place if detail.place else "未設定"}}</p>
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
@app.route("/event/<int:i>")
@login_required
def event(i):
    events = load_events()

    now = datetime.now()
    y = now.year
    m = now.month

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
        detail=events[i]
    )


# =========================
# 追加
# =========================
@app.route("/add", methods=["POST"])
@login_required
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
# 起動
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)