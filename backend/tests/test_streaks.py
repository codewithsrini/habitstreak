import datetime as dt

from app.services.streaks import Streaks, compute_streaks

TODAY = dt.date(2026, 10, 16)

def days_ago(*offsets: int) -> list[dt.date]:
    """days_ago(0, 1, 2) -> today, yesterday, the day before."""
    return [TODAY - dt.timedelta(days=n) for n in offsets]

def test_no_checkins():
    assert compute_streaks([], TODAY) == Streaks(current=0, longest=0)

def test_only_today():
    assert compute_streaks(days_ago(0), TODAY) == Streaks(1, 1)

def test_run_including_today():
    assert compute_streaks(days_ago(0, 1, 2), TODAY) == Streaks(3, 3)

def test_today_not_done_yet_keeps_streak_alive():
    # Done yesterday and the 2 days before, but not today (yet)
    assert compute_streaks(days_ago(1, 2, 3), TODAY) == Streaks(3, 3)

def test_missed_yesterday_and_today_breaks_current_streak():
    assert compute_streaks(days_ago(2, 3, 4), TODAY) == Streaks(0, 3)

def test_longest_can_be_in_the_past():
    # Current run of 2, older run of 4 with a gap between
    dates = days_ago(0, 1) + days_ago(5, 6, 7, 8)
    assert compute_streaks(dates, TODAY) == Streaks(2, 4)

def test_gap_splits_streaks():
    dates = days_ago(0, 2)  # yesterday missing
    assert compute_streaks(dates, TODAY) == Streaks(1, 1)


def test_unsorted_and_duplicate_input():
    dates = days_ago(2, 0, 1, 1, 0)
    assert compute_streaks(dates, TODAY) == Streaks(3, 3)


def test_future_dates_are_ignored():
    future = [TODAY + dt.timedelta(days=1), TODAY + dt.timedelta(days=2)]
    assert compute_streaks(future + days_ago(0), TODAY) == Streaks(1, 1)
