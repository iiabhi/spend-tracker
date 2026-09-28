"""
Tests for Spec 06: Date Filter For Profile Page.

Derived from .claude/specs/06-date-filter-profile-page.md (Routes, Rules for
implementation, Definition of Done). These tests exercise externally
observable behavior only (HTTP responses, redirects, rendered content) and
do not depend on internal implementation details of app.py.
"""
import pytest

from tests.conftest import create_expense, create_user, login


# --------------------------------------------------------------------- #
# Access control
# --------------------------------------------------------------------- #

def test_profile_logged_out_redirects_to_login(test_client):
    response = test_client.get("/profile")
    assert response.status_code in (301, 302)
    assert "/login" in response.headers["Location"]


def test_profile_logged_out_does_not_leak_data(test_client):
    response = test_client.get("/profile", follow_redirects=True)
    assert response.status_code == 200
    # Should land on the login page, not a profile/expenses page.
    assert b"login" in response.data.lower() or b"password" in response.data.lower()


# --------------------------------------------------------------------- #
# Basic listing (no filter)
# --------------------------------------------------------------------- #

def test_profile_logged_in_shows_all_expenses(test_client):
    user_id = create_user()
    create_expense(user_id, 10.00, "Food", "2026-01-05", "Lunch")
    create_expense(user_id, 20.00, "Bills", "2026-01-10", "Electricity")
    login(test_client, user_id)

    response = test_client.get("/profile")

    assert response.status_code == 200
    assert b"Lunch" in response.data
    assert b"Electricity" in response.data


def test_profile_no_filter_orders_most_recent_first(test_client):
    user_id = create_user()
    create_expense(user_id, 10.00, "Food", "2026-01-05", "Older Expense")
    create_expense(user_id, 20.00, "Bills", "2026-01-20", "Newer Expense")
    login(test_client, user_id)

    response = test_client.get("/profile")
    body = response.data.decode()

    assert response.status_code == 200
    older_index = body.find("Older Expense")
    newer_index = body.find("Newer Expense")
    assert older_index != -1 and newer_index != -1
    assert newer_index < older_index


def test_profile_shows_user_name_or_email(test_client):
    user_id = create_user(name="Alice Example", email="alice@example.com")
    login(test_client, user_id)

    response = test_client.get("/profile")

    assert response.status_code == 200
    assert b"Alice Example" in response.data or b"alice@example.com" in response.data


# --------------------------------------------------------------------- #
# Filtering: from only
# --------------------------------------------------------------------- #

def test_filter_from_only_shows_on_or_after(test_client):
    user_id = create_user()
    create_expense(user_id, 10.00, "Food", "2026-01-01", "Too Early")
    create_expense(user_id, 20.00, "Food", "2026-01-10", "On Boundary")
    create_expense(user_id, 30.00, "Food", "2026-01-20", "After Boundary")
    login(test_client, user_id)

    response = test_client.get("/profile?from=2026-01-10")

    assert response.status_code == 200
    assert b"Too Early" not in response.data
    assert b"On Boundary" in response.data
    assert b"After Boundary" in response.data


# --------------------------------------------------------------------- #
# Filtering: to only
# --------------------------------------------------------------------- #

def test_filter_to_only_shows_on_or_before(test_client):
    user_id = create_user()
    create_expense(user_id, 10.00, "Food", "2026-01-01", "Before Boundary")
    create_expense(user_id, 20.00, "Food", "2026-01-10", "On Boundary")
    create_expense(user_id, 30.00, "Food", "2026-01-20", "Too Late")
    login(test_client, user_id)

    response = test_client.get("/profile?to=2026-01-10")

    assert response.status_code == 200
    assert b"Before Boundary" in response.data
    assert b"On Boundary" in response.data
    assert b"Too Late" not in response.data


# --------------------------------------------------------------------- #
# Filtering: both from and to (inclusive range)
# --------------------------------------------------------------------- #

def test_filter_from_and_to_inclusive_range(test_client):
    user_id = create_user()
    create_expense(user_id, 10.00, "Food", "2026-01-01", "Before Range")
    create_expense(user_id, 20.00, "Food", "2026-01-05", "Start Boundary")
    create_expense(user_id, 30.00, "Food", "2026-01-10", "Inside Range")
    create_expense(user_id, 40.00, "Food", "2026-01-15", "End Boundary")
    create_expense(user_id, 50.00, "Food", "2026-01-20", "After Range")
    login(test_client, user_id)

    response = test_client.get("/profile?from=2026-01-05&to=2026-01-15")

    assert response.status_code == 200
    assert b"Before Range" not in response.data
    assert b"Start Boundary" in response.data
    assert b"Inside Range" in response.data
    assert b"End Boundary" in response.data
    assert b"After Range" not in response.data


# --------------------------------------------------------------------- #
# Empty-state / no matches
# --------------------------------------------------------------------- #

def test_filter_no_matches_shows_empty_state_not_error(test_client):
    user_id = create_user()
    create_expense(user_id, 10.00, "Food", "2026-01-01", "Only Expense")
    login(test_client, user_id)

    response = test_client.get("/profile?from=2030-01-01&to=2030-12-31")

    assert response.status_code == 200
    assert b"Only Expense" not in response.data
    # Some empty-state indication should be present rather than a blank/error page.
    lowered = response.data.lower()
    assert b"no expense" in lowered or b"no results" in lowered or b"empty" in lowered


# --------------------------------------------------------------------- #
# Malformed dates
# --------------------------------------------------------------------- #

def test_malformed_from_date_does_not_crash_and_is_ignored(test_client):
    user_id = create_user()
    create_expense(user_id, 10.00, "Food", "2026-01-01", "Some Expense")
    login(test_client, user_id)

    response = test_client.get("/profile?from=notadate")

    assert response.status_code == 200
    # Treated as if 'from' were omitted, so the expense should still show.
    assert b"Some Expense" in response.data


def test_malformed_to_date_does_not_crash_and_is_ignored(test_client):
    user_id = create_user()
    create_expense(user_id, 10.00, "Food", "2026-01-01", "Some Expense")
    login(test_client, user_id)

    response = test_client.get("/profile?to=not-a-real-date")

    assert response.status_code == 200
    assert b"Some Expense" in response.data


def test_malformed_both_dates_behaves_as_unfiltered(test_client):
    user_id = create_user()
    create_expense(user_id, 10.00, "Food", "2026-01-01", "Expense A")
    create_expense(user_id, 20.00, "Food", "2026-06-01", "Expense B")
    login(test_client, user_id)

    response = test_client.get("/profile?from=garbage&to=alsogarbage")

    assert response.status_code == 200
    assert b"Expense A" in response.data
    assert b"Expense B" in response.data


# --------------------------------------------------------------------- #
# Per-user isolation
# --------------------------------------------------------------------- #

def test_user_only_sees_own_expenses(test_client):
    user_a = create_user(name="User A", email="a@example.com")
    user_b = create_user(name="User B", email="b@example.com")
    create_expense(user_a, 10.00, "Food", "2026-01-01", "Belongs To A")
    create_expense(user_b, 20.00, "Food", "2026-01-01", "Belongs To B")

    login(test_client, user_a)
    response = test_client.get("/profile")

    assert response.status_code == 200
    assert b"Belongs To A" in response.data
    assert b"Belongs To B" not in response.data


def test_second_user_only_sees_own_expenses_with_filter(test_client):
    user_a = create_user(name="User A", email="a2@example.com")
    user_b = create_user(name="User B", email="b2@example.com")
    create_expense(user_a, 10.00, "Food", "2026-01-10", "A Expense")
    create_expense(user_b, 20.00, "Food", "2026-01-10", "B Expense")

    login(test_client, user_b)
    response = test_client.get("/profile?from=2026-01-01&to=2026-01-31")

    assert response.status_code == 200
    assert b"B Expense" in response.data
    assert b"A Expense" not in response.data


# --------------------------------------------------------------------- #
# Template extends base.html (basic sanity, not implementation detail)
# --------------------------------------------------------------------- #

def test_profile_page_includes_filter_form_inputs(test_client):
    user_id = create_user()
    login(test_client, user_id)

    response = test_client.get("/profile")
    body = response.data.decode().lower()

    assert response.status_code == 200
    assert 'name="from"' in body
    assert 'name="to"' in body
