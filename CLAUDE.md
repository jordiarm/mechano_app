# mechano_app

Typing speed tracker and training app built with Flask.

## Engineering standards

- Act as a **staff software engineer with 10+ years of experience**. Always find the optimal solution before implementation. Keep performance in mind at every step.
- **Always adhere to coding best practices** — clean code, proper naming, DRY, separation of concerns, consistent style. This applies to both code quality and project structure. Proactively identify and fix structural issues.

## Tech stack

- **Backend**: Python / Flask, SQLite (`mechano.db`)
- **AI**: OpenAI Agents SDK (`openai-agents`), `gpt-4o-mini`
- **Frontend**: Vanilla JS, CSS (dark terminal-inspired theme)
- **Fonts**: JetBrains Mono (loaded from Google Fonts)

## Project structure

```
app.py                        # Flask app, API routes, auth, SQLite setup, helpers
ai_agent.py                   # OpenAI Agents SDK — practice text generation agent
data/                         # Static data constants (extracted from app.py)
  __init__.py                 # Re-exports all data constants
  words.py                    # WORD_POOL — 2,278 English + programming words
  lessons.py                  # LESSONS — progressive typing lessons
  passages.py                 # PASSAGES — 31 longer prose texts
  code_snippets.py            # CODE_SNIPPETS — real code from multiple languages
requirements.txt              # flask, openai-agents, python-dotenv
.env                          # OPENAI_API_KEY (not committed)
pyproject.toml                # Ruff and pytest configuration
templates/auth.html           # Login and registration page
templates/index.html          # Single-page app (test, learn, stats, leaderboard views)
static/css/style.css          # All styles
static/js/engine.js           # Typing engine, lesson system, weak keys practice, effects
tests/conftest.py             # Pytest fixtures (test client, temp DB, seed data)
tests/test_api.py             # API route tests (61 tests)
.github/workflows/ci.yml     # CI pipeline (lint + test on push/PR to main)
```

## Running

```bash
uv sync
echo 'OPENAI_API_KEY=sk-...' > .env
export SECRET_KEY="your-secret-key"  # optional, defaults to dev key
uv run python app.py
# Open http://localhost:5555
```

## CI Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push/PR to `main`:
- **lint** job: `ruff check .` and `ruff format --check .`
- **test** job: `pytest -v`

## Linting and testing

```bash
uv run ruff check .          # Lint
uv run ruff format --check . # Format check
uv run ruff format .         # Auto-format
uv run pytest -v             # Run tests
```

## Key design decisions

- Static data (words, lessons, passages, code snippets) lives in `data/` module, keeping `app.py` focused on routes and logic
- Test tab modes: words, passage. Games tab modes: sudden_death (one mistake = game over), code (real code snippets), custom (user-pasted text)
- Games tab follows the learn tab pattern: browser view with cards → active game view with typing container → results overlay
- User authentication via Flask sessions and werkzeug password hashing; all data is scoped per user via `user_id` FK columns
- All data (test results, lesson progress, character errors) is stored in SQLite locally — no remote backend
- Lessons unlock progressively; passing requires accuracy threshold (85-90%), no WPM gate
- Weak keys practice generates words weighted toward the user's most-missed characters from the last 10 tests (scoped via `result_id` FK on `char_errors`); practice text is deduplicated via `random.sample` (no repeated words)
- AI-powered weak keys practice (`/api/weak-keys/ai-practice`) uses the OpenAI Agents SDK to generate coherent sentences emphasising the user's weak characters; the agent is defined in `ai_agent.py` and uses `gpt-4o-mini`; the frontend tracks `weak.aiGenerated` so retry/restart calls the correct generator
- Typing containers use a 3-line sliding window (translateY) instead of scrolling
- Sound effects use Web Audio API (no audio files)
- Stats view filters by test duration via a toggle bar (15s/30s/60s/2m/all, default 60s) and by mode (all/words/passage, default all); `/api/stats` and `/api/results` accept optional `?duration=` and `?mode=` query params, combinable
- Stats overview cards and charts are scoped to the last 60 tests (not all-time); `/api/stats` aggregates via a subquery with `LIMIT 60`
- Stats cards: avg WPM, best WPM, avg accuracy, avg keys/sec, best score, best streak; `avg_kps` is computed as `total_chars / duration`; `best_score` is computed as `MAX(wpm * (accuracy/100)²)`
- Leaderboard view (`/api/leaderboard`) ranks all users by best WPM (GROUP BY user, ORDER BY MAX(wpm) DESC, LIMIT 100); supports the same `?duration=` and `?mode=` filters as stats; returns `current_user` so the client can highlight the logged-in user's row; top 3 rows styled gold/silver/bronze
- `WORD_POOL` is deduplicated; lesson lookups use pre-built dicts (`_LESSON_BY_ID`, `_ALL_LESSON_IDS`) for O(1) access
- `char_errors` bulk insert uses `executemany`; `get_results`/`get_stats` use parameterized WHERE clauses instead of duplicated SQL branches
- `engine.js` shares a `renderTextToDisplay()` helper across test/lesson/weak-keys modes, and a `renderLineChart()` helper for both WPM and accuracy charts

## Database tables

- `users` — registered accounts (username, password_hash); all other tables reference `users(id)` via `user_id` FK
- `results` — test results (user_id, WPM, accuracy, errors, streak, duration, mode)
- `lesson_progress` — per-lesson attempts with pass/fail (user_id scoped)
- `char_errors` — every individual character miss (user_id, result_id FK, expected vs typed), used for weak keys analysis; queries filter to last 10 results

## Issue log

> **Instructions for Claude:** When you encounter and resolve a bug, lint failure, test failure, architectural issue, or any non-trivial problem during development, log it here. Each entry should capture what went wrong, why, and how it was fixed. This log helps you avoid repeating mistakes and builds project-specific intuition over time. Keep entries concise.

### 2026-03-20 — Unused imports and lint violations on CI setup

- **What:** `app.py` had unused imports (`json`, `datetime`) and a duplicate `if`/`elif` branch (ruff SIM114). `tests/conftest.py` had unused imports (`tempfile`, `Path`). All lesson/passage data strings exceeded the 120-char line limit (E501).
- **Why:** The unused imports were left over from earlier development. The SIM114 was two branches with identical bodies that could be combined with `or`. E501 violations were unavoidable in content strings.
- **Fix:** Removed unused imports. Combined the duplicate branches into `if idx == 0 or all_ids[idx - 1] in completed:`. Added `E501` to ruff's ignore list in `pyproject.toml` since long lines in data strings are expected and harmless.

### 2026-03-20 — Wrong test assertions for duration filter "no match" case

- **What:** `test_stats_filtered_by_duration_no_match` failed because it asserted `best_wpm == 75.0` and `avg_accuracy == 96.5` — values from the seed data — when filtering by duration=15 which has zero matching results.
- **Why:** Copy-paste error from the positive test case. The "no match" test should assert all values are zero/empty since no results exist for that duration.
- **Fix:** Replaced assertions with `best_wpm == 0` and `history == []`. Lesson: always review assertion values against the test scenario, especially for negative/empty cases.

### 2026-03-20 — `CREATE TABLE IF NOT EXISTS` doesn't add new columns to existing tables

- **What:** After adding `result_id` FK column to `char_errors`, the weak keys section silently disappeared. The `/api/weak-keys` query failed because the `result_id` column didn't exist in the running database, and the JS `try/catch` swallowed the error.
- **Why:** `CREATE TABLE IF NOT EXISTS` skips entirely when the table already exists — it does not diff the schema or add missing columns. The existing `mechano.db` kept the old schema without `result_id`.
- **Fix:** Added an auto-migration in `init_db()` that checks `PRAGMA table_info(char_errors)` for the `result_id` column and runs `ALTER TABLE` if missing. Lesson: whenever adding columns to existing tables, always add a migration step — `CREATE TABLE IF NOT EXISTS` is only for first-time creation.

### 2026-03-26 — AI practice retry reverted to non-AI text

- **What:** After finishing an AI-generated weak keys practice and clicking retry (or pressing Enter), the next session used the regular word-pool text instead of generating new AI text.
- **Why:** The retry handler (`btn-retry` click and Enter key shortcut) unconditionally called `startWeakPractice()` without checking whether the session was AI-generated.
- **Fix:** Added `weak.aiGenerated` flag to the weak keys state. Set it in `startWeakPractice()` (false) and `startAiPractice()` (true). Both retry paths now check the flag to call the correct function.
