"""Applications and reminders stored in SQLite.

Personal data is never stored or logged here; applications hold only the
scheme id, status, next action, optional reminder date and free notes.
"""
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

STATUSES = (
    "not_started",
    "documents_ready",
    "applied",
    "under_review",
    "approved",
    "rejected",
)

_DEFAULT_DB = Path(__file__).resolve().parent / "app.db"

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS applications (
    id TEXT PRIMARY KEY,
    scheme_id TEXT,
    status TEXT,
    next_action TEXT,
    reminder_date TEXT,
    notes TEXT,
    created_at TEXT,
    updated_at TEXT
)
"""


def _db_path():
    # Read on every call so tests can point APP_DB somewhere else.
    return os.environ.get("APP_DB") or str(_DEFAULT_DB)


def _now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _connect():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        conn.execute(_CREATE_SQL)
        yield conn
        conn.commit()
    finally:
        conn.close()


def _row_to_dict(row):
    return dict(row) if row is not None else None


def list_applications():
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM applications ORDER BY created_at, rowid"
        ).fetchall()
        return [_row_to_dict(row) for row in rows]


def get_application(app_id):
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM applications WHERE id = ?", (app_id,)
        ).fetchone()
        return _row_to_dict(row)


def create_application(scheme_id, next_action=""):
    app_id = str(uuid.uuid4())
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO applications "
            "(id, scheme_id, status, next_action, reminder_date, notes, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (app_id, scheme_id, "not_started", next_action, None, "", now, now),
        )
        row = conn.execute(
            "SELECT * FROM applications WHERE id = ?", (app_id,)
        ).fetchone()
        return _row_to_dict(row)


def update_application(app_id, status=None, notes=None, reminder_date=None):
    """Update the given fields. Fields passed as None are left unchanged.

    Returns the updated application, or None if it does not exist.
    Raises ValueError for an unknown status.
    """
    if status is not None and status not in STATUSES:
        raise ValueError(f"Invalid status: {status}")

    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM applications WHERE id = ?", (app_id,)
        ).fetchone()
        if row is None:
            return None

        # Column names below are fixed literals, never user input.
        changes = {"updated_at": _now()}
        if status is not None:
            changes["status"] = status
        if notes is not None:
            changes["notes"] = notes
        if reminder_date is not None:
            changes["reminder_date"] = reminder_date

        assignments = ", ".join(f"{column} = ?" for column in changes)
        conn.execute(
            f"UPDATE applications SET {assignments} WHERE id = ?",
            (*changes.values(), app_id),
        )
        row = conn.execute(
            "SELECT * FROM applications WHERE id = ?", (app_id,)
        ).fetchone()
        return _row_to_dict(row)


def list_reminders():
    with _connect() as conn:
        rows = conn.execute(
            "SELECT scheme_id, reminder_date FROM applications "
            "WHERE reminder_date IS NOT NULL ORDER BY reminder_date, created_at, rowid"
        ).fetchall()
        return [
            {
                "scheme_id": row["scheme_id"],
                "date": row["reminder_date"],
                "message": f"Check {row['scheme_id']} by {row['reminder_date']}",
            }
            for row in rows
        ]
