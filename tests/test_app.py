from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
ORIGINAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_for_activity_adds_participant():
    email = "teststudent@mergington.edu"
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "duplicate@mergington.edu"
    client.post("/activities/Chess Club/signup", params={"email": email})

    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert app_module.activities["Chess Club"]["participants"].count(email) == 1


def test_remove_participant_removes_email():
    email = "michael@mergington.edu"
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "missing@mergington.edu"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
