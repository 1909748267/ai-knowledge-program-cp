import { Button, Text, View } from "@tarojs/components";
import Taro from "@tarojs/taro";

import { getQuizResult } from "@/utils/storage";

import "./index.scss";

export default function ResultPage() {
    const result = getQuizResult();

    if (!result) {
        return (
            <View className="result-empty">
                <Text className="empty-title">暂无结算结果</Text>
                <Button className="primary-btn" onClick={() => Taro.reLaunch({ url: "/pages/input/index" })}>
                    返回输入页
                </Button>
            </View>
        );
    }

    return (
        <View className="result-page">
            <View className="result-header">
                <Text className="trophy">🎉</Text>
                <Text className="title">闯关完成！</Text>
            </View>

            <View className="score-card">
                <Text className="score-number">{result.score}</Text>
                <Text className="score-label">你的得分</Text>

                <View className="stats-row">
                    <View className="stat-item">
                        <Text className="stat-value success">{result.correctCount}</Text>
                        <Text className="stat-label">正确</Text>
                    </View>
                    <View className="stat-item">
                        <Text className="stat-value error">{result.wrongCount}</Text>
                        <Text className="stat-label">错误</Text>
                    </View>
                </View>
            </View>

            <View className="badge-card">
                <Text className="badge-icon">🏅</Text>
                <View>
                    <Text className="badge-title">知识达人</Text>
                    <Text className="badge-desc">正确率超过80%获得</Text>
                </View>
            </View>

            <View className="actions-row">
                <Button className="secondary-btn" onClick={() => Taro.navigateTo({ url: "/pages/analysis/index" })}>
                    查看分析
                </Button>
                <Button className="primary-btn" onClick={() => Taro.reLaunch({ url: "/pages/input/index" })}>
                    再来一遍
                </Button>
            </View>

            <Text className="share-link" onClick={() => Taro.showToast({ title: "分享功能 Phase 2 开放", icon: "none" })}>
                🔗 分享给好友
            </Text>
        </View>
    );
}
