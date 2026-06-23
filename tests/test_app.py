import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
initial_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_for_activity_adds_participant():
    email = "teststudent@mergington.edu"
    response = client.post(f"/activities/{quote('Chess Club')}/signup?email={quote(email)}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    updated = client.get("/activities").json()
    assert email in updated["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    email = "michael@mergington.edu"
    response = client.post(f"/activities/{quote('Chess Club')}/signup?email={quote(email)}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity():
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/{quote('Chess Club')}/participants?email={quote(email)}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"

    updated = client.get("/activities").json()
    assert email not in updated["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    email = "notfound@mergington.edu"
    response = client.delete(f"/activities/{quote('Chess Club')}/participants?email={quote(email)}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
