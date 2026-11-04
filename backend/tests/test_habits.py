import datetime as dt
import uuid

from app.models import CheckIn

TODAY = "2026-10-16"
URL = "/api/v1/habits"


def hdr(client_id: uuid.UUID | None = None) -> dict[str, str]:
    return {"X-Client-Id": str(client_id or uuid.uuid4())}


def test_missing_client_header_is_rejected(api):
    assert api.get(URL, params={"today": TODAY}).status_code == 422


def test_invalid_client_id_uses_error_shape(api):
    r = api.get(URL, params={"today": TODAY}, headers={"X-Client-Id": "nope"})
    assert r.status_code == 400
    assert r.json() == {
        "error": {"code": "invalid_client_id", "message": "X-Client-Id must be a valid UUID"}
    }


def test_create_then_list(api):
    h = hdr()
    r = api.post(URL, params={"today": TODAY}, json={"name": "  Read 20 min  "}, headers=h)
    assert r.status_code == 201
    assert r.json()["name"] == "Read 20 min"
    assert r.json()["currentStreak"] == 0
    assert r.json()["doneToday"] is False

    listed = api.get(URL, params={"today": TODAY}, headers=h).json()
    assert [x["name"] for x in listed] == ["Read 20 min"]


def test_blank_name_is_rejected(api):
    r = api.post(URL, params={"today": TODAY}, json={"name": "   "}, headers=hdr())
    assert r.status_code == 422


def test_clients_are_isolated(api):
    alice, bob = hdr(), hdr()
    created = api.post(URL, params={"today": TODAY}, json={"name": "Walk"}, headers=alice).json()

    assert api.get(URL, params={"today": TODAY}, headers=bob).json() == []

    r = api.patch(
        f"{URL}/{created['id']}", params={"today": TODAY}, json={"name": "Hacked"}, headers=bob
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "habit_not_found"


def test_archive_hides_habit(api):
    h = hdr()
    created = api.post(URL, params={"today": TODAY}, json={"name": "Walk"}, headers=h).json()
    api.patch(f"{URL}/{created['id']}", params={"today": TODAY}, json={"archived": True}, headers=h)
    assert api.get(URL, params={"today": TODAY}, headers=h).json() == []


def test_list_includes_streaks(api, db_session):
    h = hdr()
    created = api.post(URL, params={"today": TODAY}, json={"name": "Read"}, headers=h).json()
    db_session.add_all(
        [CheckIn(habit_id=created["id"], date=dt.date(2026, 10, d)) for d in (15, 16)]
    )
    db_session.commit()

    habit = api.get(URL, params={"today": TODAY}, headers=h).json()[0]
    assert habit["currentStreak"] == 2
    assert habit["longestStreak"] == 2
    assert habit["doneToday"] is True