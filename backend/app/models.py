import datetime as dt
import uuid

from sqlalchemy import Date, DateTime, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.UTC)

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    habits: Mapped[list["Habit"]] = relationship(back_populates="client")

class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    color: Mapped[str | None] = mapped_column(String(20), default=None)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    archived_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    client: Mapped["Client"] = relationship(back_populates="habits")
    check_ins: Mapped[list["CheckIn"]] = relationship(
        back_populates="habit", cascade="all, delete-orphan" 
    )

class CheckIn(Base):
    __tablename__ = "check_ins"
    __table_args__ = (UniqueConstraint("habit_id", "date", name="uq_checkin_habit_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"))
    date: Mapped[dt.date] = mapped_column(Date)

    habit: Mapped["Habit"] = relationship(back_populates="check_ins")
