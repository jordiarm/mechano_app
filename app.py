import random
import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request

from data import CODE_SNIPPETS, LESSONS, PASSAGES, WORD_POOL

app = Flask(__name__)
DATABASE = Path(__file__).parent / "mechano.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wpm REAL NOT NULL,
            accuracy REAL NOT NULL,
            errors INTEGER NOT NULL,
            total_chars INTEGER NOT NULL,
            correct_chars INTEGER NOT NULL,
            streak INTEGER NOT NULL DEFAULT 0,
            duration INTEGER NOT NULL,
            mode TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS char_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id INTEGER,
            expected_char TEXT NOT NULL,
            typed_char TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (result_id) REFERENCES results(id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS lesson_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id TEXT NOT NULL,
            wpm REAL NOT NULL,
            accuracy REAL NOT NULL,
            errors INTEGER NOT NULL,
            total_chars INTEGER NOT NULL,
            correct_chars INTEGER NOT NULL,
            passed INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Migrate: add result_id to char_errors if missing
    columns = [row[1] for row in db.execute("PRAGMA table_info(char_errors)").fetchall()]
    if "result_id" not in columns:
        db.execute("ALTER TABLE char_errors ADD COLUMN result_id INTEGER REFERENCES results(id)")
    db.commit()
    db.close()


_LESSON_BY_ID = {lesson["id"]: lesson for level in LESSONS for lesson in level["lessons"]}

_ALL_LESSON_IDS = [lesson["id"] for level in LESSONS for lesson in level["lessons"]]


def _get_lesson_by_id(lesson_id):
    return _LESSON_BY_ID.get(lesson_id)


def _get_all_lesson_ids():
    return _ALL_LESSON_IDS


def _build_results_filter():
    """Build WHERE clause and params from duration/mode query params."""
    clauses = []
    params = []
    duration = request.args.get("duration", None, type=int)
    mode = request.args.get("mode", None, type=str)
    if duration:
        clauses.append("duration = ?")
        params.append(duration)
    if mode:
        clauses.append("mode = ?")
        params.append(mode)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where, params


_WEAK_KEYS_SQL = """
    SELECT LOWER(expected_char) as ch, COUNT(*) as miss_count
    FROM char_errors
    WHERE result_id IN (SELECT id FROM results ORDER BY id DESC LIMIT 10)
      AND (expected_char BETWEEN 'a' AND 'z'
           OR expected_char BETWEEN 'A' AND 'Z')
    GROUP BY LOWER(expected_char)
    ORDER BY miss_count DESC
    LIMIT ?
"""


# --- Routes ---


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/words", methods=["GET"])
def get_words():
    count = request.args.get("count", 200, type=int)
    words = [random.choice(WORD_POOL) for _ in range(count)]
    return jsonify({"words": " ".join(words)})


@app.route("/api/passages", methods=["GET"])
def get_passages():
    return jsonify({"passages": PASSAGES})


@app.route("/api/passage", methods=["GET"])
def get_passage():
    idx = request.args.get("index", None, type=int)
    if idx is not None and 0 <= idx < len(PASSAGES):
        return jsonify(PASSAGES[idx])
    return jsonify(random.choice(PASSAGES))


@app.route("/api/code-snippets", methods=["GET"])
def get_code_snippets():
    return jsonify({"snippets": CODE_SNIPPETS})


@app.route("/api/code-snippet", methods=["GET"])
def get_code_snippet():
    idx = request.args.get("index", None, type=int)
    if idx is not None and 0 <= idx < len(CODE_SNIPPETS):
        return jsonify(CODE_SNIPPETS[idx])
    return jsonify(random.choice(CODE_SNIPPETS))


@app.route("/api/results", methods=["POST"])
def save_result():
    data = request.get_json()
    db = get_db()
    cursor = db.execute(
        """INSERT INTO results (wpm, accuracy, errors, total_chars, correct_chars, streak, duration, mode)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["wpm"],
            data["accuracy"],
            data["errors"],
            data["total_chars"],
            data["correct_chars"],
            data["streak"],
            data["duration"],
            data["mode"],
        ),
    )
    result_id = cursor.lastrowid
    db.commit()
    return jsonify({"status": "ok", "id": result_id})


@app.route("/api/results", methods=["GET"])
def get_results():
    db = get_db()
    limit = request.args.get("limit", 50, type=int)
    where, params = _build_results_filter()
    params.append(limit)
    rows = db.execute(
        f"SELECT * FROM results {where} ORDER BY created_at DESC LIMIT ?",
        params,
    ).fetchall()
    results = [dict(row) for row in rows]
    return jsonify({"results": results})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    db = get_db()
    where, params = _build_results_filter()
    params = tuple(params)
    row = db.execute(
        f"""
        SELECT
            COUNT(*) as total_tests,
            COALESCE(AVG(wpm), 0) as avg_wpm,
            COALESCE(MAX(wpm), 0) as best_wpm,
            COALESCE(AVG(accuracy), 0) as avg_accuracy,
            COALESCE(MAX(streak), 0) as best_streak,
            COALESCE(SUM(total_chars), 0) as total_chars_typed
        FROM results {where}
    """,
        params,
    ).fetchone()
    recent = db.execute(
        f"SELECT wpm, accuracy, streak, created_at FROM results {where} ORDER BY created_at DESC LIMIT 20",
        params,
    ).fetchall()
    stats = dict(row)
    stats["history"] = [dict(r) for r in recent]

    return jsonify(stats)


@app.route("/api/lessons", methods=["GET"])
def get_lessons():
    db = get_db()
    # Get all passed lesson IDs
    rows = db.execute("SELECT DISTINCT lesson_id FROM lesson_progress WHERE passed = 1").fetchall()
    completed = {row["lesson_id"] for row in rows}

    # Get best stats per lesson
    best_rows = db.execute("""
        SELECT lesson_id, MAX(wpm) as best_wpm, MAX(accuracy) as best_accuracy
        FROM lesson_progress GROUP BY lesson_id
    """).fetchall()
    best_stats = {row["lesson_id"]: dict(row) for row in best_rows}

    all_ids = _get_all_lesson_ids()
    id_to_idx = {lid: i for i, lid in enumerate(all_ids)}
    result = []
    for level in LESSONS:
        level_data = {
            "level": level["level"],
            "level_name": level["level_name"],
            "lessons": [],
        }
        for lesson in level["lessons"]:
            lid = lesson["id"]
            idx = id_to_idx[lid]
            # Available if first lesson or previous lesson completed
            if idx == 0 or all_ids[idx - 1] in completed:
                status = "completed" if lid in completed else "available"
            else:
                status = "locked"

            entry = {
                "id": lid,
                "title": lesson["title"],
                "description": lesson["description"],
                "keys": lesson["keys"],
                "pass_accuracy": lesson["pass_accuracy"],
                "status": status,
            }
            if lid in best_stats:
                entry["best_wpm"] = best_stats[lid]["best_wpm"]
                entry["best_accuracy"] = best_stats[lid]["best_accuracy"]
            level_data["lessons"].append(entry)
        result.append(level_data)

    return jsonify({"levels": result})


@app.route("/api/lesson/<lesson_id>", methods=["GET"])
def get_lesson(lesson_id):
    lesson = _get_lesson_by_id(lesson_id)
    if not lesson:
        return jsonify({"error": "not found"}), 404
    return jsonify(lesson)


@app.route("/api/lesson/<lesson_id>/result", methods=["POST"])
def save_lesson_result(lesson_id):
    lesson = _get_lesson_by_id(lesson_id)
    if not lesson:
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    passed = 1 if data["accuracy"] >= lesson["pass_accuracy"] else 0
    db = get_db()
    db.execute(
        """INSERT INTO lesson_progress (lesson_id, wpm, accuracy, errors, total_chars, correct_chars, passed)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (lesson_id, data["wpm"], data["accuracy"], data["errors"], data["total_chars"], data["correct_chars"], passed),
    )
    db.commit()
    return jsonify({"status": "ok", "passed": bool(passed)})


@app.route("/api/char-errors", methods=["POST"])
def save_char_errors():
    data = request.get_json()
    errors = data.get("errors", [])
    if not errors:
        return jsonify({"status": "ok"})
    result_id = data.get("result_id")
    db = get_db()
    db.executemany(
        "INSERT INTO char_errors (result_id, expected_char, typed_char) VALUES (?, ?, ?)",
        [(result_id, err["expected"], err["typed"]) for err in errors],
    )
    db.commit()
    return jsonify({"status": "ok"})


@app.route("/api/weak-keys", methods=["GET"])
def get_weak_keys():
    db = get_db()
    rows = db.execute(_WEAK_KEYS_SQL, (10,)).fetchall()
    keys = [{"char": row["ch"], "count": row["miss_count"]} for row in rows]
    return jsonify({"weak_keys": keys})


@app.route("/api/weak-keys/practice", methods=["GET"])
def get_weak_keys_practice():
    """Generate practice words that focus on the user's weakest keys."""
    db = get_db()
    rows = db.execute(_WEAK_KEYS_SQL, (6,)).fetchall()

    if not rows:
        return jsonify({"text": "", "weak_keys": [], "has_data": False})

    weak_chars = {row["ch"] for row in rows}
    weak_list = [{"char": row["ch"], "count": row["miss_count"]} for row in rows]

    # Score each word in WORD_POOL by how many weak chars it contains
    scored = []
    for word in WORD_POOL:
        score = sum(1 for c in word.lower() if c in weak_chars)
        if score > 0:
            scored.append((score, word))
    scored.sort(key=lambda x: -x[0])

    # Take the top words, with some randomness
    top_words = [w for _, w in scored[:60]]
    if len(top_words) < 20:
        # Fallback: generate letter combos if not enough matching words
        for ch in weak_chars:
            top_words.extend([ch * 3, ch + "a", "a" + ch, ch + "e", "e" + ch])

    count = min(50, max(30, len(top_words)))
    selected = [random.choice(top_words) for _ in range(count)]
    return jsonify(
        {
            "text": " ".join(selected),
            "weak_keys": weak_list,
            "has_data": True,
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5555)
