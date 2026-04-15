from app.deps import get_current_user, get_user_service


def test_get_me_success(client, stub_user_service):
    client.app.dependency_overrides[get_user_service] = lambda: stub_user_service
    client.app.dependency_overrides[get_current_user] = lambda: stub_user_service.user

    response = client.get("/api/users/me")

    client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["nickname"] == "测试用户"


def test_update_me_success(client, stub_user_service):
    client.app.dependency_overrides[get_user_service] = lambda: stub_user_service
    client.app.dependency_overrides[get_current_user] = lambda: stub_user_service.user

    response = client.patch(
        "/api/users/me",
        json={"nickname": "新昵称", "avatar_url": "https://example.com/new.png"},
    )

    client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["user"]["nickname"] == "新昵称"


def test_get_me_should_require_auth(client):
    response = client.get("/api/users/me")

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"
