import { Button, Text, View } from "@tarojs/components";
import Taro from "@tarojs/taro";
import { useMemo, useState } from "react";

import { getQuizSession, setQuizResult } from "@/utils/storage";

import "./index.scss";

export default function QuizPage() {
    const session = getQuizSession();
    const questions = session?.questions ?? [];

    const [currentIndex, setCurrentIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState("");
    const [answers, setAnswers] = useState<string[]>([]);
    const [showFeedback, setShowFeedback] = useState(false);
    const [touchStartX, setTouchStartX] = useState<number | null>(null);

    const currentQuestion = questions[currentIndex];

    const isCorrect = useMemo(() => {
        if (!showFeedback || !currentQuestion) {
            return false;
        }
        return selectedAnswer === currentQuestion.correct_answer;
    }, [showFeedback, selectedAnswer, currentQuestion]);

    if (!session || questions.length === 0 || !currentQuestion) {
        return (
            <View className="quiz-empty">
                <Text className="empty-title">暂无题目数据</Text>
                <Button className="back-btn" onClick={() => Taro.reLaunch({ url: "/pages/input/index" })}>
                    返回输入页
                </Button>
            </View>
        );
    }

    const selectOption = (option: string) => {
        if (showFeedback) {
            return;
        }

        setSelectedAnswer(option);
        setShowFeedback(true);
    };

    const completeAndGoResult = (finalAnswers: string[]) => {
        const correctCount = questions.filter((q, idx) => q.correct_answer === finalAnswers[idx]).length;
        const wrongCount = questions.length - correctCount;
        const score = Number(((correctCount / questions.length) * 100).toFixed(1));

        setQuizResult({
            score,
            totalScore: 100,
            accuracyRate: `${score}%`,
            correctCount,
            wrongCount,
            answers: finalAnswers,
        });

        Taro.redirectTo({ url: "/pages/result/index" });
    };

    const goNext = () => {
        if (!showFeedback) {
            Taro.showToast({ title: "请先作答", icon: "none" });
            return;
        }

        const nextAnswers = [...answers];
        nextAnswers[currentIndex] = selectedAnswer;
        setAnswers(nextAnswers);

        if (currentIndex === questions.length - 1) {
            completeAndGoResult(nextAnswers);
            return;
        }

        setCurrentIndex(currentIndex + 1);
        setSelectedAnswer("");
        setShowFeedback(false);
    };

    const progress = ((currentIndex + 1) / questions.length) * 100;

    return (
        <View className="quiz-page">
            <View className="progress-section">
                <View className="progress-header">
                    <Text className="progress-text">闯关进度</Text>
                    <Text className="progress-text">
                        {currentIndex + 1} / {questions.length}
                    </Text>
                </View>
                <View className="progress-bar">
                    <View className="progress-fill" style={{ width: `${progress}%` }} />
                </View>
            </View>

            <View
                className="question-card"
                onTouchStart={(event: any) => setTouchStartX(event.changedTouches[0].pageX)}
                onTouchEnd={(event: any) => {
                    const endX = event.changedTouches[0].pageX;
                    if (showFeedback && touchStartX !== null && touchStartX - endX > 60) {
                        goNext();
                    }
                    setTouchStartX(null);
                }}
            >
                <Text className="question-badge">📖 第{currentIndex + 1}题</Text>
                <Text className="question-text">{currentQuestion.question}</Text>

                <View className="options-list">
                    {currentQuestion.options.map((option, idx) => {
                        const letter = String.fromCharCode(65 + idx);
                        const isSelected = selectedAnswer === option;
                        const isRight = showFeedback && option === currentQuestion.correct_answer;
                        const isWrong = showFeedback && isSelected && option !== currentQuestion.correct_answer;

                        return (
                            <View
                                key={option}
                                className={`option-item ${isSelected ? "selected" : ""} ${isRight ? "correct" : ""} ${isWrong ? "wrong" : ""}`}
                                onClick={() => selectOption(option)}
                            >
                                <Text className="option-letter">{letter}</Text>
                                <Text className="option-label">{option}</Text>
                            </View>
                        );
                    })}
                </View>

                <View className="swipe-hint">← 左滑下一题</View>

                {showFeedback && (
                    <View className="feedback-overlay">
                        <View className="feedback-header">
                            <Text className="feedback-icon">{isCorrect ? "✅" : "❌"}</Text>
                            <Text className={`feedback-title ${isCorrect ? "correct" : "wrong"}`}>
                                {isCorrect ? "太棒了！正确！" : "回答错误，继续加油"}
                            </Text>
                        </View>

                        <View className="explanation-card">
                            <Text className="explanation-header">💡 知识点解析</Text>
                            <Text className="explanation-kp">{currentQuestion.knowledge_point}</Text>
                            <Text className="explanation-text">{currentQuestion.explanation}</Text>
                        </View>

                        <Button className="next-btn" onClick={goNext}>
                            {currentIndex === questions.length - 1 ? "完成闯关" : "下一题 →"}
                        </Button>
                    </View>
                )}
            </View>
        </View>
    );
}
