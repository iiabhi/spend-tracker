# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

"Spendly" is a Flask expense tracker built as a step-by-step learning project. The codebase is intentionally incomplete: routes and the database layer exist as stubs with comments describing what each step should implement (see `app.py` and `database/db.py`). Treat comments like `# Students will implement these` and `# coming in Step N` as the spec for that piece, not as dead code to remove.

## Commands

```bash
# activate the venv (already created at ./venv)
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run the dev server (http://localhost:5001)
python app.py

# run tests
pytest
pytest path/to/test_file.py::test_name   # single test
```

There is no lint/format tooling configured in this repo.

## Architecture

- **`app.py`** — single-file Flask app; all routes are defined here (no blueprints). Currently only GET routes that render templates exist (`/`, `/register`, `/login`, `/terms`); `/logout`, `/profile`, and the `/expenses/*` CRUD routes are placeholders returning plain strings until their corresponding step is implemented.
- **`database/db.py`** — intended to hold `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (creates tables with `CREATE TABLE IF NOT EXISTS`), and `seed_db()` (sample dev data). Not yet implemented — this is Step 1 of the build progression.
- **`templates/`** — Jinja2 templates, all extending `templates/base.html` (nav, footer, shared `<head>`). Forms in `login.html`/`register.html` already POST to `/login` and `/register` and render an `{{ error }}` block, so the auth routes need to handle POST and pass `error` on failure.
- **`static/css/style.css`** — shared/base styles; **`static/css/landing.css`** — landing-page-only styles loaded via the `head` block.
- **`static/js/main.js`** — currently empty; add JS here as interactive features are built.
- SQLite is the database (per `db.py`'s docstring); the compiled DB file `expense_tracker.db` is gitignored and created at runtime by `init_db()`.
