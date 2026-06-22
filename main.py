from flask import Flask, request, redirect, render_template_string
import json
import os

app = Flask(__name__)

DATA_FILE = "events.json"


# =========================
# データ読み書き
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
# テンプレート（共通デザイン）
# =========================
BASE_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>デート管理</title>

<style>
body {
    margin:0;
    font-family:"Yu Gothic", sans-serif;
    background:#fff7d6;
}

.container {
    max-width:900px;
    margin:auto;
    padding:20px;
}

h1 {
    text-align:center;
    color:#444;
    margin-bottom:20px;
}

.card {
    background:white;
    padding:18px;
    border-radius:16px;
    margin-bottom:12px;
    box-shadow:0 6px 18px rgba(0,0,0,0.08);
}

input {
    width:100%;
    padding:10px;
    margin:6px 0 12px;
    border-radius:10px;
    border:1px solid #ddd;
}

button {
    background:#444;
    color:white;
    border:none;
    padding:10px 16px;
    border-radius:10px;
    cursor:pointer;
}

a {
    text-decoration:none;
    color:#444;
}

.actions {
    margin-top:10px;
    display:flex;
    gap:10px;
    font-size:14px;
}

.small {
    font-size:12px;
    opacity:0.7;
}
</style>
</head>

<body>
<div class="container">
<h1>デート管理アプリ</h1>

<form action="/add" method="post" class="card">
    <h3>イベント追加</h3>
    <input name="title" placeholder="タイトル" required>
    <input type="date" name="date" required>
    <input name="place" placeholder="場所" required>
    <button>追加</button>
</form>

{{content}}

</div>
</body>
</html>
"""


# =========================
# 一覧
# =========================
@app.route("/")
def home():
    events = load_events()

    cards = ""
    for i, e in enumerate(events):
        cards += f"""
        <div class="card">
            <h3>{e['title']}</h3>
            <p>📅 {e['date']}</p>
            <p>📍 {e['place']}</p>

            <div class="actions">
                <a href="/event/{i}">詳細</a>
                <a href="/edit/{i}">編集</a>
                <a href="/delete/{i}">削除</a>
            </div>
        </div>
        """

    return render_template_string(BASE_HTML.replace("{{content}}", cards))


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
# 詳細
# =========================
@app.route("/event/<int:i>")
def event(i):
    events = load_events()
    e = events[i]

    return f"""
    <div style="padding:20px;font-family:Yu Gothic;background:#fff7d6;min-height:100vh;">
        <div style="max-width:600px;margin:auto;background:white;padding:20px;border-radius:16px;">
            <h2>{e['title']}</h2>
            <p>📅 {e['date']}</p>
            <p>📍 {e['place']}</p>
            <a href="/">戻る</a>
        </div>
    </div>
    """


# =========================
# 編集
# =========================
@app.route("/edit/<int:i>")
def edit(i):
    events = load_events()
    e = events[i]

    return f"""
    <div style="padding:20px;font-family:Yu Gothic;background:#fff7d6;min-height:100vh;">
        <div style="max-width:600px;margin:auto;background:white;padding:20px;border-radius:16px;">
            <h2>編集</h2>

            <form action="/update/{i}" method="post">
                <input name="title" value="{e['title']}" required>
                <input type="date" name="date" value="{e['date']}" required>
                <input name="place" value="{e['place']}" required>
                <button>更新</button>
            </form>

            <a href="/">戻る</a>
        </div>
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
# Render対応起動（重要）
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)