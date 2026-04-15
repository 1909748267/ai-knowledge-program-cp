from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.deps import get_current_user, get_learning_service, get_quiz_service
from app.errors import AppError
from app.schemas import GenerateAnalysisRequest, GenerateQuestionsRequest, SuccessResponse
from app.services.learning_service import LearningService
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/api", tags=["quiz"])


@router.post("/generate-questions", response_model=SuccessResponse)
def generate_questions(
    request: GenerateQuestionsRequest,
    quiz_service: QuizService = Depends(get_quiz_service),
    learning_service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(get_current_user),
) -> SuccessResponse:
    result = quiz_service.generate_questions(
        content=request.content,
        level=request.level,
        question_count=request.question_count,
    )
    session_id = learning_service.create_quiz_session(
        user_id=current_user["id"],
        questions=result["questions"],
    )
    result["session_id"] = session_id
    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    return SuccessResponse(data=result)


@router.post("/generate-analysis", response_model=SuccessResponse)
def generate_analysis(
    request: GenerateAnalysisRequest,
    quiz_service: QuizService = Depends(get_quiz_service),
    learning_service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(get_current_user),
) -> SuccessResponse:
    if len(request.questions) != len(request.user_answers):
        raise AppError(code="INVALID_INPUT", message="questions 和 user_answers 数量不一致", status_code=400)

    result = quiz_service.generate_analysis(
        questions=[q.model_dump() for q in request.questions],
        user_answers=request.user_answers,
        content=request.content,
    )

    try:
        accuracy_float = float(str(result["accuracy_rate"]).replace("%", ""))
    except (TypeError, ValueError):
        accuracy_float = 0.0

    learning_service.complete_quiz_session(
        user_id=current_user["id"],
        session_id=request.session_id,
        questions=[q.model_dump() for q in request.questions],
        user_answers=request.user_answers,
        score=float(result["score"]),
        accuracy_rate=accuracy_float,
    )

    return SuccessResponse(data=result)
