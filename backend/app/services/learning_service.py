import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import text

from app.db import get_engine
from app.errors import AppError


class LearningService:
    def __init__(self) -> None:
        self._engine = None

    @property
    def engine(self):
        if self._engine is None:
            self._engine = get_engine()
        return self._engine

    def create_quiz_session(self, user_id: int, questions: List[Dict[str, Any]]) -> int:
        slim_questions = [self._question_snapshot(question) for question in questions]

        with self.engine.begin() as conn:
            result = conn.execute(
                text(
                    """
                    INSERT INTO quiz_sessions (user_id, status, question_count, questions_json)
                    VALUES (:user_id, 'in_progress', :question_count, :questions_json)
                    """
                ),
                {
                    "user_id": user_id,
                    "question_count": len(questions),
                    "questions_json": json.dumps(slim_questions, ensure_ascii=False),
                },
            )
            session_id = int(result.lastrowid)

        return session_id

    def complete_quiz_session(
        self,
        *,
        user_id: int,
        session_id: int | None,
        questions: List[Dict[str, Any]],
        user_answers: List[str],
        score: float,
        accuracy_rate: float,
    ) -> None:
        if len(questions) != len(user_answers):
            raise AppError(code="INVALID_INPUT", message="questions 和 user_answers 数量不一致", status_code=400)

        target_session_id = session_id

        with self.engine.begin() as conn:
            if target_session_id is None:
                row = conn.execute(
                    text(
                        """
                        SELECT id
                        FROM quiz_sessions
                        WHERE user_id = :user_id AND status = 'in_progress'
                        ORDER BY id DESC
                        LIMIT 1
                        """
                    ),
                    {"user_id": user_id},
                ).mappings().first()
                if row is not None:
                    target_session_id = int(row["id"])

            if target_session_id is None:
                target_session_id = self.create_quiz_session(user_id, questions)

            session_row = conn.execute(
                text(
                    """
                    SELECT id, created_at
                    FROM quiz_sessions
                    WHERE id = :session_id AND user_id = :user_id
                    LIMIT 1
                    """
                ),
                {"session_id": target_session_id, "user_id": user_id},
            ).mappings().first()
            if session_row is None:
                raise AppError(code="HISTORY_NOT_FOUND", message="学习记录不存在", status_code=404)

            created_at = session_row.get("created_at")
            duration_sec = None
            if isinstance(created_at, datetime):
                now = datetime.now(timezone.utc)
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                duration_sec = max(0, int((now - created_at).total_seconds()))

            conn.execute(
                text(
                    """
                    UPDATE quiz_sessions
                    SET
                        status = 'completed',
                        score = :score,
                        accuracy_rate = :accuracy_rate,
                        duration_sec = :duration_sec,
                        completed_at = NOW()
                    WHERE id = :session_id AND user_id = :user_id
                    """
                ),
                {
                    "score": score,
                    "accuracy_rate": accuracy_rate,
                    "duration_sec": duration_sec,
                    "session_id": target_session_id,
                    "user_id": user_id,
                },
            )

            conn.execute(
                text("DELETE FROM quiz_answers WHERE session_id = :session_id"),
                {"session_id": target_session_id},
            )

            answers_data = []
            wrong_rows = []
            for idx, (question, answer) in enumerate(zip(questions, user_answers), start=1):
                correct_answer = str(question.get("correct_answer", ""))
                knowledge_point = str(question.get("knowledge_point", ""))
                is_correct = int(answer == correct_answer)
                answers_data.append(
                    {
                        "session_id": target_session_id,
                        "question_index": idx,
                        "user_answer": answer,
                        "correct_answer": correct_answer,
                        "knowledge_point": knowledge_point,
                        "is_correct": is_correct,
                    }
                )
                if not is_correct:
                    wrong_rows.append(
                        {
                            "user_id": user_id,
                            "session_id": target_session_id,
                            "question_index": idx,
                            "question_snapshot": json.dumps(
                                self._question_snapshot(question), ensure_ascii=False
                            ),
                            "user_answer": answer,
                            "correct_answer": correct_answer,
                            "knowledge_point": knowledge_point,
                        }
                    )

            for row in answers_data:
                conn.execute(
                    text(
                        """
                        INSERT INTO quiz_answers (
                            session_id,
                            question_index,
                            user_answer,
                            correct_answer,
                            knowledge_point,
                            is_correct
                        )
                        VALUES (
                            :session_id,
                            :question_index,
                            :user_answer,
                            :correct_answer,
                            :knowledge_point,
                            :is_correct
                        )
                        """
                    ),
                    row,
                )

            for row in wrong_rows:
                conn.execute(
                    text(
                        """
                        INSERT INTO wrong_questions (
                            user_id,
                            session_id,
                            question_index,
                            question_snapshot,
                            user_answer,
                            correct_answer,
                            knowledge_point
                        )
                        VALUES (
                            :user_id,
                            :session_id,
                            :question_index,
                            :question_snapshot,
                            :user_answer,
                            :correct_answer,
                            :knowledge_point
                        )
                        """
                    ),
                    row,
                )

    def list_history(self, user_id: int, cursor: int | None, limit: int) -> Dict[str, Any]:
        safe_limit = max(1, min(limit, 20))
        cursor_value = cursor or 0

        with self.engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT
                        id,
                        status,
                        question_count,
                        score,
                        accuracy_rate,
                        duration_sec,
                        created_at,
                        completed_at
                    FROM quiz_sessions
                    WHERE user_id = :user_id
                    AND (:cursor = 0 OR id < :cursor)
                    ORDER BY id DESC
                    LIMIT :limit
                    """
                ),
                {
                    "user_id": user_id,
                    "cursor": cursor_value,
                    "limit": safe_limit,
                },
            ).mappings().all()

        data = [self._serialize_session_row(row) for row in rows]
        next_cursor = data[-1]["id"] if len(data) == safe_limit else None
        return {"list": data, "next_cursor": next_cursor}

    def get_history_detail(self, user_id: int, session_id: int) -> Dict[str, Any]:
        with self.engine.connect() as conn:
            session_row = conn.execute(
                text(
                    """
                    SELECT
                        id,
                        status,
                        question_count,
                        score,
                        accuracy_rate,
                        duration_sec,
                        questions_json,
                        created_at,
                        completed_at
                    FROM quiz_sessions
                    WHERE id = :session_id AND user_id = :user_id
                    LIMIT 1
                    """
                ),
                {"session_id": session_id, "user_id": user_id},
            ).mappings().first()
            if session_row is None:
                raise AppError(code="HISTORY_NOT_FOUND", message="学习记录不存在", status_code=404)

            answer_rows = conn.execute(
                text(
                    """
                    SELECT
                        question_index,
                        user_answer,
                        correct_answer,
                        knowledge_point,
                        is_correct,
                        created_at
                    FROM quiz_answers
                    WHERE session_id = :session_id
                    ORDER BY question_index ASC
                    """
                ),
                {"session_id": session_id},
            ).mappings().all()

        questions = []
        raw_questions = session_row.get("questions_json")
        if isinstance(raw_questions, str) and raw_questions.strip():
            try:
                parsed = json.loads(raw_questions)
                if isinstance(parsed, list):
                    questions = parsed
            except json.JSONDecodeError:
                questions = []

        answers = [
            {
                "question_index": int(row["question_index"]),
                "user_answer": row.get("user_answer") or "",
                "correct_answer": row.get("correct_answer") or "",
                "knowledge_point": row.get("knowledge_point") or "",
                "is_correct": bool(row.get("is_correct")),
                "created_at": self._to_iso(row.get("created_at")),
            }
            for row in answer_rows
        ]

        return {
            "session": self._serialize_session_row(session_row),
            "questions": questions,
            "answers": answers,
        }

    def list_wrongbook(self, user_id: int, cursor: int | None, limit: int) -> Dict[str, Any]:
        safe_limit = max(1, min(limit, 20))
        cursor_value = cursor or 0

        with self.engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT
                        id,
                        session_id,
                        question_index,
                        question_snapshot,
                        user_answer,
                        correct_answer,
                        knowledge_point,
                        created_at
                    FROM wrong_questions
                    WHERE user_id = :user_id
                    AND (:cursor = 0 OR id < :cursor)
                    ORDER BY id DESC
                    LIMIT :limit
                    """
                ),
                {
                    "user_id": user_id,
                    "cursor": cursor_value,
                    "limit": safe_limit,
                },
            ).mappings().all()

        data = []
        for row in rows:
            snapshot = {}
            raw_snapshot = row.get("question_snapshot")
            if isinstance(raw_snapshot, str) and raw_snapshot.strip():
                try:
                    parsed = json.loads(raw_snapshot)
                    if isinstance(parsed, dict):
                        snapshot = parsed
                except json.JSONDecodeError:
                    snapshot = {}

            data.append(
                {
                    "id": int(row["id"]),
                    "session_id": int(row["session_id"]) if row.get("session_id") is not None else None,
                    "question_index": int(row["question_index"]) if row.get("question_index") is not None else None,
                    "question_snapshot": snapshot,
                    "user_answer": row.get("user_answer") or "",
                    "correct_answer": row.get("correct_answer") or "",
                    "knowledge_point": row.get("knowledge_point") or "",
                    "created_at": self._to_iso(row.get("created_at")),
                }
            )

        next_cursor = data[-1]["id"] if len(data) == safe_limit else None
        return {"list": data, "next_cursor": next_cursor}

    @staticmethod
    def _question_snapshot(question: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": question.get("id"),
            "type": question.get("type"),
            "question": question.get("question"),
            "options": question.get("options"),
            "correct_answer": question.get("correct_answer"),
            "knowledge_point": question.get("knowledge_point"),
            "explanation": question.get("explanation"),
        }

    @staticmethod
    def _serialize_session_row(row: Any) -> Dict[str, Any]:
        return {
            "id": int(row["id"]),
            "status": row.get("status") or "in_progress",
            "question_count": int(row.get("question_count") or 0),
            "score": float(row["score"]) if row.get("score") is not None else None,
            "accuracy_rate": float(row["accuracy_rate"]) if row.get("accuracy_rate") is not None else None,
            "duration_sec": int(row["duration_sec"]) if row.get("duration_sec") is not None else None,
            "created_at": LearningService._to_iso(row.get("created_at")),
            "completed_at": LearningService._to_iso(row.get("completed_at")),
        }

    @staticmethod
    def _to_iso(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.isoformat()
        return str(value)
