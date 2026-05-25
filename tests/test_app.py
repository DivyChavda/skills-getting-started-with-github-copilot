import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant():
    email = "teststudent@mergington.edu"
    activity_name = quote("Chess Club", safe="")

    signup_response = client.post(f"/activities/{activity_name}/signup?email={quote(email, safe='')}" )
    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {email} for Chess Club"

    activities_response = client.get("/activities")
    assert email in activities_response.json()["Chess Club"]["participants"]


def test_signup_for_activity_fails_if_activity_missing():
    response = client.post("/activities/Nonexistent%20Club/signup?email=foo@bar.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_fails_when_duplicate_email():
    email = "emma@mergington.edu"
    activity_name = quote("Programming Class", safe="")

    first_response = client.post(f"/activities/{activity_name}/signup?email={quote(email, safe='')}" )
    assert first_response.status_code == 400
    assert first_response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_from_activity_removes_participant():
    email = "michael@mergington.edu"
    activity_name = quote("Chess Club", safe="")

    response = client.delete(f"/activities/{activity_name}/unregister?email={quote(email, safe='')}" )
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"

    activities_response = client.get("/activities")
    assert email not in activities_response.json()["Chess Club"]["participants"]


def test_unregister_fails_if_not_registered():
    email = "nobody@mergington.edu"
    activity_name = quote("Chess Club", safe="")

    response = client.delete(f"/activities/{activity_name}/unregister?email={quote(email, safe='')}" )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"
