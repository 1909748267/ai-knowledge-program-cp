import Taro from "@tarojs/taro";

import {
  AnalysisApiData,
  ApiSuccess,
  HistoryDetailData,
  HistoryListData,
  LevelType,
  LoginApiData,
  Question,
  QuestionsApiData,
  UserProfile,
  WrongbookListData,
} from "@/types";
import { clearAuth, getAccessToken } from "@/utils/storage";

const API_BASE = process.env.TARO_APP_API_BASE_URL || "http://127.0.0.1:8000";

async function request<T>(
  url: string,
  method: "GET" | "POST" | "PATCH",
  data?: unknown,
  requireAuth = true,
): Promise<T> {
  const token = getAccessToken();

  const response = await Taro.request<T>({
    url: `${API_BASE}${url}`,
    method,
    data,
    timeout: 60000,
    header: {
      "content-type": "application/json",
      ...(requireAuth && token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (response.statusCode >= 400) {
    const message = (response.data as any)?.error?.message || "请求失败";
    if (response.statusCode === 401) {
      clearAuth();
      Taro.reLaunch({ url: "/pages/login/index" });
    }
    throw new Error(message);
  }

  return response.data;
}

export async function wechatLogin(code: string): Promise<LoginApiData> {
  const data = await request<ApiSuccess<LoginApiData>>(
    "/api/auth/wechat/login",
    "POST",
    { code },
    false,
  );
  return data.data;
}

export async function logout(): Promise<{ success: boolean }> {
  const data = await request<ApiSuccess<{ success: boolean }>>("/api/auth/logout", "POST");
  return data.data;
}

export async function getMe(): Promise<UserProfile> {
  const data = await request<ApiSuccess<UserProfile>>("/api/users/me", "GET");
  return data.data;
}

export async function updateMe(payload: {
  nickname?: string;
  avatar_url?: string;
}): Promise<UserProfile> {
  const data = await request<ApiSuccess<{ success: boolean; user: UserProfile }>>(
    "/api/users/me",
    "PATCH",
    payload,
  );
  return data.data.user;
}

export async function generateQuestions(payload: {
  content: string;
  level: LevelType;
  question_count: number;
}): Promise<QuestionsApiData> {
  const data = await request<ApiSuccess<QuestionsApiData>>("/api/generate-questions", "POST", payload);
  return data.data;
}

export async function generateAnalysis(payload: {
  questions: Question[];
  user_answers: string[];
  content?: string;
  session_id?: number;
}): Promise<AnalysisApiData> {
  const data = await request<ApiSuccess<AnalysisApiData>>("/api/generate-analysis", "POST", payload);
  return data.data;
}

export async function getHistory(cursor?: number, limit = 10): Promise<HistoryListData> {
  const query = [`limit=${limit}`];
  if (cursor) {
    query.push(`cursor=${cursor}`);
  }

  const data = await request<ApiSuccess<HistoryListData>>(`/api/history?${query.join("&")}`, "GET");
  return data.data;
}

export async function getHistoryDetail(sessionId: number): Promise<HistoryDetailData> {
  const data = await request<ApiSuccess<HistoryDetailData>>(`/api/history/${sessionId}`, "GET");
  return data.data;
}

export async function getWrongbook(cursor?: number, limit = 10): Promise<WrongbookListData> {
  const query = [`limit=${limit}`];
  if (cursor) {
    query.push(`cursor=${cursor}`);
  }

  const data = await request<ApiSuccess<WrongbookListData>>(`/api/wrongbook?${query.join("&")}`, "GET");
  return data.data;
}
