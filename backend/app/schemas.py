from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


QuestionType = Literal["single_choice", "judgment"]
LevelType = Literal["basic", "advanced"]


class Question(BaseModel):
    id: str
    type: QuestionType
    question: str
    options: List[str] = Field(min_length=2)
    correct_answer: str
    knowledge_point: str
    explanation: str


class GenerateQuestionsRequest(BaseModel):
    content: str = Field(min_length=1)
    level: LevelType = "basic"
    question_count: int = Field(default=5, ge=1, le=10)


class WeakPoint(BaseModel):
    knowledge_point: str
    reason: str
    suggestion: str


class GenerateAnalysisRequest(BaseModel):
    questions: List[Question]
    user_answers: List[str]
    content: Optional[str] = None
    session_id: Optional[int] = None


class QuestionsData(BaseModel):
    questions: List[Question]
    tokens_used: int
    estimated_cost: float
    timestamp: datetime


class AnalysisData(BaseModel):
    score: float
    total_score: float
    accuracy_rate: str
    summary: str
    weak_points: List[WeakPoint]
    next_steps: List[str]
    tokens_used: int
    estimated_cost: float


class SuccessResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    deepseek_config: str
    version: str


class WechatLoginRequest(BaseModel):
    code: str = Field(min_length=1)


class UserStats(BaseModel):
    total_sessions: int = 0
    avg_accuracy_rate: float = 0.0


class UserProfile(BaseModel):
    id: int
    nickname: str
    avatar_url: str
    created_at: Optional[str] = None
    last_login_at: Optional[str] = None
    stats: UserStats = Field(default_factory=UserStats)


class UpdateUserRequest(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class CursorQuery(BaseModel):
    cursor: Optional[int] = None
    limit: int = Field(default=10, ge=1, le=20)
