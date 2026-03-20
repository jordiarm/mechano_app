import json


class TestIndex:
    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"mechano_app" in resp.data


class TestWords:
    def test_get_words_default(self, client):
        resp = client.get("/api/words")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "words" in data
        words = data["words"].split()
        assert len(words) == 200

    def test_get_words_custom_count(self, client):
        resp = client.get("/api/words?count=10")
        data = resp.get_json()
        words = data["words"].split()
        assert len(words) == 10


class TestPassages:
    def test_get_all_passages(self, client):
        resp = client.get("/api/passages")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "passages" in data
        assert len(data["passages"]) > 0
        assert "title" in data["passages"][0]
        assert "text" in data["passages"][0]

    def test_get_passage_by_index(self, client):
        resp = client.get("/api/passage?index=0")
        data = resp.get_json()
        assert "title" in data
        assert data["title"] == "The Zen of Python"

    def test_get_passage_invalid_index(self, client):
        resp = client.get("/api/passage?index=9999")
        data = resp.get_json()
        # Falls back to random passage
        assert "title" in data
        assert "text" in data

    def test_get_random_passage(self, client):
        resp = client.get("/api/passage")
        data = resp.get_json()
        assert "title" in data


class TestCodeSnippets:
    def test_get_all_code_snippets(self, client):
        resp = client.get("/api/code-snippets")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "snippets" in data
        assert len(data["snippets"]) > 0
        snippet = data["snippets"][0]
        assert "title" in snippet
        assert "text" in snippet
        assert "language" in snippet

    def test_get_code_snippet_by_index(self, client):
        resp = client.get("/api/code-snippet?index=0")
        data = resp.get_json()
        assert "title" in data
        assert "text" in data
        assert data["language"] == "python"

    def test_get_code_snippet_invalid_index(self, client):
        resp = client.get("/api/code-snippet?index=9999")
        data = resp.get_json()
        # Falls back to random snippet
        assert "title" in data
        assert "text" in data

    def test_get_random_code_snippet(self, client):
        resp = client.get("/api/code-snippet")
        data = resp.get_json()
        assert "title" in data
        assert "text" in data


class TestResults:
    def test_save_result(self, client):
        resp = client.post(
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

    def test_get_results_empty(self, client):
        resp = client.get("/api/results")
        data = resp.get_json()
        assert data["results"] == []

    def test_get_results_with_data(self, client, seed_results):
        resp = client.get("/api/results")
        data = resp.get_json()
        assert len(data["results"]) == 2

    def test_get_results_limit(self, client, seed_results):
        resp = client.get("/api/results?limit=1")
        data = resp.get_json()
        assert len(data["results"]) == 1

    def test_get_results_filter_by_duration(self, client, seed_results):
        resp = client.get("/api/results?duration=60")
        data = resp.get_json()
        assert len(data["results"]) == 2
        for r in data["results"]:
            assert r["duration"] == 60

    def test_get_results_filter_by_duration_no_match(self, client, seed_results):
        resp = client.get("/api/results?duration=15")
        data = resp.get_json()
        assert len(data["results"]) == 0

    def test_get_results_filter_by_mode(self, client, seed_results):
        resp = client.get("/api/results?mode=words")
        data = resp.get_json()
        assert len(data["results"]) == 1
        assert data["results"][0]["mode"] == "words"

    def test_get_results_filter_by_mode_passage(self, client, seed_results):
        resp = client.get("/api/results?mode=passage")
        data = resp.get_json()
        assert len(data["results"]) == 1
        assert data["results"][0]["mode"] == "passage"

    def test_get_results_filter_by_mode_no_match(self, client, seed_results):
        resp = client.get("/api/results?mode=nonexistent")
        data = resp.get_json()
        assert len(data["results"]) == 0

    def test_get_results_filter_by_mode_and_duration(self, client, seed_results):
        resp = client.get("/api/results?mode=words&duration=60")
        data = resp.get_json()
        assert len(data["results"]) == 1
        assert data["results"][0]["mode"] == "words"
        assert data["results"][0]["duration"] == 60


class TestStats:
    def test_stats_empty(self, client):
        resp = client.get("/api/stats")
        data = resp.get_json()
        assert data["total_tests"] == 0
        assert data["avg_wpm"] == 0
        assert data["history"] == []

    def test_stats_with_data(self, client, seed_results):
        resp = client.get("/api/stats")
        data = resp.get_json()
        assert data["total_tests"] == 2

    def test_stats_filtered_by_duration(self, client, seed_results):
        resp = client.get("/api/stats?duration=60")
        data = resp.get_json()
        assert data["total_tests"] == 2
        assert data["best_wpm"] == 75.0

    def test_stats_filtered_by_duration_no_match(self, client, seed_results):
        resp = client.get("/api/stats?duration=15")
        data = resp.get_json()
        assert data["total_tests"] == 0
        assert data["avg_wpm"] == 0
        assert data["best_wpm"] == 0
        assert data["history"] == []

    def test_stats_filtered_by_mode_words(self, client, seed_results):
        resp = client.get("/api/stats?mode=words")
        data = resp.get_json()
        assert data["total_tests"] == 1
        assert data["best_wpm"] == 60.0

    def test_stats_filtered_by_mode_passage(self, client, seed_results):
        resp = client.get("/api/stats?mode=passage")
        data = resp.get_json()
        assert data["total_tests"] == 1
        assert data["best_wpm"] == 75.0

    def test_stats_filtered_by_mode_no_match(self, client, seed_results):
        resp = client.get("/api/stats?mode=nonexistent")
        data = resp.get_json()
        assert data["total_tests"] == 0
        assert data["best_wpm"] == 0
        assert data["history"] == []

    def test_stats_filtered_by_mode_and_duration(self, client, seed_results):
        resp = client.get("/api/stats?mode=words&duration=60")
        data = resp.get_json()
        assert data["total_tests"] == 1
        assert data["best_wpm"] == 60.0


class TestLessons:
    def test_get_lessons(self, client):
        resp = client.get("/api/lessons")
        data = resp.get_json()
        levels = data["levels"]
        assert len(levels) == 8
        # First lesson is always available
        assert levels[0]["lessons"][0]["status"] == "available"
        # Second lesson is locked (first not completed)
        assert levels[0]["lessons"][1]["status"] == "locked"

    def test_get_lesson_by_id(self, client):
        resp = client.get("/api/lesson/1.1")
        data = resp.get_json()
        assert data["id"] == "1.1"
        assert data["title"] == "Left Hand Home Keys"
        assert "text" in data

    def test_get_lesson_not_found(self, client):
        resp = client.get("/api/lesson/99.99")
        assert resp.status_code == 404

    def test_save_lesson_result_pass(self, client):
        resp = client.post(
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

    def test_save_lesson_result_fail(self, client):
        resp = client.post(
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

    def test_save_lesson_result_not_found(self, client):
        resp = client.post(
            "/api/lesson/99.99/result",
            data=json.dumps({"wpm": 40.0, "accuracy": 95.0, "errors": 0, "total_chars": 10, "correct_chars": 10}),
            content_type="application/json",
        )
        assert resp.status_code == 404

    def test_lesson_unlock_progression(self, client):
        # Complete lesson 1.1
        client.post(
            "/api/lesson/1.1/result",
            data=json.dumps({"wpm": 40.0, "accuracy": 95.0, "errors": 1, "total_chars": 80, "correct_chars": 76}),
            content_type="application/json",
        )
        # Lesson 1.2 should now be available
        resp = client.get("/api/lessons")
        levels = resp.get_json()["levels"]
        assert levels[0]["lessons"][0]["status"] == "completed"
        assert levels[0]["lessons"][1]["status"] == "available"


class TestCharErrors:
    def test_save_char_errors(self, client):
        # First create a result to link errors to
        res = client.post(
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
        resp = client.post(
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

    def test_save_empty_errors(self, client):
        resp = client.post(
            "/api/char-errors",
            data=json.dumps({"errors": []}),
            content_type="application/json",
        )
        assert resp.get_json()["status"] == "ok"


class TestWeakKeys:
    def test_weak_keys_empty(self, client):
        resp = client.get("/api/weak-keys")
        data = resp.get_json()
        assert data["weak_keys"] == []

    def test_weak_keys_with_data(self, client, seed_char_errors):
        resp = client.get("/api/weak-keys")
        data = resp.get_json()
        assert len(data["weak_keys"]) == 3
        # Most missed key first
        assert data["weak_keys"][0]["char"] == "t"
        assert data["weak_keys"][0]["count"] == 10

    def test_weak_keys_practice_empty(self, client):
        resp = client.get("/api/weak-keys/practice")
        data = resp.get_json()
        assert data["has_data"] is False
        assert data["text"] == ""

    def test_weak_keys_practice_with_data(self, client, seed_char_errors):
        resp = client.get("/api/weak-keys/practice")
        data = resp.get_json()
        assert data["has_data"] is True
        assert len(data["text"]) > 0
        assert len(data["weak_keys"]) == 3
