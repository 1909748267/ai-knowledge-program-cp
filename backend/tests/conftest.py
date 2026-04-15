from fastapi.testclient import TestClient

from app.main import create_app


class StubQuizService:
    def __init__(self):
        self.questions_payload = {
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
            "tokens_used": 123,
            "estimated_cost": 0.012,
        }
        self.analysis_payload = {
            "score": 80.0,
            "total_score": 100,
            "accuracy_rate": "80.0%",
            "summary": "整体掌握良好。",
            "weak_points": [
                {
                    "knowledge_point": "高级应用",
                    "reason": "题目2回答错误",
                    "suggestion": "复习对应原文段落",
                }
            ],
            "next_steps": ["复习错题", "回看原文", "再次练习"],
            "tokens_used": 88,
            "estimated_cost": 0.009,
        }

    def generate_questions(self, content: str, level: str, question_count: int):
        return self.questions_payload

    def generate_analysis(self, questions, user_answers, content=None):
        return self.analysis_payload


class StubLearningService:
    def create_quiz_session(self, user_id: int, questions):
        return 9001

    def complete_quiz_session(self, **kwargs):
        return None

    def list_history(self, user_id: int, cursor, limit: int):
        return {
            "list": [
                {
                    "id": 101,
                    "status": "completed",
                    "question_count": 5,
                    "score": 80.0,
                    "accuracy_rate": 80.0,
                    "duration_sec": 32,
                    "created_at": "2026-04-15T10:00:00+00:00",
                    "completed_at": "2026-04-15T10:00:32+00:00",
                }
            ],
            "next_cursor": None,
        }

    def get_history_detail(self, user_id: int, session_id: int):
        return {
            "session": {
                "id": session_id,
                "status": "completed",
                "question_count": 1,
                "score": 100.0,
                "accuracy_rate": 100.0,
                "duration_sec": 10,
                "created_at": "2026-04-15T10:00:00+00:00",
                "completed_at": "2026-04-15T10:00:10+00:00",
            },
            "questions": [
                {
                    "id": "q_1",
                    "type": "single_choice",
                    "question": "什么是机器学习？",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "knowledge_point": "基础",
                    "explanation": "解析",
                }
            ],
            "answers": [
                {
                    "question_index": 1,
                    "user_answer": "A",
                    "correct_answer": "A",
                    "knowledge_point": "基础",
                    "is_correct": True,
                    "created_at": "2026-04-15T10:00:05+00:00",
                }
            ],
        }

    def list_wrongbook(self, user_id: int, cursor, limit: int):
        return {
            "list": [
                {
                    "id": 201,
                    "session_id": 101,
                    "question_index": 2,
                    "question_snapshot": {
                        "id": "q_2",
                        "type": "single_choice",
                        "question": "题干",
                        "options": ["A", "B"],
                        "correct_answer": "B",
                        "knowledge_point": "重点",
                        "explanation": "解析",
                    },
                    "user_answer": "A",
                    "correct_answer": "B",
                    "knowledge_point": "重点",
                    "created_at": "2026-04-15T10:01:00+00:00",
                }
            ],
            "next_cursor": None,
        }


class StubUserService:
    def __init__(self):
        self.user = {
            "id": 1,
            "nickname": "测试用户",
            "avatar_url": "https://example.com/avatar.png",
            "created_at": "2026-04-15T10:00:00+00:00",
            "last_login_at": "2026-04-15T10:00:00+00:00",
            "stats": {"total_sessions": 3, "avg_accuracy_rate": 82.5},
        }

    def login_by_wechat_code(self, code: str):
        if code == "bad-code":
            from app.errors import AppError

            raise AppError(code="WECHAT_LOGIN_FAILED", message="微信登录失败", status_code=400)
        return {
            "access_token": "token-abc",
            "expires_in": 604800,
            "user": self.user,
        }

    def get_user_by_id(self, user_id: int):
        if user_id != 1:
            from app.errors import AppError

            raise AppError(code="USER_NOT_FOUND", message="用户不存在", status_code=404)
        return self.user

    def update_user(self, user_id: int, nickname: str | None, avatar_url: str | None):
        if nickname is not None:
            self.user["nickname"] = nickname
        if avatar_url is not None:
            self.user["avatar_url"] = avatar_url
        return self.user


import pytest


@pytest.fixture()
def stub_service() -> StubQuizService:
    return StubQuizService()


@pytest.fixture()
def stub_learning_service() -> StubLearningService:
    return StubLearningService()


@pytest.fixture()
def stub_user_service() -> StubUserService:
    return StubUserService()


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    return TestClient(app)
