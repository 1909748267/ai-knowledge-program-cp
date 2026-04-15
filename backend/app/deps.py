from app.services.quiz_service import QuizService


def get_quiz_service() -> QuizService:
    return QuizService()
