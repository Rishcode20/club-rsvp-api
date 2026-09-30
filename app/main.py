from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import RSVP, Event

# Creates the tables in the database if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Club RSVP API")


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    event_date: date
    location: str = Field(min_length=1, max_length=200)
    capacity: int = Field(gt=0)


class EventOut(EventCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class RSVPCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=200)


class RSVPOut(RSVPCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_id: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/events", response_model=EventOut, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@app.get("/events", response_model=list[EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.scalars(select(Event).order_by(Event.event_date)).all()


@app.post("/events/{event_id}/rsvps", response_model=RSVPOut, status_code=201)
def create_rsvp(event_id: int, payload: RSVPCreate, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    taken = db.scalar(
        select(func.count()).select_from(RSVP).where(RSVP.event_id == event_id)
    )
    if taken >= event.capacity:
        raise HTTPException(status_code=409, detail="Event is full")

    rsvp = RSVP(event_id=event_id, name=payload.name, email=payload.email.lower())
    db.add(rsvp)
    try:
        db.commit()
    except IntegrityError:  # the unique constraint we added in models.py
        db.rollback()
        raise HTTPException(status_code=409, detail="This email has already RSVPed")
    db.refresh(rsvp)
    return rsvp


@app.get("/events/{event_id}/rsvps", response_model=list[RSVPOut])
def list_rsvps(event_id: int, db: Session = Depends(get_db)):
    if db.get(Event, event_id) is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db.scalars(
        select(RSVP).where(RSVP.event_id == event_id).order_by(RSVP.id)
    ).all()