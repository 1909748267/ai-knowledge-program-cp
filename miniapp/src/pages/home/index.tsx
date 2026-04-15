import { Button, Text, View } from "@tarojs/components";
import Taro, { useDidShow } from "@tarojs/taro";
import { useState } from "react";

import { getMe, logout, updateMe } from "@/services/api";
import { UserProfile } from "@/types";
import { clearAuth, clearQuizRuntime, getAccessToken, getUserProfile, setUserProfile } from "@/utils/storage";

import "./index.scss";

export default function HomePage() {
    const [user, setUser] = useState<UserProfile | null>(getUserProfile());
    const [loading, setLoading] = useState(false);

    useDidShow(() => {
        if (!getAccessToken()) {
            Taro.reLaunch({ url: "/pages/login/index" });
            return;
        }

        setLoading(true);
        getMe()
            .then((data) => {
                setUserProfile(data);
                setUser(data);
            })
            .finally(() => setLoading(false));
    });

    const handleStart = () => {
        clearQuizRuntime();
        Taro.navigateTo({ url: "/pages/input/index" });
    };

    const handleUpdateProfile = async () => {
        try {
            const profile = await Taro.getUserProfile({ desc: "用于完善会员资料" });
            const updated = await updateMe({
                nickname: profile.userInfo.nickName,
                avatar_url: profile.userInfo.avatarUrl,
            });
            setUserProfile(updated);
            setUser(updated);
            Taro.showToast({ title: "资料已更新", icon: "success" });
        } catch (error) {
            Taro.showToast({ title: (error as Error).message || "更新失败", icon: "none" });
        }
    };

    const handleLogout = async () => {
        try {
            await logout();
        } finally {
            clearAuth();
            clearQuizRuntime();
            Taro.reLaunch({ url: "/pages/login/index" });
        }
    };

    return (
        <View className="home-page">
            <View className="hero-card">
                <View className="profile-row">
                    <View
                        className="avatar"
                        style={{
                            backgroundImage: user?.avatar_url ? `url(${user.avatar_url})` : "none",
                        }}
                    >
                        {!user?.avatar_url ? "🙂" : ""}
                    </View>
                    <View className="profile-main">
                        <Text className="nickname">{user?.nickname || "微信用户"}</Text>
                        <Text className="subline">个人中心</Text>
                    </View>
                </View>

                <View className="stats-card">
                    <View className="stat-item">
                        <Text className="stat-value">{user?.stats?.total_sessions ?? 0}</Text>
                        <Text className="stat-label">累计练习</Text>
                    </View>
                    <View className="stat-item">
                        <Text className="stat-value">{(user?.stats?.avg_accuracy_rate ?? 0).toFixed(1)}%</Text>
                        <Text className="stat-label">平均正确率</Text>
                    </View>
                </View>

                <Button className="start-btn" loading={loading} onClick={handleStart}>
                    开始学习 🚀
                </Button>

                <View className="links-row">
                    <Button className="ghost-btn" onClick={() => Taro.navigateTo({ url: "/pages/history/index" })}>
                        学习历史
                    </Button>
                    <Button className="ghost-btn" onClick={() => Taro.navigateTo({ url: "/pages/wrongbook/index" })}>
                        错题本
                    </Button>
                </View>

                <View className="footer-row">
                    <Text className="action-link" onClick={handleUpdateProfile}>
                        完善资料
                    </Text>
                    <Text className="action-link danger" onClick={handleLogout}>
                        退出登录
                    </Text>
                </View>
            </View>
        </View>
    );
}
