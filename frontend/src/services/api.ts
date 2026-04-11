const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';
const API_BASE = `${BACKEND_URL}/api`;

export interface Question {
  id: string;
  question_text_no: string;
  question_text_th: string;
  question_text_en: string;
  answer_a_no: string;
  answer_b_no: string;
  answer_c_no: string;
  answer_d_no: string;
  answer_a_th: string;
  answer_b_th: string;
  answer_c_th: string;
  answer_d_th: string;
  answer_a_en: string;
  answer_b_en: string;
  answer_c_en: string;
  answer_d_en: string;
  correct_answer: string;
  explanation_no: string;
  explanation_th: string;
  explanation_en: string;
  category: string;
  difficulty: string;
  image_url?: string;
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

const fetchJSON = async (url: string, options?: RequestInit) => {
  const response = await fetch(url, options);
  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new Error(`API ${response.status}: ${text}`);
  }
  return response.json();
};

export const api = {
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
};
