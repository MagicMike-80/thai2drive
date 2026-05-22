/**
 * AI Learning API service for Thai2Drive.
 * All calls go to /api/ai/* endpoints on the backend.
 */

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';
const AI_BASE = `${BACKEND_URL}/api/ai`;

// ─── Types ────────────────────────────────────────────────────────────────────

export interface AIAttemptRequest {
  device_id: string;
  question_id: string;
  is_correct: boolean;
  time_taken_ms: number;
  category: string;
  mode: string;
  difficulty?: string;
}

export interface CategoryStat {
  category: string;
  total: number;
  correct: number;
  accuracy: number;   // 0-100
  avg_time: number;   // ms
}

export interface AIDashboard {
  exam_readiness: number;        // 0-100
  total_attempts: number;
  recent_accuracy: number;       // 0-100
  trend: 'improving' | 'stable' | 'declining';
  weakest_category: string | null;
  strongest_category: string | null;
  category_stats: CategoryStat[];
  srs_due_count: number;
  coaching_messages: string[];
  all_categories: string[];
}

export interface AIExplanation {
  why_correct: string;
  why_wrong: Record<string, string>;   // { A: "...", B: "...", C: "..." }
  important_rule: string;
  real_traffic_situation: string;
  common_mistake: string;
  exam_tip: string;
  memory_rule: string;
  is_math: boolean;
  formula_explanation: string;
  _fallback?: boolean;
  _error?: string;
}

export interface AIExplanationResponse {
  question_id: string;
  lang: string;
  explanation: AIExplanation;
  is_fallback: boolean;
}

export interface SmartPracticeResponse {
  questions: any[];       // normalized Question objects
  srs_due_count: number;
  total_in_queue: number;
}

export interface CoachingResponse {
  messages: string[];
  srs_due_count: number;
  total_attempts: number;
}

// ─── Helper ───────────────────────────────────────────────────────────────────

async function safeFetch<T>(url: string, options?: RequestInit): Promise<T | null> {
  try {
    const r = await fetch(url, options);
    if (!r.ok) return null;
    return r.json();
  } catch {
    return null;
  }
}

// ─── API ──────────────────────────────────────────────────────────────────────

export const aiLearningApi = {
  /**
   * Record a question attempt.
   * Fire-and-forget — never throws. Called after every handleCheck in quiz.
   */
  async recordAttempt(req: AIAttemptRequest): Promise<void> {
    try {
      await fetch(`${AI_BASE}/attempt`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(req),
      });
    } catch {
      // Silently ignore — analytics must never break the quiz UX
    }
  },

  /**
   * Fetch the full AI learning dashboard.
   */
  async getDashboard(
    deviceId: string,
    lang: string = 'no',
    streak: number = 0,
  ): Promise<AIDashboard | null> {
    return safeFetch<AIDashboard>(
      `${AI_BASE}/dashboard/${encodeURIComponent(deviceId)}?lang=${lang}&streak=${streak}`,
    );
  },

  /**
   * Get (or generate) an AI explanation for a question.
   * Returns null on any error — UI shows fallback.
   */
  async getExplanation(
    questionId: string,
    lang: string = 'no',
  ): Promise<AIExplanationResponse | null> {
    return safeFetch<AIExplanationResponse>(
      `${AI_BASE}/explanation/${encodeURIComponent(questionId)}?lang=${lang}`,
    );
  },

  /**
   * Get a smart practice session queue.
   */
  async getSmartPractice(
    deviceId: string,
    count: number = 10,
  ): Promise<SmartPracticeResponse | null> {
    return safeFetch<SmartPracticeResponse>(
      `${AI_BASE}/smart-practice/${encodeURIComponent(deviceId)}?count=${count}`,
    );
  },

  /**
   * Lightweight coaching messages for the home screen banner.
   */
  async getCoaching(
    deviceId: string,
    lang: string = 'no',
    streak: number = 0,
  ): Promise<CoachingResponse | null> {
    return safeFetch<CoachingResponse>(
      `${AI_BASE}/coaching/${encodeURIComponent(deviceId)}?lang=${lang}&streak=${streak}`,
    );
  },
};
