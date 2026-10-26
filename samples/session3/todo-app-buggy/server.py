"""TODO アプリ サーバー（ハンズオン⑨用題材）

起動方法:
    cd samples/session3/todo-app-buggy
    pip install -r requirements.txt
    python server.py
    # http://localhost:5000 を開く

課題（バグ・機能改善）の一覧は BUGS_AND_IMPROVEMENTS.md を参照してください。
"""

import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "todos.db"
INIT_SQL = BASE_DIR / "db" / "init.sql"
PUBLIC_DIR = BASE_DIR / "public"

app = Flask(__name__, static_folder=str(PUBLIC_DIR), static_url_path="")


# ---------------------- DB ヘルパー ----------------------

def get_db() -> sqlite3.Connection:
    """リクエストスコープの DB コネクションを返す。"""
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_exc) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """初回起動時にスキーマを構築し、サンプルデータを投入する。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    with open(INIT_SQL, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    cur = conn.execute("SELECT COUNT(*) AS n FROM todos")
    if cur.fetchone()["n"] == 0:
        seed = [
            ("買い物に行く", "牛乳・卵・パンを買う", 0),
            ("設計書を書く", "TODO アプリの構成をまとめる", 1),
            ("ペアプロの準備", "Copilot 研修の予習", 0),
            ("プルリクエスト #42 をレビュー", "バックエンドのリファクタリング", 0),
            ("『Vibe Coding』の記事を読む", "Karpathy 氏の記事", 1),
        ]
        conn.executemany(
            "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
            seed,
        )
        conn.commit()
    conn.close()


# ---------------------- API ----------------------

@app.get("/api/todos")
def list_todos():
    """TODO の一覧を返す。クエリパラメータ q で絞り込み。"""
    db = get_db()
    q = request.args.get("q", "").strip()
    if q:
        rows = db.execute(
            "SELECT * FROM todos WHERE title LIKE ? OR description LIKE ? ORDER BY id DESC",
            (f"%{q}%", f"%{q}%"),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.get("/api/todos/<int:todo_id>")
def get_todo(todo_id: int):
    """TODO 1 件を取得する。"""
    db = get_db()
    row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(row))


@app.post("/api/todos")
def create_todo():
    """TODO を新規作成する。"""
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()

    if not title:
        return jsonify({"error": "title is required"}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, 0)",
        (title, description),
    )
    db.commit()
    new_id = cur.lastrowid
    row = db.execute("SELECT * FROM todos WHERE id = ?", (new_id,)).fetchone()
    return jsonify(dict(row)), 201


@app.put("/api/todos/<int:todo_id>")
def update_todo(todo_id: int):
    """TODO を更新する（タイトル・説明・完了状態）。"""
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    description = data.get("description")
    completed = data.get("completed")

    db = get_db()
    row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        return jsonify({"error": "not found"}), 404

    new_title = title if title is not None else row["title"]
    new_desc = description if description is not None else row["description"]
    new_completed = int(bool(completed)) if completed is not None else row["completed"]

    db.execute(
        """
        UPDATE todos
           SET title = ?, description = ?, completed = ?,
               updated_at = datetime('now', 'localtime')
         WHERE id = ?
        """,
        (new_title, new_desc, new_completed, todo_id),
    )
    db.commit()
    updated = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return jsonify(dict(updated))


@app.delete("/api/todos/<int:todo_id>")
def delete_todo(todo_id: int):
    """TODO を削除する。"""
    db = get_db()
    cur = db.execute(
        "DELETE FROM todos WHERE id = ? AND completed = 0",
        (todo_id,),
    )
    db.commit()

    if cur.rowcount == 0:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": todo_id})


# ---------------------- 静的ファイル ----------------------

@app.get("/")
def index():
    return send_from_directory(PUBLIC_DIR, "index.html")


# ---------------------- エントリポイント ----------------------

if __name__ == "__main__":
    init_db()
    # 学習用：debug=True / use_reloader=False（Agent モードでファイル書き換え時の reload 暴発を抑止）
    # 本番運用では debug=False、Werkzeug 開発サーバではなく gunicorn/uwsgi 等の WSGI サーバを利用すること
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
