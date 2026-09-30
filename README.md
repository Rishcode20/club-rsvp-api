# club-rsvp-api
REST API for managing club events and RSVPs
# Club RSVP API

A REST API for managing club events and RSVPs. Organizers create events with a capacity, students sign up, and the API enforces the rules: no duplicate sign-ups and no sign-ups once an event is full.

**Live API docs:** https://club-rsvp-api.onrender.com/docs
_(Hosted on a free tier, so the first request after idle can take up to a minute.)_

## Tech stack
Python 3.14, FastAPI, SQLAlchemy, PostgreSQL (SQLite for local runs and tests), Docker, GitHub Actions, Render

## Endpoints
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/events` | Create an event (title, date, location, capacity) |
| GET | `/events` | List events by date |
| POST | `/events/{id}/rsvps` | RSVP to an event |
| GET | `/events/{id}/rsvps` | List attendees for an event |

Errors: `422` invalid input, `404` unknown event, `409` event full or email already registered.

## Design notes
- The database is chosen by the `DATABASE_URL` environment variable: Postgres in the cloud, a SQLite file locally.
- Duplicate RSVPs are blocked by a database unique constraint on `(event_id, email)`, not just application code. Emails are normalized to lowercase.
- Input is validated with Pydantic before it reaches the database.

## Run locally
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Then open http://127.0.0.1:8000/docs

## Run with Docker
```bash
docker build -t club-rsvp-api .
docker run --rm -p 8000:8000 club-rsvp-api
```

## Tests and CI
```bash
pytest -q
```
Eight tests cover the success path and each error rule. GitHub Actions runs the tests and builds the Docker image on every pull request and push to `main`.