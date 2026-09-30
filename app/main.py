from datetime import date

from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import Event

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