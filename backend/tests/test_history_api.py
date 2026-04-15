from app.deps import get_current_user, get_learning_service


def test_list_history_success(client, stub_learning_service):
    client.app.dependency_overrides[get_learning_service] = lambda: stub_learning_service
    client.app.dependency_overrides[get_current_user] = lambda: {"id": 1}

    response = client.get("/api/history?limit=10")

    client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]["list"]) == 1


def test_history_detail_success(client, stub_learning_service):
    client.app.dependency_overrides[get_learning_service] = lambda: stub_learning_service
    client.app.dependency_overrides[get_current_user] = lambda: {"id": 1}

    response = client.get("/api/history/101")

    client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["session"]["id"] == 101
    assert len(body["data"]["questions"]) == 1


def test_list_history_should_require_auth(client):
    response = client.get("/api/history")

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"
