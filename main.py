from flask import Flask, request, redirect, render_template_string
import json, os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "events.json"


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
# 年間カレンダー用
# =========================
def get_year_matrix(year, events):
    months = []
    for m in range(1, 13):
        first = datetime(year, m, 1)
        next_month = datetime(year + (m // 12), (m % 12) + 1, 1)

        days = (next_month - first).days

        month_data = {
            "month": m,
            "days": []
        }

        for d in range(1, days + 1):
            date_str = f"{year}-{str(m).zfill(2)}-{str(d).zfill(2)}"

            day_events = [
                e for e in events if e["date"] == date_str
            ]

            month_data["days"].append({
                "day": d,
                "events": day_events
            })

        months.append(month_data)

    return months


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
    overflow-x:hidden;
}

.container{
    max-width:1000px;
    margin:auto;
    padding:14px;
}

h1{
    text-align:center;
    margin:10px 0 20px;
}

/* フォーム */
form{
    background:white;
    padding:14px;
    border-radius:16px;
    margin-bottom:16px;
    box-shadow:0 6px 18px rgba(0,0,0,0.08);
}

input{
    width:100%;
    padding:10px;
    margin:6px 0 10px;
    border-radius:10px;
    border:1px solid #ddd;
    box-sizing:border-box;
}

button{
    width:100%;
    padding:12px;
    border:none;
    border-radius:10px;
    background:#333;
    color:white;
}

/* カード */
.card{
    background:white;
    padding:14px;
    border-radius:14px;
    margin-bottom:10px;
    box-shadow:0 6px 16px rgba(0,0,0,0.06);
}

/* カレンダー */
.calendar{
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:4px;
    margin-bottom:20px;
}

.day{
    background:white;
    min-height:60px;
    border-radius:10px;
    padding:4px;
    font-size:10px;
}

.date{
    font-weight:700;
    font-size:11px;
}

.event{
    background:#333;
    color:white;
    font-size:9px;
    padding:2px 4px;
    border-radius:6px;
    margin-top:3px;
}

/* 年間 */
.year-wrap{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
    gap:10px;
}

.month{
    background:white;
    border-radius:14px;
    padding:10px;
    box-shadow:0 4px 14px rgba(0,0,0,0.05);
}

.month h3{
    margin:0 0 8px;
    font-size:14px;
}

.small-day{
    font-size:9px;
    color:#666;
    margin-bottom:2px;
}

.actions{
    display:flex;
    gap:8px;
    margin-top:6px;
    font-size:12px;
}

a{
    color:#333;
    text-decoration:none;
}
</style>
</head>

<body>

<div class="container">

<h1>📅 デートカレンダー</h1>

<form action="/add" method="post">
    <input name="title" placeholder="イベント名" required>
    <input type="date" name="date" required>
    <input name="place" placeholder="場所（任意）">
    <button>追加</button>
</form>

<h2>📆 年間カレンダー</h2>
<div class="year-wrap">
{% for m in year %}
<div class="month">
    <h3>{{ m.month }}月</h3>

    {% for d in m.days %}
        <div class="small-day">
            {{ d.day }}
            {% for e in d.events %}
                <div class="event">{{ e.title }}</div>
            {% endfor %}
        </div>
    {% endfor %}
</div>
{% endfor %}
</div>

<h2>📌 イベント一覧</h2>

{% for i,e in events %}
<div class="card">
    <b>{{ e.title }}</b><br>
    📅 {{ e.date }}<br>
    📍 {{ e.place if e.place else "未設定" }}

    <div class="actions">
        <a href="/edit/{{ i }}">編集</a>
        <a href="/delete/{{ i }}">削除</a>
    </div>
</div>
{% endfor %}

</div>

</body>
</html>
"""


# =========================
# ルート
# =========================
@app.route("/")
def home():
    events = load_events()
    year = get_year_matrix(datetime.now().year, events)

    return render_template_string(
        HTML,
        events=list(enumerate(events)),
        year=year
    )


# =========================
# 追加（場所任意）
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
# 削除
# =========================
@app.route("/delete/<int:i>")
def delete(i):
    events = load_events()
    if 0 <= i < len(events):
        events.pop(i)
    save_events(events)
    return redirect("/")


# =========================
# 編集
# =========================
@app.route("/edit/<int:i>")
def edit(i):
    events = load_events()
    e = events[i]

    return f"""
    <div style="padding:20px;font-family:Noto Sans JP;">
        <h2>編集</h2>
        <form action="/update/{i}" method="post">
            <input name="title" value="{e['title']}">
            <input type="date" name="date" value="{e['date']}">
            <input name="place" value="{e['place']}">
            <button>更新</button>
        </form>
        <a href="/">戻る</a>
    </div>
    """


@app.route("/update/<int:i>", methods=["POST"])
def update(i):
    events = load_events()
    events[i] = {
        "title": request.form["title"],
        "date": request.form["date"],
        "place": request.form.get("place", "")
    }
    save_events(events)
    return redirect("/")


# =========================
# Render起動
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)