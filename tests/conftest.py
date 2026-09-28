import os
import sys

import pytest
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database.db as db  # noqa: E402
import app as app_module  # noqa: E402


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Point the app's get_db() at an isolated, temporary SQLite file."""
    path = str(tmp_path / "test_spendly.db")
    monkeypatch.setattr(db, "DB_PATH", path)
    # app.py imported get_db by reference from database.db; patch the same
    # module-level constant it closes over so both app and db use the temp file.
    monkeypatch.setattr(app_module, "get_db", db.get_db)
    db.init_db()
    return path


@pytest.fixture
def app(db_path):
    app_module.app.config.update(TESTING=True)
    return app_module.app


@pytest.fixture
def client(app):
    return app.app_context(), app.test_client()


@pytest.fixture
def test_client(app):
    return app.test_client()


def create_user(name="Alice", email="alice@example.com", password="password123"):
    conn = db.get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def create_expense(user_id, amount, category, date, description=""):
    conn = db.get_db()
    try:
        conn.execute(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, amount, category, date, description),
        )
        conn.commit()
    finally:
        conn.close()


def login(client, user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
