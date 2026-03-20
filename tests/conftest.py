import sqlite3

import pytest
from werkzeug.security import generate_password_hash

import app as app_module


@pytest.fixture()
def app(tmp_path):
    """Create a test app with a temporary database."""
    db_path = tmp_path / "test.db"
    app_module.DATABASE = db_path
    app_module.init_db()
    app_module.app.config["TESTING"] = True
    app_module.app.config["SECRET_KEY"] = "test-secret"
    yield app_module.app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user(app):
    """Create a test user and return their id."""
    db = sqlite3.connect(app_module.DATABASE)
    cursor = db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        ("testuser", generate_password_hash("testpass")),
    )
    user_id = cursor.lastrowid
    db.commit()
    db.close()
    return user_id


@pytest.fixture()
def auth_client(client, user):
    """A test client with an active login session."""
    client.post("/login", data={"username": "testuser", "password": "testpass"})
    return client


@pytest.fixture()
def seed_results(app, user):
    """Insert some test results into the database."""
    db = sqlite3.connect(app_module.DATABASE)
    db.execute(
        "INSERT INTO results (user_id, wpm, accuracy, errors, total_chars, correct_chars, streak, duration, mode) "
        "VALUES (?, 60.0, 95.0, 5, 200, 190, 10, 60, 'words')",
        (user,),
    )
    db.execute(
        "INSERT INTO results (user_id, wpm, accuracy, errors, total_chars, correct_chars, streak, duration, mode) "
        "VALUES (?, 75.0, 98.0, 2, 300, 294, 25, 60, 'passage')",
        (user,),
    )
    db.commit()
    db.close()


@pytest.fixture()
def seed_char_errors(app, user):
    """Insert some character errors linked to results for weak keys testing."""
    db = sqlite3.connect(app_module.DATABASE)
    cursor = db.execute(
        "INSERT INTO results (user_id, wpm, accuracy, errors, total_chars, correct_chars, streak, duration, mode) "
        "VALUES (?, 50.0, 90.0, 22, 200, 178, 5, 60, 'words')",
        (user,),
    )
    result_id = cursor.lastrowid
    for _ in range(10):
        db.execute(
            "INSERT INTO char_errors (result_id, user_id, expected_char, typed_char) VALUES (?, ?, 't', 'r')",
            (result_id, user),
        )
    for _ in range(7):
        db.execute(
            "INSERT INTO char_errors (result_id, user_id, expected_char, typed_char) VALUES (?, ?, 'e', 'w')",
            (result_id, user),
        )
    for _ in range(5):
        db.execute(
            "INSERT INTO char_errors (result_id, user_id, expected_char, typed_char) VALUES (?, ?, 's', 'a')",
            (result_id, user),
        )
    db.commit()
    db.close()
