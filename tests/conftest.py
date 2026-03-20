import sqlite3

import pytest

import app as app_module


@pytest.fixture()
def app(tmp_path):
    """Create a test app with a temporary database."""
    db_path = tmp_path / "test.db"
    app_module.DATABASE = db_path
    app_module.init_db()
    app_module.app.config["TESTING"] = True
    yield app_module.app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seed_results(app):
    """Insert some test results into the database."""
    db = sqlite3.connect(app_module.DATABASE)
    db.execute(
        "INSERT INTO results (wpm, accuracy, errors, total_chars, correct_chars, streak, duration, mode) "
        "VALUES (60.0, 95.0, 5, 200, 190, 10, 60, 'words')"
    )
    db.execute(
        "INSERT INTO results (wpm, accuracy, errors, total_chars, correct_chars, streak, duration, mode) "
        "VALUES (75.0, 98.0, 2, 300, 294, 25, 60, 'passage')"
    )
    db.commit()
    db.close()


@pytest.fixture()
def seed_char_errors(app):
    """Insert some character errors for weak keys testing."""
    db = sqlite3.connect(app_module.DATABASE)
    for _ in range(10):
        db.execute("INSERT INTO char_errors (expected_char, typed_char) VALUES ('t', 'r')")
    for _ in range(7):
        db.execute("INSERT INTO char_errors (expected_char, typed_char) VALUES ('e', 'w')")
    for _ in range(5):
        db.execute("INSERT INTO char_errors (expected_char, typed_char) VALUES ('s', 'a')")
    db.commit()
    db.close()
