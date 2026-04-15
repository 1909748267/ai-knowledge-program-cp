export type LevelType = "basic" | "advanced";

export type QuestionType = "single_choice" | "judgment";

export interface Question {
  id: string;
  type: QuestionType;
  question: string;
  options: string[];
  correct_answer: string;
  knowledge_point: string;
  explanation: string;
}

export interface WeakPoint {
  knowledge_point: string;
  reason: string;
  suggestion: string;
}

export interface QuestionsApiData {
  questions: Question[];
  tokens_used: number;
  estimated_cost: number;
  timestamp: string;
  session_id: number;
}

export interface AnalysisApiData {
  score: number;
  total_score: number;
  accuracy_rate: string;
  summary: string;
  weak_points: WeakPoint[];
  next_steps: string[];
  tokens_used: number;
  estimated_cost: number;
}

export interface ApiSuccess<T> {
  success: true;
  data: T;
}

export interface UserStats {
  total_sessions: number;
  avg_accuracy_rate: number;
}

export interface UserProfile {
  id: number;
  nickname: string;
  avatar_url: string;
  created_at?: string | null;
  last_login_at?: string | null;
  stats: UserStats;
}

export interface LoginApiData {
  access_token: string;
  expires_in: number;
  user: UserProfile;
}

export interface HistoryItem {
  id: number;
  status: string;
  question_count: number;
  score: number | null;
  accuracy_rate: number | null;
  duration_sec: number | null;
  created_at: string | null;
  completed_at: string | null;
}

export interface HistoryListData {
  list: HistoryItem[];
  next_cursor: number | null;
}

export interface HistoryAnswer {
  question_index: number;
  user_answer: string;
  correct_answer: string;
  knowledge_point: string;
  is_correct: boolean;
  created_at: string | null;
}

export interface HistoryDetailData {
  session: HistoryItem;
  questions: Question[];
  answers: HistoryAnswer[];
}

export interface WrongbookItem {
  id: number;
  session_id: number | null;
  question_index: number | null;
  question_snapshot: Question;
  user_answer: string;
  correct_answer: string;
  knowledge_point: string;
  created_at: string | null;
}

export interface WrongbookListData {
  list: WrongbookItem[];
  next_cursor: number | null;
}

export interface QuizSession {
  content: string;
  level: LevelType;
  questionCount: number;
  questions: Question[];
  sessionId: number;
}

export interface QuizResult {
  score: number;
  totalScore: number;
  accuracyRate: string;
  correctCount: number;
  wrongCount: number;
  answers: string[];
}
