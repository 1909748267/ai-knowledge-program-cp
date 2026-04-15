import { Button, Text, View } from "@tarojs/components";
import Taro from "@tarojs/taro";

import { clearQuizRuntime } from "@/utils/storage";

import "./index.scss";

export default function HomePage() {
    const handleStart = () => {
        clearQuizRuntime();
        Taro.navigateTo({ url: "/pages/input/index" });
    };

    return (
        <View className="home-page">
            <View className="hero-card">
                <View className="mascot">📚</View>
                <Text className="title">AI闯关学习</Text>
                <Text className="subtitle">把知识变成闯关游戏</Text>
                <Button className="start-btn" onClick={handleStart}>
                    开始学习 🚀
                </Button>
                <View className="divider">或</View>
                <View className="links-row">
                    <Button className="ghost-btn" onClick={() => Taro.navigateTo({ url: "/pages/wrongbook/index" })}>
                        错题本
                    </Button>
                    <Button className="ghost-btn" onClick={() => Taro.navigateTo({ url: "/pages/history/index" })}>
                        学习记录
                    </Button>
                </View>
            </View>
        </View>
    );
}
