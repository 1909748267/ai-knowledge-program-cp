import Taro from "@tarojs/taro";

import { AnalysisApiData, QuizResult, QuizSession } from "@/types";

const SESSION_KEY = "quiz_session";
const RESULT_KEY = "quiz_result";
const ANALYSIS_KEY = "quiz_analysis";

export function setQuizSession(session: QuizSession) {
  Taro.setStorageSync(SESSION_KEY, session);
}

export function getQuizSession(): QuizSession | null {
  return Taro.getStorageSync(SESSION_KEY) || null;
}

export function setQuizResult(result: QuizResult) {
  Taro.setStorageSync(RESULT_KEY, result);
}

export function getQuizResult(): QuizResult | null {
  return Taro.getStorageSync(RESULT_KEY) || null;
}

export function setAnalysisReport(report: AnalysisApiData) {
  Taro.setStorageSync(ANALYSIS_KEY, report);
}

export function getAnalysisReport(): AnalysisApiData | null {
  return Taro.getStorageSync(ANALYSIS_KEY) || null;
}

export function clearQuizRuntime() {
  Taro.removeStorageSync(SESSION_KEY);
  Taro.removeStorageSync(RESULT_KEY);
  Taro.removeStorageSync(ANALYSIS_KEY);
}
