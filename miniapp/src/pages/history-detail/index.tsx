import { Button, Text, View } from "@tarojs/components";
import Taro, { useDidShow, useRouter } from "@tarojs/taro";
import { useState } from "react";

import { getHistoryDetail } from "@/services/api";
import { HistoryDetailData } from "@/types";

import "./index.scss";

export default function HistoryDetailPage() {
    const router = useRouter();
    const sessionId = Number(router.params.sessionId || 0);
    const [detail, setDetail] = useState<HistoryDetailData | null>(null);
    const [loading, setLoading] = useState(false);

    useDidShow(() => {
        if (!sessionId) {
            Taro.showToast({ title: "参数错误", icon: "none" });
            return;
        }

        setLoading(true);
        getHistoryDetail(sessionId)
            .then((data) => setDetail(data))
            .catch((error) => Taro.showToast({ title: (error as Error).message || "加载失败", icon: "none" }))
            .finally(() => setLoading(false));
    });

    if (!detail) {
        return (
            <View className="history-detail-page">
                <View className="loading-box">
                    <Text className="loading-text">{loading ? "加载中..." : "暂无详情"}</Text>
                    <Button className="back-btn" onClick={() => Taro.navigateBack()}>
                        返回
                    </Button>
                </View>
            </View>
        );
    }

    return (
        <View className="history-detail-page">
            <View className="summary-card">
                <Text className="title">本次练习摘要</Text>
                <View className="summary-grid">
                    <Text>题数：{detail.session.question_count}</Text>
                    <Text>得分：{detail.session.score ?? 0}</Text>
                    <Text>正确率：{detail.session.accuracy_rate ?? 0}%</Text>
                    <Text>用时：{detail.session.duration_sec ?? 0}s</Text>
                </View>
            </View>

            <View className="replay-list">
                {detail.questions.map((question, index) => {
                    const answer = detail.answers[index];
                    return (
                        <View key={`${question.id}-${index}`} className="question-card">
                            <Text className="question-index">第 {index + 1} 题</Text>
                            <Text className="question-text">{question.question}</Text>
                            <View className="options-list">
                                {question.options.map((option) => (
                                    <Text key={option} className="option-item">
                                        {option}
                                    </Text>
                                ))}
                            </View>
                            <Text className="answer-line">你的答案：{answer?.user_answer || "未作答"}</Text>
                            <Text className="answer-line correct">正确答案：{answer?.correct_answer || question.correct_answer}</Text>
                            <Text className="analysis">解析：{question.explanation}</Text>
                        </View>
                    );
                })}
            </View>
        </View>
    );
}
