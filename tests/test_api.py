def make_event(client, capacity=2):
    resp = client.post(
        "/events",
        json={
            "title": "Workshop",
            "event_date": "2026-10-15",
            "location": "ENG 101",
            "capacity": capacity,
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def rsvp(client, event_id, email="priya@torontomu.ca"):
    return client.post(
        f"/events/{event_id}/rsvps", json={"name": "Priya", "email": email}
    )


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_list_events(client):
    make_event(client)
    events = client.get("/events").json()
    assert len(events) == 1
    assert events[0]["title"] == "Workshop"


def test_zero_capacity_rejected(client):
    resp = client.post(
        "/events",
        json={"title": "X", "event_date": "2026-10-15", "location": "Y", "capacity": 0},
    )
    assert resp.status_code == 422


def test_rsvp_success_and_listed(client):
    event_id = make_event(client)
    assert rsvp(client, event_id).status_code == 201
    listed = client.get(f"/events/{event_id}/rsvps").json()
    assert [r["email"] for r in listed] == ["priya@torontomu.ca"]


def test_duplicate_email_rejected_even_with_different_case(client):
    event_id = make_event(client)
    assert rsvp(client, event_id, "priya@torontomu.ca").status_code == 201
    assert rsvp(client, event_id, "Priya@TorontoMU.ca").status_code == 409


def test_rsvp_unknown_event_returns_404(client):
    assert rsvp(client, 999).status_code == 404


def test_full_event_rejects_new_rsvp(client):
    event_id = make_event(client, capacity=1)
    assert rsvp(client, event_id, "a@torontomu.ca").status_code == 201
    resp = rsvp(client, event_id, "b@torontomu.ca")
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Event is full"


def test_invalid_email_rejected(client):
    event_id = make_event(client)
    assert rsvp(client, event_id, "not-an-email").status_code == 422

def test_root_redirects_to_docs(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers["location"] == "/docs"