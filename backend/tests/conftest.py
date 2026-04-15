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


import pytest


@pytest.fixture()
def stub_service() -> StubQuizService:
    return StubQuizService()


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    return TestClient(app)
