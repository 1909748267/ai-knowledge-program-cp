import { Button, Text, View } from "@tarojs/components";
import Taro, { useDidShow } from "@tarojs/taro";
import { useState } from "react";

import { getWrongbook } from "@/services/api";
import { WrongbookItem } from "@/types";

import "./index.scss";

export default function WrongbookPage() {
    const [list, setList] = useState<WrongbookItem[]>([]);
    const [nextCursor, setNextCursor] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);

    const loadWrongbook = async (cursor?: number, append = false) => {
        setLoading(true);
        try {
            const data = await getWrongbook(cursor, 10);
            setList((prev) => (append ? [...prev, ...data.list] : data.list));
            setNextCursor(data.next_cursor);
        } catch (error) {
            Taro.showToast({ title: (error as Error).message || "加载失败", icon: "none" });
        } finally {
            setLoading(false);
        }
    };

    useDidShow(() => {
        loadWrongbook(undefined, false);
    });

    return (
        <View className="wrongbook-page">
            <View className="head-card">
                <Text className="title">📘 错题本</Text>
                <Text className="desc">把错题变成你的提分阶梯</Text>
            </View>

            {list.length === 0 && !loading ? (
                <View className="empty-card">
                    <Text className="empty-text">还没有错题记录，继续保持</Text>
                    <Button className="back-home" onClick={() => Taro.reLaunch({ url: "/pages/home/index" })}>
                        返回首页
                    </Button>
                </View>
            ) : (
                <View className="wrong-list">
                    {list.map((item) => (
                        <View key={item.id} className="wrong-item">
                            <Text className="question-text">{item.question_snapshot?.question || "题目内容缺失"}</Text>
                            <Text className="meta">知识点：{item.knowledge_point || "未标注"}</Text>
                            <Text className="meta">你的答案：{item.user_answer || "未作答"}</Text>
                            <Text className="meta correct">正确答案：{item.correct_answer || "未知"}</Text>
                            <Button
                                className="retry-btn"
                                onClick={() =>
                                    Taro.navigateTo({
                                        url: `/pages/input/index?seed=${encodeURIComponent(item.question_snapshot?.question || item.knowledge_point || "")}`,
                                    })
                                }
                            >
                                再练一次
                            </Button>
                        </View>
                    ))}

                    {nextCursor ? (
                        <Button className="load-more" loading={loading} onClick={() => loadWrongbook(nextCursor, true)}>
                            加载更多
                        </Button>
                    ) : (
                        <Text className="no-more">没有更多错题了</Text>
                    )}
                </View>
            )}
        </View>
    );
}
