# mechano_app

A typing speed tracker and training app with a dark terminal-inspired theme.

## Features

- **Typing tests** — measure your WPM and accuracy
- **Progressive lessons** — unlock new lessons by meeting accuracy thresholds (85-90%)
- **Weak keys practice** — generates words weighted toward your most-missed characters
- **Stats tracking** — all results stored locally in SQLite

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

# Run the app
python app.py
```

Then open [http://localhost:5555](http://localhost:5555) in your browser.

## Project structure

```
app.py                  # Flask app, API routes, lesson/word data, SQLite setup
requirements.txt        # Flask dependency
templates/index.html    # Single-page app (test, learn, stats views)
static/css/style.css    # All styles
static/js/engine.js     # Typing engine, lesson system, weak keys practice, effects
```
