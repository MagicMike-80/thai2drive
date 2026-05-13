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
  // ==================== AUTH ====================
  async signup(email: string, password: string): Promise<AuthResponse> {
    return fetchJSON(`${API_BASE}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    return fetchJSON(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
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
    return fetchJSON(`${API_BASE}/quiz-attempts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  async getQuizAttempts(deviceId: string, limit = 20): Promise<QuizAttempt[]> {
    return fetchJSON(`${API_BASE}/quiz-attempts/${deviceId}?limit=${limit}`);
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
};
