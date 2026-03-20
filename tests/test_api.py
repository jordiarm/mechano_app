import json
import sqlite3

from werkzeug.security import generate_password_hash

import app as app_module


class TestAuth:
    def test_register_success(self, client):
        resp = client.post("/register", data={"username": "newuser", "password": "pass1234"})
        assert resp.status_code == 302
        assert resp.headers["Location"] == "/"

    def test_register_short_username(self, client):
        resp = client.post("/register", data={"username": "a", "password": "pass1234"})
        assert resp.status_code == 200
        assert b"at least 2 characters" in resp.data

    def test_register_short_password(self, client):
        resp = client.post("/register", data={"username": "newuser", "password": "ab"})
        assert resp.status_code == 200
        assert b"at least 4 characters" in resp.data

    def test_register_duplicate_username(self, client, user):
        resp = client.post("/register", data={"username": "testuser", "password": "pass1234"})
        assert resp.status_code == 200
        assert b"already taken" in resp.data

    def test_login_success(self, client, user):
        resp = client.post("/login", data={"username": "testuser", "password": "testpass"})
        assert resp.status_code == 302
        assert resp.headers["Location"] == "/"

    def test_login_wrong_password(self, client, user):
        resp = client.post("/login", data={"username": "testuser", "password": "wrong"})
        assert resp.status_code == 200
        assert b"invalid username or password" in resp.data

    def test_login_nonexistent_user(self, client):
        resp = client.post("/login", data={"username": "ghost", "password": "pass"})
        assert resp.status_code == 200
        assert b"invalid username or password" in resp.data

    def test_logout(self, auth_client):
        resp = auth_client.post("/logout")
        assert resp.status_code == 302
        assert resp.headers["Location"] == "/login"

    def test_unauthenticated_redirect(self, client):
        resp = client.get("/")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_unauthenticated_api_401(self, client):
        resp = client.get("/api/results", headers={"Content-Type": "application/json"})
        assert resp.status_code == 401

    def test_get_me(self, auth_client):
        resp = auth_client.get("/api/me")
        data = resp.get_json()
        assert data["username"] == "testuser"
        assert "user_id" in data


class TestIndex:
    def test_index_returns_html(self, auth_client):
        resp = auth_client.get("/")
        assert resp.status_code == 200
        assert b"mechano_app" in resp.data


class TestWords:
    def test_get_words_default(self, auth_client):
        resp = auth_client.get("/api/words")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "words" in data
        words = data["words"].split()
        assert len(words) == 200

    def test_get_words_custom_count(self, auth_client):
        resp = auth_client.get("/api/words?count=10")
        data = resp.get_json()
        words = data["words"].split()
        assert len(words) == 10


class TestPassages:
    def test_get_all_passages(self, auth_client):
        resp = auth_client.get("/api/passages")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "passages" in data
        assert len(data["passages"]) > 0
        assert "title" in data["passages"][0]
        assert "text" in data["passages"][0]

    def test_get_passage_by_index(self, auth_client):
        resp = auth_client.get("/api/passage?index=0")
        data = resp.get_json()
        assert "title" in data
        assert data["title"] == "The Zen of Python"

    def test_get_passage_invalid_index(self, auth_client):
        resp = auth_client.get("/api/passage?index=9999")
        data = resp.get_json()
        # Falls back to random passage
        assert "title" in data
        assert "text" in data

    def test_get_random_passage(self, auth_client):
        resp = auth_client.get("/api/passage")
        data = resp.get_json()
        assert "title" in data


class TestCodeSnippets:
    def test_get_all_code_snippets(self, auth_client):
        resp = auth_client.get("/api/code-snippets")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "snippets" in data
        assert len(data["snippets"]) > 0
        snippet = data["snippets"][0]
        assert "title" in snippet
        assert "text" in snippet
        assert "language" in snippet

    def test_get_code_snippet_by_index(self, auth_client):
        resp = auth_client.get("/api/code-snippet?index=0")
        data = resp.get_json()
        assert "title" in data
        assert "text" in data
        assert data["language"] == "python"

    def test_get_code_snippet_invalid_index(self, auth_client):
        resp = auth_client.get("/api/code-snippet?index=9999")
        data = resp.get_json()
        # Falls back to random snippet
        assert "title" in data
        assert "text" in data

    def test_get_random_code_snippet(self, auth_client):
        resp = auth_client.get("/api/code-snippet")
        data = resp.get_json()
        assert "title" in data
        assert "text" in data


class TestResults:
    def test_save_result(self, auth_client):
        resp = auth_client.post(
            "/api/results",
            data=json.dumps(
                {
                    "wpm": 65.0,
                    "accuracy": 96.5,
                    "errors": 3,
                    "total_chars": 250,
                    "correct_chars": 241,
                    "streak": 15,
                    "duration": 60,
                    "mode": "words",
                }
            ),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_get_results_empty(self, auth_client):
        resp = auth_client.get("/api/results")
        data = resp.get_json()
        assert data["results"] == []

    def test_get_results_with_data(self, auth_client, seed_results):
        resp = auth_client.get("/api/results")
        data = resp.get_json()
        assert len(data["results"]) == 2

    def test_get_results_limit(self, auth_client, seed_results):
        resp = auth_client.get("/api/results?limit=1")
        data = resp.get_json()
        assert len(data["results"]) == 1

    def test_get_results_filter_by_duration(self, auth_client, seed_results):
        resp = auth_client.get("/api/results?duration=60")
        data = resp.get_json()
        assert len(data["results"]) == 2
        for r in data["results"]:
            assert r["duration"] == 60

    def test_get_results_filter_by_duration_no_match(self, auth_client, seed_results):
        resp = auth_client.get("/api/results?duration=15")
        data = resp.get_json()
        assert len(data["results"]) == 0

    def test_get_results_filter_by_mode(self, auth_client, seed_results):
        resp = auth_client.get("/api/results?mode=words")
        data = resp.get_json()
        assert len(data["results"]) == 1
        assert data["results"][0]["mode"] == "words"

    def test_get_results_filter_by_mode_passage(self, auth_client, seed_results):
        resp = auth_client.get("/api/results?mode=passage")
        data = resp.get_json()
        assert len(data["results"]) == 1
        assert data["results"][0]["mode"] == "passage"

    def test_get_results_filter_by_mode_no_match(self, auth_client, seed_results):
        resp = auth_client.get("/api/results?mode=nonexistent")
        data = resp.get_json()
        assert len(data["results"]) == 0

    def test_get_results_filter_by_mode_and_duration(self, auth_client, seed_results):
        resp = auth_client.get("/api/results?mode=words&duration=60")
        data = resp.get_json()
        assert len(data["results"]) == 1
        assert data["results"][0]["mode"] == "words"
        assert data["results"][0]["duration"] == 60


class TestStats:
    def test_stats_empty(self, auth_client):
        resp = auth_client.get("/api/stats")
        data = resp.get_json()
        assert data["total_tests"] == 0
        assert data["avg_wpm"] == 0
        assert data["history"] == []

    def test_stats_with_data(self, auth_client, seed_results):
        resp = auth_client.get("/api/stats")
        data = resp.get_json()
        assert data["total_tests"] == 2

    def test_stats_filtered_by_duration(self, auth_client, seed_results):
        resp = auth_client.get("/api/stats?duration=60")
        data = resp.get_json()
        assert data["total_tests"] == 2
        assert data["best_wpm"] == 75.0

    def test_stats_filtered_by_duration_no_match(self, auth_client, seed_results):
        resp = auth_client.get("/api/stats?duration=15")
        data = resp.get_json()
        assert data["total_tests"] == 0
        assert data["avg_wpm"] == 0
        assert data["best_wpm"] == 0
        assert data["history"] == []

    def test_stats_filtered_by_mode_words(self, auth_client, seed_results):
        resp = auth_client.get("/api/stats?mode=words")
        data = resp.get_json()
        assert data["total_tests"] == 1
        assert data["best_wpm"] == 60.0

    def test_stats_filtered_by_mode_passage(self, auth_client, seed_results):
        resp = auth_client.get("/api/stats?mode=passage")
        data = resp.get_json()
        assert data["total_tests"] == 1
        assert data["best_wpm"] == 75.0

    def test_stats_filtered_by_mode_no_match(self, auth_client, seed_results):
        resp = auth_client.get("/api/stats?mode=nonexistent")
        data = resp.get_json()
        assert data["total_tests"] == 0
        assert data["best_wpm"] == 0
        assert data["history"] == []

    def test_stats_filtered_by_mode_and_duration(self, auth_client, seed_results):
        resp = auth_client.get("/api/stats?mode=words&duration=60")
        data = resp.get_json()
        assert data["total_tests"] == 1
        assert data["best_wpm"] == 60.0


class TestLessons:
    def test_get_lessons(self, auth_client):
        resp = auth_client.get("/api/lessons")
        data = resp.get_json()
        levels = data["levels"]
        assert len(levels) == 8
        # First lesson is always available
        assert levels[0]["lessons"][0]["status"] == "available"
        # Second lesson is locked (first not completed)
        assert levels[0]["lessons"][1]["status"] == "locked"

    def test_get_lesson_by_id(self, auth_client):
        resp = auth_client.get("/api/lesson/1.1")
        data = resp.get_json()
        assert data["id"] == "1.1"
        assert data["title"] == "Left Hand Home Keys"
        assert "text" in data

    def test_get_lesson_not_found(self, auth_client):
        resp = auth_client.get("/api/lesson/99.99")
        assert resp.status_code == 404

    def test_save_lesson_result_pass(self, auth_client):
        resp = auth_client.post(
            "/api/lesson/1.1/result",
            data=json.dumps(
                {
                    "wpm": 40.0,
                    "accuracy": 95.0,
                    "errors": 2,
                    "total_chars": 80,
                    "correct_chars": 76,
                }
            ),
            content_type="application/json",
        )
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["passed"] is True

    def test_save_lesson_result_fail(self, auth_client):
        resp = auth_client.post(
            "/api/lesson/1.1/result",
            data=json.dumps(
                {
                    "wpm": 20.0,
                    "accuracy": 70.0,
                    "errors": 20,
                    "total_chars": 80,
                    "correct_chars": 56,
                }
            ),
            content_type="application/json",
        )
        data = resp.get_json()
        assert data["passed"] is False

    def test_save_lesson_result_not_found(self, auth_client):
        resp = auth_client.post(
            "/api/lesson/99.99/result",
            data=json.dumps({"wpm": 40.0, "accuracy": 95.0, "errors": 0, "total_chars": 10, "correct_chars": 10}),
            content_type="application/json",
        )
        assert resp.status_code == 404

    def test_lesson_unlock_progression(self, auth_client):
        # Complete lesson 1.1
        auth_client.post(
            "/api/lesson/1.1/result",
            data=json.dumps({"wpm": 40.0, "accuracy": 95.0, "errors": 1, "total_chars": 80, "correct_chars": 76}),
            content_type="application/json",
        )
        # Lesson 1.2 should now be available
        resp = auth_client.get("/api/lessons")
        levels = resp.get_json()["levels"]
        assert levels[0]["lessons"][0]["status"] == "completed"
        assert levels[0]["lessons"][1]["status"] == "available"


class TestCharErrors:
    def test_save_char_errors(self, auth_client):
        # First create a result to link errors to
        res = auth_client.post(
            "/api/results",
            data=json.dumps(
                {
                    "wpm": 60.0,
                    "accuracy": 95.0,
                    "errors": 2,
                    "total_chars": 100,
                    "correct_chars": 98,
                    "streak": 10,
                    "duration": 60,
                    "mode": "words",
                }
            ),
            content_type="application/json",
        )
        result_id = res.get_json()["id"]
        resp = auth_client.post(
            "/api/char-errors",
            data=json.dumps(
                {
                    "result_id": result_id,
                    "errors": [
                        {"expected": "t", "typed": "r"},
                        {"expected": "e", "typed": "w"},
                    ],
                }
            ),
            content_type="application/json",
        )
        assert resp.get_json()["status"] == "ok"

    def test_save_empty_errors(self, auth_client):
        resp = auth_client.post(
            "/api/char-errors",
            data=json.dumps({"errors": []}),
            content_type="application/json",
        )
        assert resp.get_json()["status"] == "ok"


class TestWeakKeys:
    def test_weak_keys_empty(self, auth_client):
        resp = auth_client.get("/api/weak-keys")
        data = resp.get_json()
        assert data["weak_keys"] == []

    def test_weak_keys_with_data(self, auth_client, seed_char_errors):
        resp = auth_client.get("/api/weak-keys")
        data = resp.get_json()
        assert len(data["weak_keys"]) == 3
        # Most missed key first
        assert data["weak_keys"][0]["char"] == "t"
        assert data["weak_keys"][0]["count"] == 10

    def test_weak_keys_practice_empty(self, auth_client):
        resp = auth_client.get("/api/weak-keys/practice")
        data = resp.get_json()
        assert data["has_data"] is False
        assert data["text"] == ""

    def test_weak_keys_practice_with_data(self, auth_client, seed_char_errors):
        resp = auth_client.get("/api/weak-keys/practice")
        data = resp.get_json()
        assert data["has_data"] is True
        assert len(data["text"]) > 0
        assert len(data["weak_keys"]) == 3


class TestUserScoping:
    """Verify that data is scoped per-user."""

    def test_results_scoped_to_user(self, app, client, user):
        """Each user should only see their own results."""
        # Create a second user
        db = sqlite3.connect(app_module.DATABASE)
        cursor = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("user2", generate_password_hash("pass2")),
        )
        user2_id = cursor.lastrowid
        # Insert results for both users
        db.execute(
            "INSERT INTO results (user_id, wpm, accuracy, errors, total_chars, correct_chars, streak, duration, mode) "
            "VALUES (?, 80.0, 99.0, 1, 100, 99, 20, 60, 'words')",
            (user,),
        )
        db.execute(
            "INSERT INTO results (user_id, wpm, accuracy, errors, total_chars, correct_chars, streak, duration, mode) "
            "VALUES (?, 50.0, 90.0, 5, 100, 95, 10, 60, 'words')",
            (user2_id,),
        )
        db.commit()
        db.close()

        # Login as user1
        client.post("/login", data={"username": "testuser", "password": "testpass"})
        resp = client.get("/api/results")
        data = resp.get_json()
        assert len(data["results"]) == 1
        assert data["results"][0]["wpm"] == 80.0

        # Logout and login as user2
        client.post("/logout")
        client.post("/login", data={"username": "user2", "password": "pass2"})
        resp = client.get("/api/results")
        data = resp.get_json()
        assert len(data["results"]) == 1
        assert data["results"][0]["wpm"] == 50.0
