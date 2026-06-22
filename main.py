from flask import Flask, request, redirect, render_template_string
import json
import os

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
    font-family:"Yu Gothic";
    background:#fff7d6;
}

.container{
    max-width:900px;
    margin:auto;
    padding:20px;
}

h1{
    text-align:center;
    color:#444;
}

form{
    background:white;
    padding:15px;
    border-radius:15px;
    margin-bottom:20px;
}

input{
    width:100%;
    padding:10px;
    margin:5px 0;
    border-radius:10px;
    border:1px solid #ddd;
}

button{
    padding:10px 15px;
    border:none;
    background:#444;
    color:white;
    border-radius:10px;
}

.calendar{
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:5px;
    background:white;
    padding:10px;
    border-radius:15px;
}

.day{
    min-height:80px;
    border:1px solid #eee;
    padding:5px;
    font-size:12px;
}

.date{
    font-weight:bold;
    font-size:12px;
}

.event{
    background:#444;
    color:white;
    padding:2px 4px;
    border-radius:6px;
    margin-top:3px;
    font-size:11px;
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

<div id="calendar" class="calendar"></div>

</div>

<script>
const events = {{events|safe}};

function buildCalendar(){
    const cal = document.getElementById("calendar");

    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth();

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month+1, 0);

    const start = firstDay.getDay();
    const days = lastDay.getDate();

    cal.innerHTML = "";

    for(let i=0;i<start;i++){
        cal.innerHTML += "<div></div>";
    }

    for(let d=1; d<=days; d++){
        const dateStr = `${year}-${String(month+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;

        let html = `<div class="day"><div class="date">${d}</div>`;

        events.forEach(e=>{
            if(e.date === dateStr){
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


@app.route("/")
def home():
    events = load_events()
    return render_template_string(HTML, events=json.dumps(events))


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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)