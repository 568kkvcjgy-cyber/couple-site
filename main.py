from flask import Flask, request, redirect, render_template_string
import json, os

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
# UIテンプレ
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
    padding:16px;
}

h1{
    text-align:center;
    margin:10px 0 20px;
}

form{
    background:white;
    padding:15px;
    border-radius:16px;
    margin-bottom:16px;
    box-shadow:0 6px 18px rgba(0,0,0,0.08);
}

input{
    width:100%;
    padding:10px;
    margin:5px 0 10px;
    border-radius:10px;
    border:1px solid #ddd;
}

button{
    width:100%;
    padding:12px;
    border:none;
    border-radius:10px;
    background:#333;
    color:white;
}

.calendar{
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:4px;
    margin-bottom:20px;
}

.day{
    background:white;
    min-height:70px;
    border-radius:10px;
    padding:4px;
    font-size:11px;
    box-shadow:0 2px 8px rgba(0,0,0,0.05);
}

.date{
    font-weight:700;
}

.event{
    background:#333;
    color:white;
    font-size:10px;
    padding:2px 4px;
    border-radius:6px;
    margin-top:3px;
}

.card{
    background:white;
    padding:14px;
    border-radius:14px;
    margin-bottom:10px;
    box-shadow:0 6px 18px rgba(0,0,0,0.06);
}

.actions{
    margin-top:8px;
    display:flex;
    gap:10px;
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
    <input name="place" placeholder="場所" required>
    <button>追加</button>
</form>

<!-- カレンダー -->
<div class="calendar" id="calendar"></div>

<!-- カード一覧 -->
{% for i,e in events %}
<div class="card">
    <b>{{ e.title }}</b><br>
    📅 {{ e.date }}<br>
    📍 {{ e.place }}

    <div class="actions">
        <a href="/event/{{ i }}">詳細</a>
        <a href="/edit/{{ i }}">編集</a>
        <a href="/delete/{{ i }}">削除</a>
    </div>
</div>
{% endfor %}

</div>

<script>
const events = {{ events_json|safe }};

function buildCalendar(){
    const cal = document.getElementById("calendar");

    const now = new Date();
    const y = now.getFullYear();
    const m = now.getMonth();

    const first = new Date(y,m,1);
    const last = new Date(y,m+1,0);

    cal.innerHTML = "";

    for(let i=0;i<first.getDay();i++){
        cal.innerHTML += "<div></div>";
    }

    for(let d=1; d<=last.getDate(); d++){
        const ds = `${y}-${String(m+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;

        let html = `<div class="day"><div class="date">${d}</div>`;

        events.forEach(e=>{
            if(e.date === ds){
                html += `<div class="event">${e.title}</div>`;
            }
        });

        html += "</div>";
        cal.innerHTML += html;
    }
}

buildCalendar();
</script>

</body>
</html>
"""


# =========================
# トップ
# =========================
@app.route("/")
def home():
    events = load_events()

    # Jinja用
    indexed_events = list(enumerate(events))

    return render_template_string(
        HTML,
        events=indexed_events,
        events_json=json.dumps(events)
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
        "place": request.form["place"]
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
        "place": request.form["place"]
    }
    save_events(events)
    return redirect("/")


# =========================
# Render起動
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)