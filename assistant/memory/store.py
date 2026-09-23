"""Local SQLite memory — no cloud account required."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from assistant.config import MEMORY_DB_PATH


class MemoryStore:
    def __init__(self, db_path: Path = MEMORY_DB_PATH) -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    path TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    due_date TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                );
                """
            )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def set_preference(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO preferences (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                """,
                (key.strip().lower(), value, self._now()),
            )

    def get_preference(self, key: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM preferences WHERE key = ?",
                (key.strip().lower(),),
            ).fetchone()
        return row["value"] if row else None

    def list_preferences(self) -> dict[str, str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT key, value FROM preferences ORDER BY key").fetchall()
        return {row["key"]: row["value"] for row in rows}

    def save_project(self, name: str, path: str, description: str = "") -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO projects (name, path, description, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    path=excluded.path,
                    description=excluded.description
                """,
                (name.strip(), path.strip(), description.strip(), self._now()),
            )

    def get_project(self, name: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT name, path, description FROM projects WHERE lower(name) = lower(?)",
                (name.strip(),),
            ).fetchone()
        if not row:
            return None
        return {"name": row["name"], "path": row["path"], "description": row["description"]}

    def list_projects(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT name, path, description FROM projects ORDER BY name"
            ).fetchall()
        return [
            {"name": r["name"], "path": r["path"], "description": r["description"]}
            for r in rows
        ]

    def add_message(self, role: str, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages (role, content, created_at) VALUES (?, ?, ?)",
                (role, content, self._now()),
            )

    def recent_messages(self, limit: int = 20) -> list[dict[str, str]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT role, content, created_at FROM messages ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {"role": r["role"], "content": r["content"], "created_at": r["created_at"]}
            for r in reversed(rows)
        ]

    # --- Todo Management ---
    def add_todo(self, title: str, due_date: str = "") -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO todos (title, status, due_date, created_at) VALUES (?, 'pending', ?, ?)",
                (title.strip(), due_date.strip(), self._now()),
            )
            return cursor.lastrowid

    def list_todos(self, status: str = "all") -> list[dict[str, Any]]:
        with self._connect() as conn:
            if status in {"pending", "completed"}:
                rows = conn.execute(
                    "SELECT id, title, status, due_date, created_at FROM todos WHERE status = ? ORDER BY id DESC",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, title, status, due_date, created_at FROM todos ORDER BY status DESC, id DESC"
                ).fetchall()
        return [dict(r) for r in rows]

    def complete_todo(self, todo_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("UPDATE todos SET status = 'completed' WHERE id = ?", (todo_id,))
            return cur.rowcount > 0

    def delete_todo(self, todo_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
            return cur.rowcount > 0

    # --- Calendar & Events ---
    def add_event(self, title: str, date: str, time: str = "", notes: str = "") -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO events (title, date, time, notes, created_at) VALUES (?, ?, ?, ?, ?)",
                (title.strip(), date.strip(), time.strip(), notes.strip(), self._now()),
            )
            return cursor.lastrowid

    def list_events(self, limit: int = 15) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, title, date, time, notes, created_at FROM events ORDER BY date ASC, time ASC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def delete_event(self, event_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
            return cur.rowcount > 0

    def context_summary(self) -> str:
        """Build a short memory context string for the system prompt."""
        parts: list[str] = []
        prefs = self.list_preferences()
        if prefs:
            pref_lines = [f"  {k}: {v}" for k, v in prefs.items()]
            parts.append("User preferences:\n" + "\n".join(pref_lines))

        projects = self.list_projects()
        if projects:
            proj_lines = [
                f"  {p['name']} -> {p['path']}"
                + (f" ({p['description']})" if p["description"] else "")
                for p in projects
            ]
            parts.append("Saved projects:\n" + "\n".join(proj_lines))

        return "\n\n".join(parts)
