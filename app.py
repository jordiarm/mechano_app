import asyncio
import os
import random
import sqlite3
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from ai_agent import generate_practice_text
from data import CODE_SNIPPETS, LESSONS, PASSAGES, WORD_POOL

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
DATABASE = Path(__file__).parent / "mechano.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
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
            user_id INTEGER REFERENCES users(id),
            expected_char TEXT NOT NULL,
            typed_char TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (result_id) REFERENCES results(id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS lesson_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
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

    # Migrations: add columns if missing (for existing databases)
    for table, column in [
        ("char_errors", "result_id"),
        ("results", "user_id"),
        ("char_errors", "user_id"),
        ("lesson_progress", "user_id"),
    ]:
        columns = [row[1] for row in db.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in columns:
            ref = "REFERENCES users(id)" if column == "user_id" else "REFERENCES results(id)"
            db.execute(f"ALTER TABLE {table} ADD COLUMN {column} INTEGER {ref}")

    # Migrate orphaned rows: assign to a default "admin" user
    has_orphans = db.execute("SELECT 1 FROM results WHERE user_id IS NULL LIMIT 1").fetchone()
    if has_orphans:
        existing = db.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
        if existing:
            admin_id = existing[0]
        else:
            cursor = db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("admin", generate_password_hash("admin")),
            )
            admin_id = cursor.lastrowid
        db.execute("UPDATE results SET user_id = ? WHERE user_id IS NULL", (admin_id,))
        db.execute("UPDATE char_errors SET user_id = ? WHERE user_id IS NULL", (admin_id,))
        db.execute("UPDATE lesson_progress SET user_id = ? WHERE user_id IS NULL", (admin_id,))

    # Indexes for common query patterns
    db.execute("CREATE INDEX IF NOT EXISTS idx_results_created_at ON results (created_at DESC)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_results_duration_mode ON results (duration, mode)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_results_user_id ON results (user_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_char_errors_result_id ON char_errors (result_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_char_errors_user_id ON char_errors (user_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_lesson_progress_lesson_passed ON lesson_progress (lesson_id, passed)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_lesson_progress_user_id ON lesson_progress (user_id)")
    db.commit()
    db.close()


# --- Auth helpers ---


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "unauthorized"}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


def current_user_id():
    return session.get("user_id")


# --- Lesson helpers ---


_LESSON_BY_ID = {lesson["id"]: lesson for level in LESSONS for lesson in level["lessons"]}

_ALL_LESSON_IDS = [lesson["id"] for level in LESSONS for lesson in level["lessons"]]


def _get_lesson_by_id(lesson_id):
    return _LESSON_BY_ID.get(lesson_id)


def _get_all_lesson_ids():
    return _ALL_LESSON_IDS


# --- Query helpers ---


def _build_results_filter():
    """Build WHERE clause and params from duration/mode query params, always scoped to current user."""
    clauses = ["user_id = ?"]
    params = [current_user_id()]
    duration = request.args.get("duration", None, type=int)
    mode = request.args.get("mode", None, type=str)
    if duration:
        clauses.append("duration = ?")
        params.append(duration)
    if mode:
        clauses.append("mode = ?")
        params.append(mode)
    where = "WHERE " + " AND ".join(clauses)
    return where, params


_WEAK_KEYS_SQL = """
    SELECT LOWER(expected_char) as ch, COUNT(*) as miss_count
    FROM char_errors
    WHERE result_id IN (SELECT id FROM results WHERE user_id = ? ORDER BY id DESC LIMIT 10)
      AND (expected_char BETWEEN 'a' AND 'z'
           OR expected_char BETWEEN 'A' AND 'Z')
    GROUP BY LOWER(expected_char)
    ORDER BY miss_count DESC
    LIMIT ?
"""


# --- Auth routes ---


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth.html", mode="register")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if len(username) < 2:
        return render_template("auth.html", mode="register", error="username must be at least 2 characters")
    if len(password) < 4:
        return render_template("auth.html", mode="register", error="password must be at least 4 characters")
    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        return render_template("auth.html", mode="register", error="username already taken")
    cursor = db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, generate_password_hash(password)),
    )
    db.commit()
    session["user_id"] = cursor.lastrowid
    session["username"] = username
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth.html", mode="login")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    db = get_db()
    user = db.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()
    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("auth.html", mode="login", error="invalid username or password")
    session["user_id"] = user["id"]
    session["username"] = username
    return redirect(url_for("index"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/api/me", methods=["GET"])
@login_required
def get_me():
    return jsonify({"user_id": current_user_id(), "username": session.get("username")})


# --- Page routes ---


@app.route("/")
@login_required
def index():
    return render_template("index.html", username=session.get("username"))


# --- Static data routes (auth required for consistency) ---


@app.route("/api/words", methods=["GET"])
@login_required
def get_words():
    count = request.args.get("count", 200, type=int)
    words = [random.choice(WORD_POOL) for _ in range(count)]
    return jsonify({"words": " ".join(words)})


@app.route("/api/passages", methods=["GET"])
@login_required
def get_passages():
    return jsonify({"passages": PASSAGES})


@app.route("/api/passage", methods=["GET"])
@login_required
def get_passage():
    idx = request.args.get("index", None, type=int)
    if idx is not None and 0 <= idx < len(PASSAGES):
        return jsonify(PASSAGES[idx])
    return jsonify(random.choice(PASSAGES))


@app.route("/api/code-snippets", methods=["GET"])
@login_required
def get_code_snippets():
    return jsonify({"snippets": CODE_SNIPPETS})


@app.route("/api/code-snippet", methods=["GET"])
@login_required
def get_code_snippet():
    idx = request.args.get("index", None, type=int)
    if idx is not None and 0 <= idx < len(CODE_SNIPPETS):
        return jsonify(CODE_SNIPPETS[idx])
    return jsonify(random.choice(CODE_SNIPPETS))


# --- User-scoped data routes ---


@app.route("/api/results", methods=["POST"])
@login_required
def save_result():
    data = request.get_json()
    db = get_db()
    cursor = db.execute(
        """INSERT INTO results (user_id, wpm, accuracy, errors, total_chars, correct_chars, streak, duration, mode)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            current_user_id(),
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
@login_required
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
@login_required
def get_stats():
    db = get_db()
    where, params = _build_results_filter()
    params = tuple(params)
    recent = db.execute(
        f"SELECT wpm, accuracy, streak, total_chars, duration, created_at FROM results {where} ORDER BY created_at DESC LIMIT 60",
        params,
    ).fetchall()
    row = db.execute(
        f"""
        SELECT
            COUNT(*) as total_tests,
            COALESCE(AVG(wpm), 0) as avg_wpm,
            COALESCE(MAX(wpm), 0) as best_wpm,
            COALESCE(AVG(accuracy), 0) as avg_accuracy,
            COALESCE(MAX(streak), 0) as best_streak,
            COALESCE(AVG(total_chars * 1.0 / duration), 0) as avg_kps,
            COALESCE(ROUND(MAX(wpm * (accuracy / 100.0) * (accuracy / 100.0)), 1), 0) as best_score
        FROM (SELECT * FROM results {where} ORDER BY created_at DESC LIMIT 60)
    """,
        params,
    ).fetchone()
    stats = dict(row)
    stats["history"] = [dict(r) for r in recent]

    return jsonify(stats)


@app.route("/api/lessons", methods=["GET"])
@login_required
def get_lessons():
    db = get_db()
    uid = current_user_id()
    # Get all passed lesson IDs
    rows = db.execute(
        "SELECT DISTINCT lesson_id FROM lesson_progress WHERE passed = 1 AND user_id = ?", (uid,)
    ).fetchall()
    completed = {row["lesson_id"] for row in rows}

    # Get best stats per lesson
    best_rows = db.execute(
        """
        SELECT lesson_id, MAX(wpm) as best_wpm, MAX(accuracy) as best_accuracy
        FROM lesson_progress WHERE user_id = ? GROUP BY lesson_id
    """,
        (uid,),
    ).fetchall()
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
@login_required
def get_lesson(lesson_id):
    lesson = _get_lesson_by_id(lesson_id)
    if not lesson:
        return jsonify({"error": "not found"}), 404
    return jsonify(lesson)


@app.route("/api/lesson/<lesson_id>/result", methods=["POST"])
@login_required
def save_lesson_result(lesson_id):
    lesson = _get_lesson_by_id(lesson_id)
    if not lesson:
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    passed = 1 if data["accuracy"] >= lesson["pass_accuracy"] else 0
    db = get_db()
    db.execute(
        """INSERT INTO lesson_progress (user_id, lesson_id, wpm, accuracy, errors, total_chars, correct_chars, passed)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            current_user_id(),
            lesson_id,
            data["wpm"],
            data["accuracy"],
            data["errors"],
            data["total_chars"],
            data["correct_chars"],
            passed,
        ),
    )
    db.commit()
    return jsonify({"status": "ok", "passed": bool(passed)})


@app.route("/api/char-errors", methods=["POST"])
@login_required
def save_char_errors():
    data = request.get_json()
    errors = data.get("errors", [])
    if not errors:
        return jsonify({"status": "ok"})
    result_id = data.get("result_id")
    uid = current_user_id()
    db = get_db()
    db.executemany(
        "INSERT INTO char_errors (result_id, user_id, expected_char, typed_char) VALUES (?, ?, ?, ?)",
        [(result_id, uid, err["expected"], err["typed"]) for err in errors],
    )
    db.commit()
    return jsonify({"status": "ok"})


@app.route("/api/leaderboard", methods=["GET"])
@login_required
def get_leaderboard():
    db = get_db()
    clauses = []
    params = []
    duration = request.args.get("duration", None, type=int)
    mode = request.args.get("mode", None, type=str)
    if duration:
        clauses.append("r.duration = ?")
        params.append(duration)
    if mode:
        clauses.append("r.mode = ?")
        params.append(mode)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = db.execute(
        f"""
        SELECT
            u.username,
            COALESCE(ROUND(AVG(r.wpm * (r.accuracy / 100.0) * (r.accuracy / 100.0)), 1), 0) as avg_score,
            COALESCE(ROUND(MAX(r.wpm * (r.accuracy / 100.0) * (r.accuracy / 100.0)), 1), 0) as best_score,
            COALESCE(MAX(r.wpm), 0) as best_wpm,
            COALESCE(ROUND(AVG(r.wpm), 1), 0) as avg_wpm,
            COALESCE(ROUND(AVG(r.accuracy), 1), 0) as avg_accuracy,
            COUNT(*) as total_tests
        FROM results r
        JOIN users u ON r.user_id = u.id
        {where}
        GROUP BY r.user_id, u.username
        ORDER BY avg_score DESC
        LIMIT 100
        """,
        params,
    ).fetchall()
    entries = [dict(row) for row in rows]
    return jsonify({"leaderboard": entries, "current_user": session.get("username")})


@app.route("/api/weak-keys", methods=["GET"])
@login_required
def get_weak_keys():
    db = get_db()
    rows = db.execute(_WEAK_KEYS_SQL, (current_user_id(), 10)).fetchall()
    keys = [{"char": row["ch"], "count": row["miss_count"]} for row in rows]
    return jsonify({"weak_keys": keys})


@app.route("/api/weak-keys/practice", methods=["GET"])
@login_required
def get_weak_keys_practice():
    """Generate practice words that focus on the user's weakest keys."""
    db = get_db()
    rows = db.execute(_WEAK_KEYS_SQL, (current_user_id(), 6)).fetchall()

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
    if len(top_words) >= count:
        selected = random.sample(top_words, count)
    else:
        selected = top_words[:]
        random.shuffle(selected)
    return jsonify(
        {
            "text": " ".join(selected),
            "weak_keys": weak_list,
            "has_data": True,
        }
    )


@app.route("/api/weak-keys/ai-practice", methods=["POST"])
@login_required
def get_weak_keys_ai_practice():
    """Generate AI-powered practice text targeting the user's weakest keys."""
    db = get_db()
    rows = db.execute(_WEAK_KEYS_SQL, (current_user_id(), 6)).fetchall()

    if not rows:
        return jsonify({"text": "", "weak_keys": [], "has_data": False})

    weak_list = [{"char": row["ch"], "count": row["miss_count"]} for row in rows]

    try:
        text = asyncio.run(generate_practice_text(weak_list))
    except Exception:
        return jsonify({"error": "AI generation failed"}), 502

    return jsonify({"text": text, "weak_keys": weak_list, "has_data": True})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5555)
