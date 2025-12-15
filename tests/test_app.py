from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_root_redirect():
    resp = client.get("/", allow_redirects=False)
    assert resp.status_code in (301, 302, 307, 308)
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # activities should be a dict and contain at least one known activity
    assert isinstance(data, dict)
    assert "Basketball" in data


def test_signup_and_unregister_flow():
    activity = "Basketball"
    email = "testuser@example.com"

    # Ensure email not present initially; if present, remove for a clean test
    resp = client.get(f"/activities")
    participants = resp.json()[activity]["participants"]
    if email in participants:
        client.delete(f"/activities/{activity}/participants?email={email}")

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant is present
    resp = client.get(f"/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    assert email in participants

    # Unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Verify participant removed
    resp = client.get(f"/activities")
    participants = resp.json()[activity]["participants"]
    assert email not in participants
