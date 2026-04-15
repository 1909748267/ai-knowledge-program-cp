import { Button, Text, View } from "@tarojs/components";
import Taro, { useDidShow } from "@tarojs/taro";
import { useState } from "react";

import { wechatLogin } from "@/services/api";
import { getAccessToken, setAccessToken, setUserProfile } from "@/utils/storage";

import "./index.scss";

export default function LoginPage() {
    const [loading, setLoading] = useState(false);

    useDidShow(() => {
        if (getAccessToken()) {
            Taro.reLaunch({ url: "/pages/home/index" });
        }
    });

    const handleWechatLogin = async () => {
        setLoading(true);
        try {
            const loginRes = await Taro.login();
            const code = loginRes.code;
            if (!code) {
                throw new Error("获取登录凭证失败，请重试");
            }

            const data = await wechatLogin(code);
            setAccessToken(data.access_token);
            setUserProfile(data.user);
            Taro.showToast({ title: "登录成功", icon: "success" });
            Taro.reLaunch({ url: "/pages/home/index" });
        } catch (error) {
            Taro.showToast({ title: (error as Error).message || "登录失败", icon: "none" });
        } finally {
            setLoading(false);
        }
    };

    return (
        <View className="login-page">
            <View className="login-card">
                <View className="mascot">🧠</View>
                <Text className="title">欢迎回来</Text>
                <Text className="subtitle">使用微信登录，开启你的闯关学习</Text>

                <Button className="wechat-btn" loading={loading} onClick={handleWechatLogin}>
                    {loading ? "登录中..." : "微信一键登录"}
                </Button>

                <Text className="tip">登录后可保存学习历史与错题本</Text>
            </View>
        </View>
    );
}
