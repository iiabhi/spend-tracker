# Spec: Authentication

## Overview
This step implements user registration, login, and session-based authentication for Spendly. The `register.html` and `login.html` templates already exist and POST to `/register` and `/login` respectively, rendering an `{{ error }}` block on failure — this step wires those forms up to real handlers backed by the `users` table. Once complete, a visitor can create an account, sign in, and have their identity persisted in a Flask session, unlocking the logged-in areas of the app (profile, expenses) built in later steps.

## Depends on
Step 1 (Database setup) — requires `get_db()`, `init_db()`, and the `users` table to already exist and work, which they do.

## Routes
- `GET /register` — render registration form — public (already exists, unchanged)
- `POST /register` — create a new user, hash password, log them in, redirect to `/profile` — public
- `GET /login` — render login form — public (already exists, unchanged)
- `POST /login` — verify credentials, start session, redirect to `/profile` — public
- `GET /logout` — clear session, redirect to `/login` — logged-in (currently a placeholder string; replace it)

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email`, `password_hash`, `created_at`) is sufficient.

## Templates
- **Create:** none
- **Modify:** none — `login.html` and `register.html` already POST to the correct routes and render `{{ error }}`; no template changes are needed

## Files to change
- `app.py` — implement `POST /register`, `POST /login`, `GET /logout`; add a `login_required` check usable by future routes; set `app.secret_key` for session support

## Files to create
- None

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash` / `check_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use Flask's built-in `session` for auth state (store `user_id`); do not build a custom token/cookie scheme
- On registration/login failure, re-render the same template with a populated `error` message and HTTP 200 — do not redirect on failure
- Validate email uniqueness at registration time and return a friendly `error` (e.g. "An account with that email already exists") rather than letting the `UNIQUE` constraint raise an unhandled exception
- Registration and login handlers must close their `get_db()` connection (use `try/finally` or a `with` pattern consistent with `db.py`)

## Definition of done
- [ ] Visiting `/register`, submitting a new name/email/password creates a row in `users` with a hashed password and redirects to `/profile`
- [ ] Submitting `/register` with an email that already exists re-renders `register.html` with an `error` message and does not create a duplicate row
- [ ] Visiting `/login` with correct credentials for a seeded user redirects to `/profile` and sets a session
- [ ] Visiting `/login` with an incorrect password or unknown email re-renders `login.html` with an `error` message
- [ ] Visiting `/logout` while logged in clears the session and redirects to `/login`
- [ ] Restarting the Flask dev server and revisiting `/profile` without a session no longer silently succeeds (even if `/profile` itself is still a placeholder until Step 4, the session check must be in place)
