import Taro from "@tarojs/taro";

import { AnalysisApiData, QuizResult, QuizSession, UserProfile } from "@/types";

const SESSION_KEY = "quiz_session";
const RESULT_KEY = "quiz_result";
const ANALYSIS_KEY = "quiz_analysis";
const ACCESS_TOKEN_KEY = "access_token";
const USER_PROFILE_KEY = "user_profile";

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

export function setAccessToken(token: string) {
  Taro.setStorageSync(ACCESS_TOKEN_KEY, token);
}

export function getAccessToken(): string {
  return Taro.getStorageSync(ACCESS_TOKEN_KEY) || "";
}

export function removeAccessToken() {
  Taro.removeStorageSync(ACCESS_TOKEN_KEY);
}

export function setUserProfile(profile: UserProfile) {
  Taro.setStorageSync(USER_PROFILE_KEY, profile);
}

export function getUserProfile(): UserProfile | null {
  return Taro.getStorageSync(USER_PROFILE_KEY) || null;
}

export function removeUserProfile() {
  Taro.removeStorageSync(USER_PROFILE_KEY);
}

export function clearAuth() {
  removeAccessToken();
  removeUserProfile();
}
