from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.deps import get_quiz_service
from app.errors import AppError
from app.schemas import GenerateAnalysisRequest, GenerateQuestionsRequest, SuccessResponse
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/api", tags=["quiz"])


@router.post("/generate-questions", response_model=SuccessResponse)
def generate_questions(
    request: GenerateQuestionsRequest,
    quiz_service: QuizService = Depends(get_quiz_service),
) -> SuccessResponse:
    result = quiz_service.generate_questions(
        content=request.content,
        level=request.level,
        question_count=request.question_count,
    )
    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    return SuccessResponse(data=result)


@router.post("/generate-analysis", response_model=SuccessResponse)
def generate_analysis(
    request: GenerateAnalysisRequest,
    quiz_service: QuizService = Depends(get_quiz_service),
) -> SuccessResponse:
    if len(request.questions) != len(request.user_answers):
        raise AppError(code="INVALID_INPUT", message="questions 和 user_answers 数量不一致", status_code=400)

    result = quiz_service.generate_analysis(
        questions=[q.model_dump() for q in request.questions],
        user_answers=request.user_answers,
        content=request.content,
    )
    return SuccessResponse(data=result)
