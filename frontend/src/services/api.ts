import AsyncStorage from '@react-native-async-storage/async-storage';
const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';
const API_BASE = `${BACKEND_URL}/api`;

// ==================== STATS TYPES ====================
export interface CategoryStat {
  category: string;
  attempts: number;
  total_q: number;
  total_correct: number;
  pct: number;
}
export interface MyStats {
  overall: { total_q: number; total_correct: number; attempts: number; pct: number };
  by_category: CategoryStat[];
}

// ==================== PRICING TYPES ====================
export interface PremiumPricingPlan {
  id: 'monthly' | 'three_months' | 'lifetime' | string;
  label?: Partial<LocalizedText>;
  amount: number;
  amount_minor?: number;
  currency: string;
  display: string;
  period?: Partial<LocalizedText>;
  stripe_price_id?: string;
}

export interface PremiumPricingResponse {
  currency: string;
  source: 'stripe' | 'fallback' | string;
  plans: PremiumPricingPlan[];
}

export interface CheckoutSessionResponse {
  url: string;
  session_id: string;
  livemode: boolean;
}

export interface CheckoutStatusResponse {
  is_premium: boolean;
  activated: boolean;
  payment_status?: string;
  status?: string;
}

// ==================== ACCESS TYPES ====================
export interface AccessStatus {
  tier: 'guest' | 'registered' | 'premium' | string;
  is_authenticated: boolean;
  is_premium: boolean;
  can_answer: boolean;
  limit: number | null;
  used: number;
  remaining: number | null;
  day_key?: string | null;
  reset_at?: string | null;
  features: Record<string, boolean>;
  message?: Partial<LocalizedText>;
  consumed?: boolean;
  event_id?: string;
}

export interface AccessConsumePayload {
  device_id: string;
  question_id?: string;
  mode?: string;
  category?: string;
  event_id?: string;
}

// ==================== SIGNS TYPES ====================
export interface Sign {
  num: string;
  type: string;
  name: { no: string; th: string; en: string };
  desc: { no: string; th: string; en: string };
}
export interface SignGroup {
  meta: { no: string; th: string; en: string; color: string; shape: string };
  signs: Sign[];
}

export interface TrafficSign {
  id: string;
  group: number;
  order?: number;
  name: Partial<LocalizedText>;
  image_url?: string;
  explanation?: Partial<LocalizedText>;
  driverAction?: Partial<LocalizedText>;
  driver_action?: Partial<LocalizedText>;
  whyDangerous?: Partial<LocalizedText>;
  why_dangerous?: Partial<LocalizedText>;
  typicalMistake?: Partial<LocalizedText>;
  typical_mistake?: Partial<LocalizedText>;
  examTip?: Partial<LocalizedText>;
  exam_tip?: Partial<LocalizedText>;
  memoryRule?: Partial<LocalizedText>;
  memory_rule?: Partial<LocalizedText>;
  realScenario?: Partial<LocalizedText>;
  real_scenario?: Partial<LocalizedText>;
}

export interface TrafficSignGroup {
  group: number;
  group_name: Partial<LocalizedText>;
  signs: TrafficSign[];
}

export interface LearningVideo {
  id: string;
  youtube_url: string;
  thumbnail_url?: string;
  duration_seconds?: number;
  language?: string;
  title_no?: string;
  title_th?: string;
  title_en?: string;
  instructor_summary_no?: string;
  instructor_summary_th?: string;
  instructor_summary_en?: string;
}

// ==================== BOK TYPES ====================
export interface BookChapter {
  chapter_num: number;
  title: { no: string; th: string; en: string };
  section_count: number;
}

export interface BookSection {
  id: string;
  chapter_num: number;
  chapter_title: { no: string; th: string; en: string };
  section_num: number;
  section_title: { no: string; th: string; en: string };
  content: { no: string; th: string; en: string };
  image?: string | null;
  pages: number[];
}

// ==================== V2 SCHEMA TYPES ====================

export interface LocalizedText {
  no: string;
  th: string;
  en: string;
  [key: string]: string;
}

export interface QuestionOption {
  id: string; // "A" | "B" | "C" | "D"
  text: LocalizedText;
}

export interface Question {
  id: string;
  question: LocalizedText;
  options: QuestionOption[];
  correctOptionId: string;
  explanation: LocalizedText;
  bildeUrl?: string | null;
  has_real_image?: boolean;
  category: string;
  difficulty: string;
  active: boolean;
  created_at: string;
}

export interface Category {
  name: string;
  count: number;
}

export interface UserProgress {
  id: string;
  device_id: string;
  total_questions_answered: number;
  correct_answers: number;
  questions_by_category: Record<string, { answered: number; correct: number }>;
  last_activity: string;
  created_at: string;
}

export interface QuizAttempt {
  id: string;
  client_attempt_id?: string;
  device_id: string;
  mode: string;
  category?: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
  passed?: boolean;
  questions_answered: any[];
  started_at: string;
  completed_at: string;
}

export interface Bookmark {
  id: string;
  device_id: string;
  question_id: string;
  created_at: string;
}

export interface AuthUser {
  id: string;
  name?: string;
  email: string;
  is_admin: boolean;
  is_premium: boolean;
}

export interface AuthResponse {
  token: string;
  user: AuthUser;
}

const fetchJSON = async (url: string, options?: RequestInit) => {
  const response = await fetch(url, options);
  if (!response.ok) {
    const text = await response.text().catch(() => '');
    let detail = text;
    try {
      const parsed = JSON.parse(text);
      detail = parsed.detail || text;
    } catch {}
    throw new Error(detail || `API ${response.status}`);
  }
  return response.json();
};

const authHeaders = (token: string) => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`,
});

export const api = {
  // ==================== PUBLIC PRICING ====================
  async getPricing(): Promise<PremiumPricingResponse> {
    return fetchJSON(`${API_BASE}/pricing`);
  },

  async createCheckoutSession(
    planId: string,
    token: string,
    opts?: { successUrl?: string; cancelUrl?: string; deviceId?: string },
  ): Promise<CheckoutSessionResponse> {
    return fetchJSON(`${API_BASE}/create-checkout-session`, {
      method: 'POST',
      headers: authHeaders(token),
      body: JSON.stringify({
        plan_id: planId,
        success_url: opts?.successUrl,
        cancel_url: opts?.cancelUrl,
        device_id: opts?.deviceId,
      }),
    });
  },

  async checkCheckoutStatus(sessionId: string, token: string): Promise<CheckoutStatusResponse> {
    return fetchJSON(`${API_BASE}/checkout/status?session_id=${encodeURIComponent(sessionId)}`, {
      headers: authHeaders(token),
    });
  },

  // ==================== ACCESS POLICY ====================
  async getAccessStatus(deviceId: string, token?: string | null): Promise<AccessStatus> {
    const headers = token ? authHeaders(token) : undefined;
    return fetchJSON(`${API_BASE}/access/status?device_id=${encodeURIComponent(deviceId)}`, { headers });
  },

  async consumeAccess(payload: AccessConsumePayload, token?: string | null): Promise<AccessStatus> {
    return fetchJSON(`${API_BASE}/access/consume`, {
      method: 'POST',
      headers: token ? authHeaders(token) : { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  },

  // ==================== AUTH ====================
  async signup(email: string, password: string, deviceId?: string, name?: string): Promise<AuthResponse> {
    return fetchJSON(`${API_BASE}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, device_id: deviceId, name }),
    });
  },

  async login(email: string, password: string, deviceId?: string): Promise<AuthResponse> {
    return fetchJSON(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, device_id: deviceId }),
    });
  },

  async getMe(token: string): Promise<AuthUser> {
    return fetchJSON(`${API_BASE}/auth/me`, {
      headers: authHeaders(token),
    });
  },

  async forgotPassword(email: string): Promise<{ message: string }> {
    return fetchJSON(`${API_BASE}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
  },

  async resetPassword(email: string, code: string, new_password: string): Promise<{ message: string }> {
    return fetchJSON(`${API_BASE}/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code, new_password }),
    });
  },

  async checkAdmin(email: string): Promise<{ is_admin: boolean }> {
    return fetchJSON(`${API_BASE}/admin/check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
  },

  // ==================== QUESTIONS ====================
  async getQuestions(category?: string, difficulty?: string, limit = 50): Promise<Question[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (difficulty) params.append('difficulty', difficulty);
    params.append('limit', limit.toString());
    return fetchJSON(`${API_BASE}/questions?${params}`);
  },

  async getRandomQuestions(count = 10, category?: string): Promise<Question[]> {
    const params = new URLSearchParams();
    params.append('count', count.toString());
    if (category) params.append('category', category);
    return fetchJSON(`${API_BASE}/questions/random?${params}`);
  },

  async getCategories(): Promise<Category[]> {
    return fetchJSON(`${API_BASE}/categories`);
  },

  async getProgress(deviceId: string): Promise<UserProgress> {
    return fetchJSON(`${API_BASE}/progress/${deviceId}`);
  },

  async updateProgress(deviceId: string, answeredCorrect: boolean, category: string): Promise<any> {
    return fetchJSON(
      `${API_BASE}/progress/${deviceId}?answered_correct=${answeredCorrect}&category=${encodeURIComponent(category)}`,
      { method: 'PUT' }
    );
  },

  async saveQuizAttempt(data: any): Promise<QuizAttempt> {
    const localAttempt: QuizAttempt = {
      id: data.id || `local_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`,
      device_id: data.device_id,
      mode: data.mode,
      category: data.category,
      total_questions: data.total_questions,
      correct_answers: data.correct_answers,
      score_percentage: data.score_percentage,
      passed: data.passed,
      questions_answered: data.questions_answered || [],
      started_at: data.started_at || new Date().toISOString(),
      completed_at: data.completed_at || new Date().toISOString(),
    };

    try {
      const existing = await AsyncStorage.getItem('t2d_local_quiz_attempts');
      const attempts = existing ? JSON.parse(existing) : [];
      attempts.unshift(localAttempt);
      await AsyncStorage.setItem('t2d_local_quiz_attempts', JSON.stringify(attempts.slice(0, 50)));
    } catch (e) {
      console.warn('Failed to cache attempt locally:', e);
    }

    try {
      return await fetchJSON(`${API_BASE}/quiz-attempts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    } catch (err) {
      console.warn('Backend saveQuizAttempt failed, returning local cached copy:', err);
      return localAttempt;
    }
  },

  async getQuizAttempts(deviceId: string, limit = 20): Promise<QuizAttempt[]> {
    return fetchJSON(`${API_BASE}/quiz-attempts/${deviceId}?limit=${limit}`);
  },

  async getHistory(token: string, limit = 20): Promise<QuizAttempt[]> {
    return fetchJSON(`${API_BASE}/history?limit=${limit}`, {
      headers: authHeaders(token),
    });
  },

  async addBookmark(deviceId: string, questionId: string): Promise<Bookmark> {
    return fetchJSON(`${API_BASE}/bookmarks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_id: deviceId, question_id: questionId }),
    });
  },

  async removeBookmark(deviceId: string, questionId: string): Promise<void> {
    await fetch(`${API_BASE}/bookmarks/${deviceId}/${questionId}`, { method: 'DELETE' });
  },

  async getBookmarks(deviceId: string): Promise<Bookmark[]> {
    return fetchJSON(`${API_BASE}/bookmarks/${deviceId}`);
  },

  async getBookmarkedQuestions(deviceId: string): Promise<Question[]> {
    return fetchJSON(`${API_BASE}/bookmarked-questions/${deviceId}`);
  },

  async seedDatabase(): Promise<{ message: string; seeded: boolean }> {
    return fetchJSON(`${API_BASE}/seed`, { method: 'POST' });
  },

  // ==================== BOK / CHAPTERS ====================
  async getChapters(): Promise<BookChapter[]> {
    return fetchJSON(`${API_BASE}/chapters`);
  },
  async getChapterSections(chapterNum: number): Promise<BookSection[]> {
    return fetchJSON(`${API_BASE}/chapters/${chapterNum}`);
  },

  // ==================== STATISTIKK ====================
  async getMyStats(deviceId: string): Promise<MyStats> {
    return fetchJSON(`${API_BASE}/stats/me?device_id=${deviceId}`);
  },

  // ==================== SKILT ====================
  async getSigns(): Promise<Record<string, SignGroup>> {
    return fetchJSON(`${API_BASE}/signs`);
  },

  async getTrafficSigns(): Promise<TrafficSignGroup[]> {
    return fetchJSON(`${API_BASE}/traffic-signs`);
  },

  async getVideosForSign(signId: string, groupName?: string, limit = 1): Promise<LearningVideo[]> {
    const params = new URLSearchParams();
    if (groupName) params.append('group', groupName);
    params.append('limit', limit.toString());
    return fetchJSON(`${API_BASE}/videos/for-sign/${encodeURIComponent(signId)}?${params}`);
  },

  async getVideoForSign(signId: string, groupName?: string): Promise<LearningVideo | null> {
    const videos = await this.getVideosForSign(signId, groupName, 1);
    return videos[0] || null;
  },

  async getVideosForTopic(tags: string, limit = 1): Promise<LearningVideo[]> {
    const params = new URLSearchParams();
    params.append('tags', tags);
    params.append('limit', limit.toString());
    return fetchJSON(`${API_BASE}/videos/for-topic?${params}`);
  },
};
