import Taro from "@tarojs/taro";

import { AnalysisApiData, ApiSuccess, LevelType, Question, QuestionsApiData } from "@/types";

const API_BASE = process.env.TARO_APP_API_BASE_URL || "http://127.0.0.1:8000";

async function request<T>(url: string, method: "GET" | "POST", data?: unknown): Promise<T> {
  const response = await Taro.request<T>({
    url: `${API_BASE}${url}`,
    method,
    data,
    timeout: 60000,
    header: {
      "content-type": "application/json",
    },
  });

  if (response.statusCode >= 400) {
    const message = (response.data as any)?.error?.message || "请求失败";
    throw new Error(message);
  }

  return response.data;
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
}): Promise<AnalysisApiData> {
  const data = await request<ApiSuccess<AnalysisApiData>>("/api/generate-analysis", "POST", payload);
  return data.data;
}
