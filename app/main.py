from fastapi import FastAPI

app = FastAPI(title="Club RSVP API")


@app.get("/health")
def health():
    return {"status": "ok"}