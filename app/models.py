from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    event_date: Mapped[date] = mapped_column(Date)
    location: Mapped[str] = mapped_column(String(200))
    capacity: Mapped[int] = mapped_column(Integer)

    rsvps: Mapped[list["RSVP"]] = relationship(back_populates="event")


class RSVP(Base):
    __tablename__ = "rsvps"
    __table_args__ = (UniqueConstraint("event_id", "email", name="one_rsvp_per_event"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200))

    event: Mapped["Event"] = relationship(back_populates="rsvps")