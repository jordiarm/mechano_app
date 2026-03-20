# mechano_app

Typing speed tracker and training app built with Flask.

## Tech stack

- **Backend**: Python / Flask, SQLite (`mechano.db`)
- **Frontend**: Vanilla JS, CSS (dark terminal-inspired theme)
- **Fonts**: JetBrains Mono (loaded from Google Fonts)

## Project structure

```
app.py                        # Flask app, API routes, lesson/word data, SQLite setup
requirements.txt              # flask==3.1.0
pyproject.toml                # Ruff and pytest configuration
templates/index.html          # Single-page app (test, learn, stats views)
static/css/style.css          # All styles
static/js/engine.js           # Typing engine, lesson system, weak keys practice, effects
tests/conftest.py             # Pytest fixtures (test client, temp DB, seed data)
tests/test_api.py             # API route tests (26 tests)
.github/workflows/ci.yml     # CI pipeline (lint + test on push/PR to main)
```

## Running

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
# Open http://localhost:5555
```

## CI Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push/PR to `main`:
- **lint** job: `ruff check .` and `ruff format --check .`
- **test** job: `pytest -v`

## Linting and testing

```bash
ruff check .          # Lint
ruff format --check . # Format check
ruff format .         # Auto-format
pytest -v             # Run tests
```

## Key design decisions

- All data (test results, lesson progress, character errors) is stored in SQLite locally — no auth, no remote backend
- Lessons unlock progressively; passing requires accuracy threshold (85-90%), no WPM gate
- Weak keys practice generates words weighted toward the user's most-missed characters
- Typing containers use a 3-line sliding window (translateY) instead of scrolling
- Sound effects use Web Audio API (no audio files)

## Database tables

- `results` — test results (WPM, accuracy, errors, streak, duration, mode)
- `lesson_progress` — per-lesson attempts with pass/fail
- `char_errors` — every individual character miss (expected vs typed), used for weak keys analysis

## Issue log

> **Instructions for Claude:** When you encounter and resolve a bug, lint failure, test failure, architectural issue, or any non-trivial problem during development, log it here. Each entry should capture what went wrong, why, and how it was fixed. This log helps you avoid repeating mistakes and builds project-specific intuition over time. Keep entries concise.

### 2026-03-20 — Unused imports and lint violations on CI setup

- **What:** `app.py` had unused imports (`json`, `datetime`) and a duplicate `if`/`elif` branch (ruff SIM114). `tests/conftest.py` had unused imports (`tempfile`, `Path`). All lesson/passage data strings exceeded the 120-char line limit (E501).
- **Why:** The unused imports were left over from earlier development. The SIM114 was two branches with identical bodies that could be combined with `or`. E501 violations were unavoidable in content strings.
- **Fix:** Removed unused imports. Combined the duplicate branches into `if idx == 0 or all_ids[idx - 1] in completed:`. Added `E501` to ruff's ignore list in `pyproject.toml` since long lines in data strings are expected and harmless.
