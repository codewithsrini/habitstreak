import datetime as dt
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_client
from app.errors import ApiError
from app.models import CheckIn, Client, Habit, utcnow
from app.schemas import HabitCreate, HabitOut, HabitUpdate
from app.services.streaks import compute_streaks

router = APIRouter(prefix="/habits", tags=["habits"])


def _to_out(habit: Habit, dates: set[dt.date], today: dt.date) -> HabitOut:
    streaks = compute_streaks(dates, today)
    return HabitOut(
        id=habit.id,
        name=habit.name,
        color=habit.color,
        current_streak=streaks.current,
        longest_streak=streaks.longest,
        done_today=today in dates,
    )


def _get_owned_habit(db: Session, client: Client, habit_id: int) -> Habit:
    habit = db.get(Habit, habit_id)
    # Same 404 whether it doesn't exist or belongs to someone else: don't leak which IDs exist.
    if habit is None or habit.client_id != client.id:
        raise ApiError(404, "habit_not_found", "Habit not found")
    return habit


@router.get("", response_model=list[HabitOut])
def list_habits(
    today: dt.date,
    client: Client = Depends(get_client),
    db: Session = Depends(get_db),
):
    habits = db.scalars(
        select(Habit)
        .where(Habit.client_id == client.id, Habit.archived_at.is_(None))
        .order_by(Habit.created_at, Habit.id)
    ).all()

    # One query for ALL check-ins (avoids N+1: one query per habit)
    dates_by_habit: dict[int, set[dt.date]] = defaultdict(set)
    if habits:
        rows = db.execute(
            select(CheckIn.habit_id, CheckIn.date).where(
                CheckIn.habit_id.in_([h.id for h in habits])
            )
        )
        for habit_id, date in rows:
            dates_by_habit[habit_id].add(date)

    return [_to_out(h, dates_by_habit[h.id], today) for h in habits]


@router.post("", response_model=HabitOut, status_code=201)
def create_habit(
    body: HabitCreate,
    today: dt.date,
    client: Client = Depends(get_client),
    db: Session = Depends(get_db),
):
    habit = Habit(client_id=client.id, name=body.name, color=body.color)
    db.add(habit)
    db.commit()
    return _to_out(habit, set(), today)


@router.patch("/{habit_id}", response_model=HabitOut)
def update_habit(
    habit_id: int,
    body: HabitUpdate,
    today: dt.date,
    client: Client = Depends(get_client),
    db: Session = Depends(get_db),
):
    habit = _get_owned_habit(db, client, habit_id)
    changes = body.model_dump(exclude_unset=True)  # only fields the caller actually sent

    if changes.get("name") is not None:
        habit.name = changes["name"]
    if "color" in changes:  # explicit null clears the color
        habit.color = changes["color"]
    if changes.get("archived") is not None:
        habit.archived_at = utcnow() if changes["archived"] else None
    db.commit()

    dates = set(db.scalars(select(CheckIn.date).where(CheckIn.habit_id == habit.id)))
    return _to_out(habit, dates, today)