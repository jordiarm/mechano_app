# mechano_app

A typing speed tracker and training app with a dark terminal-inspired theme.

## Features

- **User accounts** — register and log in; all progress is scoped per user
- **Test** — measure your WPM and accuracy
  - **Words** — random common English and programming words
  - **Passage** — longer prose texts on tech topics
- **Games** — challenge modes with unique twists
  - **Sudden Death** — one mistake and the game is over
  - **Code** — real code snippets in Python, JS, SQL, Shell, TypeScript, Go, Rust, and more
  - **Custom** — paste your own text to practice with
- **Learn** — progressive lessons and targeted practice
  - **Lessons** — 8 levels (32 lessons) from home row to real-world code patterns, unlocked by meeting accuracy thresholds (85-90%)
  - **Weak keys** — generates words weighted toward your most-missed characters from the last 5 tests
- **Stats** — best/avg WPM, keys/sec, accuracy, and streak cards; WPM and accuracy charts over last 60 tests; history table, filterable by mode and duration
- **Leaderboard** — global ranking of all users by best WPM, with gold/silver/bronze highlights for top 3; filterable by mode and duration; your row is highlighted
- **Settings** — dark/light theme, toggle scanlines, sounds, particles, and screen shake
- **Effects** — keystroke particles, combo streaks, screen shake, sound effects (Web Audio API)

## Tech stack

- **Backend**: Python / Flask, SQLite
- **Frontend**: Vanilla JS, CSS, JetBrains Mono font

## Getting started

```bash
# Clone the repo
git clone https://github.com/jordiarmentia/mechano_app.git
cd mechano_app

# Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# (Optional) Set a secret key for session security
export SECRET_KEY="your-secret-key"

# Run the app
python app.py
```

Then open [http://localhost:5555](http://localhost:5555) in your browser.

## Project structure

```
app.py                        # Flask app, API routes, auth, SQLite setup, helpers
data/                         # Static data constants
  __init__.py                 # Re-exports all data constants
  words.py                    # WORD_POOL — 2,278 English + programming words
  lessons.py                  # LESSONS — progressive typing lessons
  passages.py                 # PASSAGES — 31 longer prose texts
  code_snippets.py            # CODE_SNIPPETS — real code from multiple languages
requirements.txt              # flask==3.1.0
pyproject.toml                # Ruff and pytest configuration
templates/auth.html           # Login and registration page
templates/index.html          # Single-page app (test, learn, stats, leaderboard views)
static/css/style.css          # All styles
static/js/engine.js           # Typing engine, lesson system, weak keys practice, effects
tests/conftest.py             # Pytest fixtures (test client, temp DB, seed data)
tests/test_api.py             # API route tests (61 tests)
.github/workflows/ci.yml     # CI pipeline (lint + test on push/PR to main)
```

## Development

```bash
ruff check .          # Lint
ruff format --check . # Format check
ruff format .         # Auto-format
pytest -v             # Run tests (61 tests)
```

## CI Pipeline

GitHub Actions workflow runs on push/PR to `main`:

- **lint** job: `ruff check .` and `ruff format --check .`
- **test** job: `pytest -v`
