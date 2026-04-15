from app.deps import get_current_user, get_learning_service, get_quiz_service


def test_generate_questions_success_with_stub(client, stub_service, stub_learning_service):
    client.app.dependency_overrides[get_quiz_service] = lambda: stub_service
    client.app.dependency_overrides[get_learning_service] = lambda: stub_learning_service
    client.app.dependency_overrides[get_current_user] = lambda: {"id": 1}

    response = client.post(
        "/api/generate-questions",
        json={
            "content": "机器学习是人工智能的一个分支。",
            "level": "basic",
            "question_count": 1,
        },
    )

    client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]["questions"]) == 1
    assert body["data"]["tokens_used"] == 123
    assert body["data"]["session_id"] == 9001


def test_generate_questions_should_validate_content_length(client):
    client.app.dependency_overrides[get_current_user] = lambda: {"id": 1}
    response = client.post(
        "/api/generate-questions",
        json={
            "content": "a" * 5001,
            "level": "basic",
            "question_count": 5,
        },
    )
    client.app.dependency_overrides.clear()

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "CONTENT_TOO_LONG"


def test_generate_questions_should_validate_question_count(client):
    client.app.dependency_overrides[get_current_user] = lambda: {"id": 1}
    response = client.post(
        "/api/generate-questions",
        json={
            "content": "有效内容",
            "level": "basic",
            "question_count": 11,
        },
    )
    client.app.dependency_overrides.clear()

    assert response.status_code == 422


def test_generate_questions_should_require_auth(client):
    response = client.post(
        "/api/generate-questions",
        json={
            "content": "有效内容",
            "level": "basic",
            "question_count": 1,
        },
    )

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"
