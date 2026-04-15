from app.deps import get_user_service


def test_wechat_login_success(client, stub_user_service):
    client.app.dependency_overrides[get_user_service] = lambda: stub_user_service

    response = client.post("/api/auth/wechat/login", json={"code": "good-code"})

    client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"] == "token-abc"
    assert body["data"]["user"]["id"] == 1


def test_wechat_login_failed(client, stub_user_service):
    client.app.dependency_overrides[get_user_service] = lambda: stub_user_service

    response = client.post("/api/auth/wechat/login", json={"code": "bad-code"})

    client.app.dependency_overrides.clear()

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "WECHAT_LOGIN_FAILED"


def test_logout_success(client):
    response = client.post("/api/auth/logout")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["success"] is True
