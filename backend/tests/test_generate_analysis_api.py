from app.deps import get_quiz_service


def test_generate_analysis_success_with_stub(client, stub_service):
    client.app.dependency_overrides[get_quiz_service] = lambda: stub_service

    response = client.post(
        "/api/generate-analysis",
        json={
            "questions": [
                {
                    "id": "q_1",
                    "type": "single_choice",
                    "question": "什么是机器学习？",
                    "options": [
                        "一种编程语言",
                        "从数据中学习规律的方法",
                        "数据库技术",
                        "网页开发框架",
                    ],
                    "correct_answer": "从数据中学习规律的方法",
                    "knowledge_point": "机器学习基础概念",
                    "explanation": "机器学习通过数据训练模型。",
                }
            ],
            "user_answers": ["从数据中学习规律的方法"],
            "content": "机器学习是人工智能的一个分支。",
        },
    )

    client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["summary"] == "整体掌握良好。"


def test_generate_analysis_should_validate_answers_length(client):
    response = client.post(
        "/api/generate-analysis",
        json={
            "questions": [
                {
                    "id": "q_1",
                    "type": "single_choice",
                    "question": "什么是机器学习？",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "knowledge_point": "基础",
                    "explanation": "说明",
                }
            ],
            "user_answers": [],
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "INVALID_INPUT"
