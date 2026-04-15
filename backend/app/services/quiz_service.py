from typing import Any, Dict, List, cast

from app.config import get_settings
from app.errors import AppError
from app.prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    ANALYSIS_USER_PROMPT,
    QUESTION_SYSTEM_PROMPT,
    QUESTION_USER_PROMPT,
)
from app.services.token_monitor import TokenMonitor


class QuizService:
    def __init__(self) -> None:
        self.token_monitor = TokenMonitor()

    def _load_llm(self):
        try:
            from langchain_deepseek import ChatDeepSeek
        except ImportError as exc:
            raise AppError(
                code="DEPENDENCY_MISSING",
                message="缺少 langchain-deepseek 依赖，请先安装 requirements.txt",
                status_code=500,
            ) from exc

        settings = get_settings()
        api_key = settings.deepseek_api_key
        if not api_key:
            raise AppError(
                code="DEEPSEEK_API_KEY_MISSING",
                message="未配置 DEEPSEEK_API_KEY",
                status_code=500,
            )

        return ChatDeepSeek(
            model=settings.deepseek_model,
            api_key=cast(Any, api_key),
            base_url=settings.deepseek_base_url,
            temperature=0.7,
            max_tokens=2000,
            max_retries=2,
        )

    def generate_questions(self, content: str, level: str = "basic", question_count: int = 5) -> Dict:
        if not content.strip():
            raise AppError(code="INVALID_INPUT", message="content 不能为空", status_code=400)
        if len(content) > 5000:
            raise AppError(code="CONTENT_TOO_LONG", message="文本超过 5000 字限制", status_code=400)

        llm = self._load_llm()

        try:
            from langchain_core.output_parsers import JsonOutputParser
            from langchain_core.prompts import ChatPromptTemplate
        except ImportError as exc:
            raise AppError(
                code="DEPENDENCY_MISSING",
                message="缺少 langchain-core 依赖，请先安装 requirements.txt",
                status_code=500,
            ) from exc

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", QUESTION_SYSTEM_PROMPT),
                ("human", QUESTION_USER_PROMPT),
            ]
        )
        parser = JsonOutputParser()
        chain = prompt | llm | parser

        try:
            result = chain.invoke(
                {
                    "content": content,
                    "level": "入门级" if level == "basic" else "进阶级",
                    "question_count": question_count,
                }
            )
        except Exception as exc:
            raise AppError(code="DEEPSEEK_API_ERROR", message=f"出题失败: {exc}", status_code=500) from exc

        questions = result.get("questions", []) if isinstance(result, dict) else []
        self._normalize_questions(questions)
        self._validate_questions(questions)

        usage = self._extract_usage(result)
        self.token_monitor.record_usage("generate_questions", usage["tokens_used"], usage["estimated_cost"])

        return {
            "questions": questions,
            "tokens_used": usage["tokens_used"],
            "estimated_cost": usage["estimated_cost"],
        }

    def generate_analysis(self, questions: List[Dict], user_answers: List[str], content: str | None = None) -> Dict:
        if not questions:
            raise AppError(code="INVALID_INPUT", message="questions 不能为空", status_code=400)

        total_score = 100.0
        points_per_question = total_score / len(questions)
        score = 0.0
        incorrect_indices: List[int] = []

        for idx, (question, answer) in enumerate(zip(questions, user_answers)):
            if answer == question.get("correct_answer"):
                score += points_per_question
            else:
                incorrect_indices.append(idx)

        accuracy_rate = round((score / total_score) * 100, 1)
        incorrect_details = "\n".join(
            [
                f"题目{idx + 1}：{questions[idx].get('question')}｜用户答案：{user_answers[idx]}｜正确答案：{questions[idx].get('correct_answer')}"
                for idx in incorrect_indices
            ]
        )

        llm = self._load_llm()

        try:
            from langchain_core.output_parsers import JsonOutputParser
            from langchain_core.prompts import ChatPromptTemplate
        except ImportError as exc:
            raise AppError(
                code="DEPENDENCY_MISSING",
                message="缺少 langchain-core 依赖，请先安装 requirements.txt",
                status_code=500,
            ) from exc

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", ANALYSIS_SYSTEM_PROMPT),
                ("human", ANALYSIS_USER_PROMPT),
            ]
        )
        parser = JsonOutputParser()
        chain = prompt | llm | parser

        try:
            result = chain.invoke(
                {
                    "total_count": len(questions),
                    "correct_count": len(questions) - len(incorrect_indices),
                    "incorrect_count": len(incorrect_indices),
                    "score": round(score, 1),
                    "accuracy_rate": accuracy_rate,
                    "incorrect_details": incorrect_details or "无",
                    "content": content or "",
                }
            )

            usage = self._extract_usage(result)
            self.token_monitor.record_usage("generate_analysis", usage["tokens_used"], usage["estimated_cost"])

            return {
                "score": round(score, 1),
                "total_score": total_score,
                "accuracy_rate": f"{accuracy_rate}%",
                "summary": result.get("summary", ""),
                "weak_points": result.get("weak_points", []),
                "next_steps": result.get("next_steps", []),
                "tokens_used": usage["tokens_used"],
                "estimated_cost": usage["estimated_cost"],
            }
        except Exception:
            # 分析接口允许降级，保证核心流程可用。
            return {
                "score": round(score, 1),
                "total_score": total_score,
                "accuracy_rate": f"{accuracy_rate}%",
                "summary": f"你的正确率是 {accuracy_rate}%",
                "weak_points": [],
                "next_steps": ["复习错题", "查阅原文", "再练一遍"],
                "tokens_used": 0,
                "estimated_cost": 0.0,
            }

    @staticmethod
    def _normalize_questions(questions: List[Dict]) -> None:
        for question in questions:
            options = question.get("options")
            if not isinstance(options, list) or not options:
                continue

            correct_answer = question.get("correct_answer")
            if correct_answer in options:
                continue

            mapped = QuizService._map_answer(correct_answer, options, question.get("type"))
            if mapped is not None:
                question["correct_answer"] = mapped
                continue

            # Fallback to avoid hard failure when model output is slightly inconsistent.
            question["correct_answer"] = options[0]

    @staticmethod
    def _map_answer(correct_answer: Any, options: List[Any], question_type: Any) -> str | None:
        if not isinstance(correct_answer, str):
            return None

        answer = correct_answer.strip()
        if not answer:
            return None

        letter_map = {"A": 0, "B": 1, "C": 2, "D": 3}
        if answer in letter_map and letter_map[answer] < len(options):
            return str(options[letter_map[answer]])

        if question_type == "judgment":
            true_set = {"正确", "对", "是", "true", "True", "T", "√"}
            false_set = {"错误", "错", "否", "false", "False", "F", "×"}
            if answer in true_set or answer in false_set:
                for option in options:
                    option_text = str(option).strip()
                    if answer in true_set and option_text in true_set:
                        return option_text
                    if answer in false_set and option_text in false_set:
                        return option_text

        for option in options:
            option_text = str(option)
            if answer in option_text:
                return option_text

        return None

    @staticmethod
    def _extract_usage(result: Dict) -> Dict:
        # 当前 DeepSeek + LangChain 响应的 usage 不总是可用，先提供可运行默认值。
        if isinstance(result, dict) and isinstance(result.get("usage"), dict):
            total = int(result["usage"].get("total_tokens", 0))
            return {
                "tokens_used": total,
                "estimated_cost": round(total / 10000 * 1.0, 4),
            }

        return {
            "tokens_used": 0,
            "estimated_cost": 0.0,
        }

    @staticmethod
    def _validate_questions(questions: List[Dict]) -> None:
        if not questions:
            raise AppError(code="PARSING_ERROR", message="模型返回题目为空", status_code=500)

        required_fields = [
            "id",
            "type",
            "question",
            "options",
            "correct_answer",
            "knowledge_point",
            "explanation",
        ]

        for idx, question in enumerate(questions):
            for field in required_fields:
                if field not in question:
                    raise AppError(
                        code="PARSING_ERROR",
                        message=f"题目{idx + 1}缺少字段: {field}",
                        status_code=500,
                    )

            if question.get("type") not in {"single_choice", "judgment"}:
                raise AppError(code="PARSING_ERROR", message=f"题目{idx + 1}类型非法", status_code=500)

            options = question.get("options")
            if not isinstance(options, list) or len(options) < 2:
                raise AppError(code="PARSING_ERROR", message=f"题目{idx + 1}选项非法", status_code=500)

            if question.get("correct_answer") not in options:
                raise AppError(code="PARSING_ERROR", message=f"题目{idx + 1}答案不在选项中", status_code=500)
