import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';

interface UserProgress {
  id: string;
  device_id: string;
  total_questions_answered: number;
  correct_answers: number;
  questions_by_category: Record<string, { answered: number; correct: number }>;
  last_activity: string;
  created_at: string;
}

interface AppState {
  // Language
  language: string;
  setLanguage: (lang: string) => void;

  // Device ID (for anonymous tracking)
  deviceId: string;
  initDeviceId: () => Promise<void>;

  // User Progress
  progress: UserProgress;
  setProgress: (progress: UserProgress) => void;

  // Bookmarks
  bookmarks: string[];
  loadBookmarks: () => Promise<void>;
  addBookmark: (questionId: string) => Promise<void>;
  removeBookmark: (questionId: string) => Promise<void>;
  isBookmarked: (questionId: string) => boolean;
}

const generateDeviceId = () => {
  return 'device_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
};

export const useAppStore = create<AppState>((set, get) => ({
  // Language
  language: 'no',
  setLanguage: async (lang) => {
    set({ language: lang });
    await AsyncStorage.setItem('language', lang);
  },

  // Device ID
  deviceId: '',
  initDeviceId: async () => {
    let deviceId = await AsyncStorage.getItem('deviceId');
    if (!deviceId) {
      deviceId = generateDeviceId();
      await AsyncStorage.setItem('deviceId', deviceId);
    }
    set({ deviceId });

    // Also load saved language
    const savedLang = await AsyncStorage.getItem('language');
    if (savedLang) {
      set({ language: savedLang });
    }

    // Load bookmarks
    await get().loadBookmarks();
  },

  // Progress
  progress: {
    id: '',
    device_id: '',
    total_questions_answered: 0,
    correct_answers: 0,
    questions_by_category: {},
    last_activity: '',
    created_at: '',
  },
  setProgress: (progress) => set({ progress }),

  // Bookmarks
  bookmarks: [],
  loadBookmarks: async () => {
    const { deviceId } = get();
    if (!deviceId) return;

    try {
      const bookmarks = await api.getBookmarks(deviceId);
      set({ bookmarks: bookmarks.map((b) => b.question_id) });
    } catch (error) {
      console.error('Error loading bookmarks:', error);
    }
  },
  addBookmark: async (questionId) => {
    const { deviceId, bookmarks } = get();
    if (!deviceId) return;

    try {
      await api.addBookmark(deviceId, questionId);
      set({ bookmarks: [...bookmarks, questionId] });
    } catch (error) {
      console.error('Error adding bookmark:', error);
    }
  },
  removeBookmark: async (questionId) => {
    const { deviceId, bookmarks } = get();
    if (!deviceId) return;

    try {
      await api.removeBookmark(deviceId, questionId);
      set({ bookmarks: bookmarks.filter((id) => id !== questionId) });
    } catch (error) {
      console.error('Error removing bookmark:', error);
    }
  },
  isBookmarked: (questionId) => {
    return get().bookmarks.includes(questionId);
  },
}));

// Don't auto-initialize - this will be called from _layout.tsx
