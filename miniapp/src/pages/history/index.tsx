import { Button, Text, View } from "@tarojs/components";
import Taro from "@tarojs/taro";

import "../wrongbook/index.scss";

export default function HistoryPage() {
    return (
        <View className="placeholder-page">
            <Text className="icon">🗂️</Text>
            <Text className="title">学习记录占位页</Text>
            <Text className="desc">Phase 1 仅保留入口和占位，历史数据持久化将在下一阶段实现。</Text>
            <Button className="back-home" onClick={() => Taro.reLaunch({ url: "/pages/home/index" })}>
                返回首页
            </Button>
        </View>
    );
}
