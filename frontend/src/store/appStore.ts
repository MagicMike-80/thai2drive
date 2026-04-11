import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Appearance } from 'react-native';
import { api } from '../services/api';
import { ThemeMode, ThemeColors, darkTheme, lightTheme } from '../theme';

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
  language: string;
  setLanguage: (lang: string) => void;
  deviceId: string;
  initDeviceId: () => Promise<void>;
  progress: UserProgress;
  setProgress: (progress: UserProgress) => void;
  bookmarks: string[];
  loadBookmarks: () => Promise<void>;
  addBookmark: (questionId: string) => Promise<void>;
  removeBookmark: (questionId: string) => Promise<void>;
  isBookmarked: (questionId: string) => boolean;
  // Theme
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;
  colors: ThemeColors;
  isDark: boolean;
  // Sound
  soundEnabled: boolean;
  setSoundEnabled: (enabled: boolean) => void;
  // Premium
  isPremium: boolean;
  freeQuestionsUsed: number;
  setPremium: (val: boolean) => void;
  incrementFreeQuestions: () => void;
  canAnswerFree: () => boolean;
  freeRemaining: () => number;
}

const generateDeviceId = () => {
  return 'device_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
};

function resolveTheme(mode: ThemeMode): { colors: ThemeColors; isDark: boolean } {
  if (mode === 'system') {
    const scheme = Appearance.getColorScheme();
    const isDark = scheme !== 'light';
    return { colors: isDark ? darkTheme : lightTheme, isDark };
  }
  const isDark = mode === 'dark';
  return { colors: isDark ? darkTheme : lightTheme, isDark };
}

export const useAppStore = create<AppState>((set, get) => ({
  language: 'no',
  setLanguage: async (lang) => {
    set({ language: lang });
    await AsyncStorage.setItem('language', lang);
  },

  deviceId: '',
  initDeviceId: async () => {
    let deviceId = await AsyncStorage.getItem('deviceId');
    if (!deviceId) {
      deviceId = generateDeviceId();
      await AsyncStorage.setItem('deviceId', deviceId);
    }
    set({ deviceId });

    const savedLang = await AsyncStorage.getItem('language');
    if (savedLang) set({ language: savedLang });

    // Load theme preference
    const savedTheme = await AsyncStorage.getItem('themeMode');
    if (savedTheme) {
      const mode = savedTheme as ThemeMode;
      const { colors, isDark } = resolveTheme(mode);
      set({ themeMode: mode, colors, isDark });
    }

    // Load sound preference
    const savedSound = await AsyncStorage.getItem('soundEnabled');
    if (savedSound !== null) set({ soundEnabled: savedSound === 'true' });

    // Load premium state
    const savedPremium = await AsyncStorage.getItem('isPremium');
    if (savedPremium === 'true') set({ isPremium: true });
    const savedFreeUsed = await AsyncStorage.getItem('freeQuestionsUsed');
    if (savedFreeUsed) set({ freeQuestionsUsed: parseInt(savedFreeUsed, 10) || 0 });

    await get().loadBookmarks();
  },

  progress: {
    id: '', device_id: '', total_questions_answered: 0, correct_answers: 0,
    questions_by_category: {}, last_activity: '', created_at: '',
  },
  setProgress: (progress) => set({ progress }),

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
  isBookmarked: (questionId) => get().bookmarks.includes(questionId),

  // Theme
  themeMode: 'dark',
  ...resolveTheme('dark'),
  setThemeMode: async (mode) => {
    const { colors, isDark } = resolveTheme(mode);
    set({ themeMode: mode, colors, isDark });
    await AsyncStorage.setItem('themeMode', mode);
  },

  // Sound
  soundEnabled: true,
  setSoundEnabled: async (enabled) => {
    set({ soundEnabled: enabled });
    await AsyncStorage.setItem('soundEnabled', enabled.toString());
  },

  // Premium
  isPremium: false,
  freeQuestionsUsed: 0,
  setPremium: async (val) => {
    set({ isPremium: val });
    await AsyncStorage.setItem('isPremium', val.toString());
  },
  incrementFreeQuestions: async () => {
    const next = get().freeQuestionsUsed + 1;
    set({ freeQuestionsUsed: next });
    await AsyncStorage.setItem('freeQuestionsUsed', next.toString());
  },
  canAnswerFree: () => {
    const { isPremium, freeQuestionsUsed } = get();
    return isPremium || freeQuestionsUsed < 5;
  },
  freeRemaining: () => {
    const { isPremium, freeQuestionsUsed } = get();
    if (isPremium) return Infinity;
    return Math.max(0, 5 - freeQuestionsUsed);
  },
}));
