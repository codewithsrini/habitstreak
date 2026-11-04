import datetime as dt
from collections.abc import Iterable
from dataclasses import dataclass

ONE_DAY = dt.timedelta(days=1)

@dataclass(frozen=True)
class Streaks:
    current: int
    longest: int

def compute_streaks(check_in_dates: Iterable[dt.date], today: dt.date) -> Streaks:
    # A set removes duplicates; dropping future dates keeps bad data from inflating streaks.
    days = {d for d in check_in_dates if d <= today }
    return Streaks(current=_current(days, today), longest=_longest(days))

def _current(days: set[dt.date], today: dt.date) -> int:
    # If today isn't done yet, the streak is still alive: count back from yesterday.
    cursor = today if today in days else today - ONE_DAY
    count = 0
    while cursor in days:
        count += 1
        cursor -= ONE_DAY
    return count

def _longest(days: set[dt.date]) -> int:
    longest = run = 0
    previous: dt.date | None = None
    for day in sorted(days):
        run = run + 1 if previous is not None and day - previous == ONE_DAY else 1
        longest = max(longest, run)
        previous = day
    return longest