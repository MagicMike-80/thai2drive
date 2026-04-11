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

export const api = {
  // Questions
  async getQuestions(category?: string, difficulty?: string, limit = 50): Promise<Question[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (difficulty) params.append('difficulty', difficulty);
    params.append('limit', limit.toString());

    const response = await fetch(`${API_BASE}/questions?${params}`);
    if (!response.ok) throw new Error('Failed to fetch questions');
    return response.json();
  },

  async getRandomQuestions(count = 10, category?: string): Promise<Question[]> {
    const params = new URLSearchParams();
    params.append('count', count.toString());
    if (category) params.append('category', category);

    const response = await fetch(`${API_BASE}/questions/random?${params}`);
    if (!response.ok) throw new Error('Failed to fetch random questions');
    return response.json();
  },

  async getQuestion(id: string): Promise<Question> {
    const response = await fetch(`${API_BASE}/questions/${id}`);
    if (!response.ok) throw new Error('Failed to fetch question');
    return response.json();
  },

  // Categories
  async getCategories(): Promise<Category[]> {
    const response = await fetch(`${API_BASE}/categories`);
    if (!response.ok) throw new Error('Failed to fetch categories');
    return response.json();
  },

  // User Progress
  async getProgress(deviceId: string): Promise<UserProgress> {
    const response = await fetch(`${API_BASE}/progress/${deviceId}`);
    if (!response.ok) throw new Error('Failed to fetch progress');
    return response.json();
  },

  async updateProgress(deviceId: string, answeredCorrect: boolean, category: string): Promise<any> {
    const response = await fetch(
      `${API_BASE}/progress/${deviceId}?answered_correct=${answeredCorrect}&category=${encodeURIComponent(category)}`,
      { method: 'PUT' }
    );
    if (!response.ok) throw new Error('Failed to update progress');
    return response.json();
  },

  // Quiz Attempts
  async saveQuizAttempt(data: Omit<QuizAttempt, 'id' | 'completed_at'>): Promise<QuizAttempt> {
    const response = await fetch(`${API_BASE}/quiz-attempts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to save quiz attempt');
    return response.json();
  },

  async getQuizAttempts(deviceId: string, limit = 20): Promise<QuizAttempt[]> {
    const response = await fetch(`${API_BASE}/quiz-attempts/${deviceId}?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch quiz attempts');
    return response.json();
  },

  // Bookmarks
  async addBookmark(deviceId: string, questionId: string): Promise<Bookmark> {
    const response = await fetch(`${API_BASE}/bookmarks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_id: deviceId, question_id: questionId }),
    });
    if (!response.ok) throw new Error('Failed to add bookmark');
    return response.json();
  },

  async removeBookmark(deviceId: string, questionId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/bookmarks/${deviceId}/${questionId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to remove bookmark');
  },

  async getBookmarks(deviceId: string): Promise<Bookmark[]> {
    const response = await fetch(`${API_BASE}/bookmarks/${deviceId}`);
    if (!response.ok) throw new Error('Failed to fetch bookmarks');
    return response.json();
  },

  async getBookmarkedQuestions(deviceId: string): Promise<Question[]> {
    const response = await fetch(`${API_BASE}/bookmarked-questions/${deviceId}`);
    if (!response.ok) throw new Error('Failed to fetch bookmarked questions');
    return response.json();
  },

  // Seed Database
  async seedDatabase(): Promise<{ message: string; seeded: boolean }> {
    const response = await fetch(`${API_BASE}/seed`, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to seed database');
    return response.json();
  },
};
