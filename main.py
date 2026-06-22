from flask import Flask, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "your-secret-key-change-this"

DATA_FILE = "events.json"
PASSWORD = "0212"  # ←ここを2人だけのパスに変更


# =========================
# データ処理
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
# ログインチェック
# =========================
def is_login():
    return session.get("auth")


# =========================
# ログイン
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == PASSWORD:
            session["auth"] = True
            return redirect("/")
        return "パスワード違う"

    return """
    <html>
    <body style="font-family:Yu Gothic;background:#fff8e7;text-align:center;padding:100px;">
        <h2>🔐 ログイン</h2>
        <form method="post">
            <input name="password" type="password" style="padding:10px;">
            <button>入る</button>
        </form>
    </body>
    </html>
    """


# =========================
# ログアウト
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================
# 一覧
# =========================
@app.route("/")
def home():
    if not is_login():
        return redirect("/login")

    events = load_events()

    cards = ""

    for i, e in enumerate(events):
        cards += f"""
        <a href="/event/{i}" style="text-decoration:none;color:inherit;">
        <div class="card">
            <h3>{e['title']}</h3>
            <p>📅 {e['date']}</p>
            <p>📍 {e['place']}</p>

            <div class="actions">
                <a href="/edit/{i}" onclick="event.stopPropagation()">編集</a>
                <a href="/delete/{i}" onclick="event.stopPropagation()">削除</a>
            </div>
        </div>
        </a>
        """

    return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>しおり</title>

<style>
* {{
    box-sizing:border-box;
}}

body {{
    margin:0;
    font-family:Yu Gothic;
    background:#fff8e7;
}}

.container {{
    max-width:900px;
    margin:auto;
    padding:30px;
}}

h1 {{
    text-align:center;
    color:#a8861d;
}}

.form {{
    background:white;
    padding:20px;
    border-radius:15px;
    margin-bottom:20px;
}}

input {{
    width:100%;
    padding:10px;
    margin:8px 0;
}}

button {{
    background:#c9a227;
    color:white;
    border:none;
    padding:10px;
    border-radius:10px;
}}

.card {{
    background:white;
    padding:15px;
    margin-bottom:12px;
    border-left:5px solid #c9a227;
    border-radius:12px;
}}

.actions {{
    display:flex;
    gap:10px;
    margin-top:10px;
}}

.actions a {{
    background:#eee;
    padding:5px 10px;
    border-radius:8px;
    text-decoration:none;
    color:#333;
}}

</style>
</head>

<body>

<div class="container">

<h1>📖 デートしおり</h1>

<a href="/logout">ログアウト</a>

<div class="form">
<form action="/add" method="post">
<input name="title" placeholder="イベント名">
<input type="date" name="date">
<input name="place" placeholder="場所">
<button>追加</button>
</form>
</div>

{cards}

</div>

</body>
</html>
"""


# =========================
# 追加
# =========================
@app.route("/add", methods=["POST"])
def add():
    if not is_login():
        return redirect("/login")

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
    if not is_login():
        return redirect("/login")

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
    if not is_login():
        return redirect("/login")

    events = load_events()
    e = events[i]

    return f"""
    <h2>編集</h2>
    <form action="/update/{i}" method="post">
        <input name="title" value="{e['title']}">
        <input name="date" value="{e['date']}">
        <input name="place" value="{e['place']}">
        <button>更新</button>
    </form>
    """


@app.route("/update/<int:i>", methods=["POST"])
def update(i):
    if not is_login():
        return redirect("/login")

    events = load_events()

    events[i] = {
        "title": request.form["title"],
        "date": request.form["date"],
        "place": request.form["place"]
    }

    save_events(events)
    return redirect("/")


# =========================
# 詳細
# =========================
@app.route("/event/<int:i>")
def detail(i):
    if not is_login():
        return redirect("/login")

    e = load_events()[i]

    return f"""
    <div style="font-family:Yu Gothic;padding:30px;background:#fff8e7;">
        <h1>{e['title']}</h1>
        <p>📅 {e['date']}</p>
        <p>📍 {e['place']}</p>
        <a href="/">戻る</a>
    </div>
    """


if __name__ == "__main__":
    app.run(debug=True)