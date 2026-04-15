import { Button, Text, View } from "@tarojs/components";
import Taro, { useDidShow } from "@tarojs/taro";
import { useState } from "react";

import { getHistory } from "@/services/api";
import { HistoryItem } from "@/types";

import "./index.scss";

export default function HistoryPage() {
    const [list, setList] = useState<HistoryItem[]>([]);
    const [nextCursor, setNextCursor] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);

    const loadHistory = async (cursor?: number, append = false) => {
        setLoading(true);
        try {
            const data = await getHistory(cursor, 10);
            setList((prev) => (append ? [...prev, ...data.list] : data.list));
            setNextCursor(data.next_cursor);
        } catch (error) {
            Taro.showToast({ title: (error as Error).message || "加载失败", icon: "none" });
        } finally {
            setLoading(false);
        }
    };

    useDidShow(() => {
        loadHistory(undefined, false);
    });

    return (
        <View className="history-page">
            <View className="header-card">
                <Text className="title">🗂️ 学习历史</Text>
                <Text className="subtitle">记录每一次闯关表现</Text>
            </View>

            {list.length === 0 && !loading ? (
                <View className="empty-box">
                    <Text className="empty-text">暂无历史记录，去闯一关吧</Text>
                    <Button className="primary-btn" onClick={() => Taro.navigateTo({ url: "/pages/input/index" })}>
                        开始学习
                    </Button>
                </View>
            ) : (
                <View className="list-wrap">
                    {list.map((item) => (
                        <View
                            key={item.id}
                            className="item-card"
                            onClick={() => Taro.navigateTo({ url: `/pages/history-detail/index?sessionId=${item.id}` })}
                        >
                            <View className="item-header">
                                <Text className="item-id">第 {item.id} 次练习</Text>
                                <Text className="item-time">{(item.created_at || "").replace("T", " ").slice(0, 16)}</Text>
                            </View>
                            <View className="item-stats">
                                <Text>题数：{item.question_count}</Text>
                                <Text>得分：{item.score ?? 0}</Text>
                                <Text>正确率：{item.accuracy_rate ?? 0}%</Text>
                            </View>
                        </View>
                    ))}

                    {nextCursor ? (
                        <Button className="load-more" loading={loading} onClick={() => loadHistory(nextCursor, true)}>
                            加载更多
                        </Button>
                    ) : (
                        <Text className="no-more">没有更多记录了</Text>
                    )}
                </View>
            )}
        </View>
    );
}
