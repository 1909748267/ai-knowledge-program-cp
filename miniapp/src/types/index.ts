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

export interface QuizSession {
  content: string;
  level: LevelType;
  questionCount: number;
  questions: Question[];
}

export interface QuizResult {
  score: number;
  totalScore: number;
  accuracyRate: string;
  correctCount: number;
  wrongCount: number;
  answers: string[];
}
