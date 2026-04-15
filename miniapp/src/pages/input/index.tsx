import { Button, Text, Textarea, View } from "@tarojs/components";
import Taro, { useLoad } from "@tarojs/taro";
import { useMemo, useState } from "react";

import { generateQuestions } from "@/services/api";
import { LevelType } from "@/types";
import { clearQuizRuntime, setQuizSession } from "@/utils/storage";

import "./index.scss";

const MAX_CONTENT_LEN = 5000;

export default function InputPage() {
    const [content, setContent] = useState("");
    const [level, setLevel] = useState<LevelType>("basic");
    const [questionCount, setQuestionCount] = useState(5);
    const [loading, setLoading] = useState(false);

    useLoad((params) => {
        if (params.seed) {
            setContent(decodeURIComponent(params.seed));
            Taro.showToast({ title: "已带入错题内容", icon: "none" });
        }
    });

    const canSubmit = useMemo(() => content.trim().length > 0 && !loading, [content, loading]);

    const handleGenerate = async () => {
        if (!content.trim()) {
            Taro.showToast({ title: "请先输入学习内容", icon: "none" });
            return;
        }

        setLoading(true);
        Taro.showLoading({ title: "正在生成题目..." });

        try {
            const data = await generateQuestions({
                content: content.trim(),
                level,
                question_count: questionCount,
            });

            clearQuizRuntime();
            setQuizSession({
                content: content.trim(),
                level,
                questionCount,
                questions: data.questions,
                sessionId: data.session_id,
            });

            Taro.navigateTo({ url: "/pages/quiz/index" });
        } catch (error) {
            Taro.showToast({
                title: (error as Error).message || "题目生成失败",
                icon: "none",
                duration: 2200,
            });
        } finally {
            Taro.hideLoading();
            setLoading(false);
        }
    };

    return (
        <View className="input-page">
            <View className="input-card">
                <Textarea
                    className="input-textarea"
                    placeholder="粘贴你想学习的文本内容...\n\n支持文章、笔记、教材等\n最多5000字"
                    maxlength={MAX_CONTENT_LEN}
                    value={content}
                    onInput={(event: any) => setContent(event.detail.value)}
                />
                <Text className="char-count">{content.length} / 5000</Text>

                <View className="upload-options">
                    <View className="upload-btn" onClick={() => Taro.showToast({ title: "Phase 1 暂不开放 URL 解析", icon: "none" })}>
                        <Text className="upload-icon">🔗</Text>
                        <Text className="upload-text">粘贴链接</Text>
                    </View>
                    <View className="upload-btn" onClick={() => Taro.showToast({ title: "Phase 1 暂不开放文件上传", icon: "none" })}>
                        <Text className="upload-icon">📄</Text>
                        <Text className="upload-text">上传文件</Text>
                    </View>
                </View>
            </View>

            <View className="settings-card">
                <View className="setting-row">
                    <Text className="setting-label">题目数量</Text>
                    <View className="setting-options">
                        <View className={`option-btn ${questionCount === 5 ? "active" : ""}`} onClick={() => setQuestionCount(5)}>
                            5题
                        </View>
                        <View className={`option-btn ${questionCount === 10 ? "active" : ""}`} onClick={() => setQuestionCount(10)}>
                            10题
                        </View>
                    </View>
                </View>
                <View className="setting-row">
                    <Text className="setting-label">难度级别</Text>
                    <View className="setting-options">
                        <View className={`option-btn ${level === "basic" ? "active" : ""}`} onClick={() => setLevel("basic")}>
                            入门
                        </View>
                        <View className={`option-btn ${level === "advanced" ? "active" : ""}`} onClick={() => setLevel("advanced")}>
                            进阶
                        </View>
                    </View>
                </View>
            </View>

            <Button className="generate-btn" disabled={!canSubmit} onClick={handleGenerate}>
                {loading ? "生成中..." : "生成闯关 🔥"}
            </Button>
        </View>
    );
}
