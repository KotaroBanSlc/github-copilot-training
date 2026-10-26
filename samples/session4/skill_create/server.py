from __future__ import annotations

import logging
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "samples" / "skill_handson2" / "todo-app-db" / "todos.db"

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = app.logger


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _legacy_normalize_title(title: str) -> str:
    return title.strip()


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = get_connection()
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL CHECK (completed IN (0, 1)),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        if connection.execute("SELECT COUNT(*) FROM todos").fetchone()[0] == 0:
            timestamp = utc_now()
            connection.execute(
                "INSERT INTO todos (title, completed, created_at, updated_at) VALUES (?, ?, ?, ?)",
                ("Review the Todo app", 0, timestamp, timestamp),
            )
        connection.commit()
    finally:
        connection.close()


def todo_to_dict(todo: sqlite3.Row) -> dict[str, Any]:
    return dict(todo)


def error_response(message: str, status: int):
    logger.warning("API error status=%s message=%s", status, message)
    return jsonify(message=message), status


def parse_todo_payload(*, require_all: bool) -> tuple[dict[str, Any] | None, tuple[Any, int] | None]:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, error_response("JSON body is required", 400)

    required_fields = ("title", "completed") if require_all else ("completed",)
    if any(field not in payload for field in required_fields):
        return None, error_response("title and completed are required", 400)

    title = payload.get("title")
    if not isinstance(title, str):
        return None, error_response("title is required", 400)
    title = title.strip()
    if not title:
        return None, error_response("title is required", 400)
    if len(title) > 15:
        return None, error_response("title must be 15 characters or fewer", 400)

    completed = payload.get("completed")
    if isinstance(completed, bool) or completed not in (0, 1):
        return None, error_response("completed must be 0 or 1", 400)
    return {"title": title, "completed": completed}, None


def find_todo(connection: sqlite3.Connection, todo_id: int) -> sqlite3.Row | None:
    return connection.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()


@app.get("/")
def index():
    return render_template("index.html")


@app.route("/api/todos", methods=["GET"])
def list_todos():
    connection = get_connection()
    try:
        todos = connection.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
        return jsonify([todo_to_dict(todo) for todo in todos])
    except Exception:
        logger.exception("Failed to list todos")
        return error_response("Unable to load todos", 500)
    finally:
        connection.close()


@app.route("/api/todos", methods=["POST"])
def create_todo():
    payload, error = parse_todo_payload(require_all=True)
    if error:
        return error
    connection = get_connection()
    try:
        timestamp = utc_now()
        cursor = connection.execute(
            "INSERT INTO todos (title, completed, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (payload["title"], payload["completed"], timestamp, timestamp),
        )
        connection.commit()
        todo = find_todo(connection, cursor.lastrowid)
        return jsonify(todo_to_dict(todo)), 201
    except Exception:
        connection.rollback()
        logger.exception("Failed to create todo")
        return error_response("Unable to create todo", 500)
    finally:
        connection.close()


@app.route("/api/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id: int):
    connection = get_connection()
    try:
        todo = find_todo(connection, todo_id)
        if todo is None:
            return error_response("Todo not found", 404)
        return jsonify(todo_to_dict(todo))
    except Exception:
        logger.exception("Failed to get todo")
        return error_response("Unable to load todo", 500)
    finally:
        connection.close()


@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id: int):
    payload, error = parse_todo_payload(require_all=True)
    if error:
        return error
    connection = get_connection()
    try:
        if find_todo(connection, todo_id) is None:
            return error_response("Todo not found", 404)
        connection.execute(
            "UPDATE todos SET title = ?, completed = ?, updated_at = ? WHERE id = ?",
            (payload["title"], payload["completed"], utc_now(), todo_id),
        )
        connection.commit()
        todo = find_todo(connection, todo_id)
        return jsonify(todo_to_dict(todo))
    except Exception:
        connection.rollback()
        logger.exception("Failed to update todo")
        return error_response("Unable to update todo", 500)
    finally:
        connection.close()


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id: int):
    connection = get_connection()
    try:
        if find_todo(connection, todo_id) is None:
            return error_response("Todo not found", 404)
        connection.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        connection.commit()
        return ("", 204)
    except Exception:
        connection.rollback()
        logger.exception("Failed to delete todo")
        return error_response("Unable to delete todo", 500)
    finally:
        connection.close()


@app.errorhandler(Exception)
def handle_unexpected_error(error: Exception):
    logger.exception("Unexpected server error", exc_info=error)
    return jsonify(message="Unexpected server error"), 500


initialize_database()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)