import { Button, Text, View } from "@tarojs/components";
import Taro, { useDidShow } from "@tarojs/taro";
import { useState } from "react";

import { generateAnalysis } from "@/services/api";
import { AnalysisApiData } from "@/types";
import { getAnalysisReport, getQuizResult, getQuizSession, setAnalysisReport } from "@/utils/storage";

import "./index.scss";

export default function AnalysisPage() {
    const [loading, setLoading] = useState(true);
    const [report, setReport] = useState<AnalysisApiData | null>(null);

    useDidShow(() => {
        const localReport = getAnalysisReport();
        if (localReport) {
            setReport(localReport);
            setLoading(false);
            return;
        }

        const session = getQuizSession();
        const result = getQuizResult();

        if (!session || !result) {
            setLoading(false);
            return;
        }

        setLoading(true);
        generateAnalysis({
            questions: session.questions,
            user_answers: result.answers,
            content: session.content,
        })
            .then((data) => {
                setReport(data);
                setAnalysisReport(data);
            })
            .catch((error) => {
                Taro.showToast({ title: (error as Error).message || "分析生成失败", icon: "none" });
            })
            .finally(() => {
                setLoading(false);
            });
    });

    if (loading) {
        return (
            <View className="analysis-loading">
                <Text className="loading-text">正在生成学习报告...</Text>
            </View>
        );
    }

    if (!report) {
        return (
            <View className="analysis-loading">
                <Text className="loading-text">暂无分析数据</Text>
                <Button className="home-btn" onClick={() => Taro.reLaunch({ url: "/pages/home/index" })}>
                    返回首页
                </Button>
            </View>
        );
    }

    return (
        <View className="analysis-page">
            <View className="analysis-card">
                <Text className="card-title">📝 整体评价</Text>
                <Text className="summary">{report.summary}</Text>
            </View>

            <View className="analysis-card">
                <Text className="card-title">⚠️ 薄弱知识点</Text>
                {report.weak_points.length === 0 ? (
                    <Text className="summary">当前未识别到明显薄弱点，继续保持。</Text>
                ) : (
                    report.weak_points.map((point) => (
                        <View key={`${point.knowledge_point}-${point.reason}`} className="weak-point">
                            <Text className="weak-title">{point.knowledge_point}</Text>
                            <Text className="weak-reason">{point.reason}</Text>
                            <Text className="weak-suggestion">{point.suggestion}</Text>
                        </View>
                    ))
                )}
            </View>

            <View className="analysis-card">
                <Text className="card-title">📋 下一步建议</Text>
                {report.next_steps.map((step, idx) => (
                    <View key={step} className="step-row">
                        <Text className="step-number">{idx + 1}</Text>
                        <Text className="step-text">{step}</Text>
                    </View>
                ))}
            </View>

            <Button className="home-btn" onClick={() => Taro.reLaunch({ url: "/pages/home/index" })}>
                返回首页 →
            </Button>
        </View>
    );
}
