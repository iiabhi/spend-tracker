# Spec: Date Filter For Profile Page

## Overview
This step implements the `/profile` page, currently a placeholder string ("Profile page — coming in Step 4"), and gives it the ability to filter a logged-in user's expenses by date range. The page lists the current user's expenses (most recent first) and adds a simple "from / to" date filter form that re-queries and re-renders the list scoped to that range, without requiring a page other than `/profile` itself. This is the first place expenses are displayed to a user, ahead of full expense CRUD (add/edit/delete) built in later steps.

## Depends on
- Step 1 (Database setup) — requires `get_db()`, `init_db()`, and the `expenses`/`users` tables.
- Step 2 (Authentication) — requires `login_required`, session-based auth, and a logged-in `user_id` to scope expenses to.

## Routes
- `GET /profile` — render the profile page with the current user's expenses, optionally filtered by `from`/`to` query-string dates — logged-in
  - Query params: `from` (YYYY-MM-DD, optional), `to` (YYYY-MM-DD, optional)
  - If neither is provided, show all of the user's expenses
  - If both are provided, show expenses where `date BETWEEN from AND to` (inclusive)
  - If only one is provided, filter with just that bound (`date >= from` or `date <= to`)
  - Invalid/malformed dates: ignore the bad param and treat it as not provided, do not error

## Database changes
No database changes. The existing `expenses` table (`id`, `user_id`, `amount`, `category`, `date`, `description`, `created_at`) is sufficient. Filtering is done with a `WHERE user_id = ?` plus optional `date` bounds, all parameterised.

## Templates
- **Create:** `templates/profile.html` — extends `base.html`; shows the user's name/email, a date-filter form (`from`/`to` inputs, submit via `GET`), and a table/list of matching expenses (date, category, amount, description); shows an empty-state message when no expenses match
- **Modify:** none

## Files to change
- `app.py` — replace the `profile()` placeholder with a real handler: read `from`/`to` from `request.args`, build the parameterised query, fetch the logged-in user's row and their filtered expenses, render `profile.html`

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (not touched in this step, but existing hashing must not be altered)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Keep the date filter server-side (GET query params), no JS-only filtering
- `profile()` must close its `get_db()` connection (`try/finally`)
- Validate `from`/`to` values look like `YYYY-MM-DD` before using them in the query; silently drop invalid ones rather than raising

## Definition of done
- [ ] Visiting `/profile` while logged in shows all of that user's expenses, most recent date first
- [ ] Visiting `/profile` while logged out redirects to `/login` (via existing `login_required`)
- [ ] Submitting the filter form with only a `from` date shows expenses on/after that date
- [ ] Submitting the filter form with only a `to` date shows expenses on/before that date
- [ ] Submitting the filter form with both `from` and `to` shows expenses within that inclusive range
- [ ] Submitting a filter range with no matching expenses shows an empty-state message instead of an error
- [ ] Passing a malformed date (e.g. `from=notadate`) does not crash the page and behaves as if that param were omitted
- [ ] A second seeded/registered user only ever sees their own expenses, never another user's
