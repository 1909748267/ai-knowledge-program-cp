from app.deps import get_current_user, get_learning_service


def test_list_wrongbook_success(client, stub_learning_service):
    client.app.dependency_overrides[get_learning_service] = lambda: stub_learning_service
    client.app.dependency_overrides[get_current_user] = lambda: {"id": 1}

    response = client.get("/api/wrongbook?limit=10")

    client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]["list"]) == 1
    assert body["data"]["list"][0]["question_snapshot"]["id"] == "q_2"


def test_list_wrongbook_should_require_auth(client):
    response = client.get("/api/wrongbook")

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"
