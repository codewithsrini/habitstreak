import datetime as dt
import uuid

import pytest
from app.db import Base
from app.models import CheckIn, Client, Habit
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


@pytest.fixture
def session():
    engine = create_engine("sqlite://")  # in-memory, fresh per test
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_duplicate_checkin_is_rejected(session):
    client = Client(id=uuid.uuid4())
    habit = Habit(name="Read 20 min", client=client)
    session.add_all([client, habit])
    session.commit()

    day = dt.date(2026, 10, 16)
    session.add(CheckIn(habit_id=habit.id, date=day))
    session.commit()

    session.add(CheckIn(habit_id=habit.id, date=day))
    with pytest.raises(IntegrityError):
        session.commit()