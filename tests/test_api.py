from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["tickets_loaded"] == 500


def test_query():
    response = client.post(
        "/query",
        json={"question": "How many open tickets are there?"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["result"] == 111