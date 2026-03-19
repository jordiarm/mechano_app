# mechano_app

Typing speed tracker and training app built with Flask.

## Tech stack

- **Backend**: Python / Flask, SQLite (`mechano.db`)
- **Frontend**: Vanilla JS, CSS (dark terminal-inspired theme)
- **Fonts**: JetBrains Mono (loaded from Google Fonts)

## Project structure

```
app.py                  # Flask app, API routes, lesson/word data, SQLite setup
requirements.txt        # flask==3.1.0
templates/index.html    # Single-page app (test, learn, stats views)
static/css/style.css    # All styles
static/js/engine.js     # Typing engine, lesson system, weak keys practice, effects
```

## Running

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
# Open http://localhost:5555
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
