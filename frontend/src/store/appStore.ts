import React from 'react';
import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Appearance } from 'react-native';
import { api, AuthUser } from '../services/api';
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
  // Auth
  authToken: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  authLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  restoreSession: () => Promise<void>;

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
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;
  colors: ThemeColors;
  isDark: boolean;
  soundEnabled: boolean;
  setSoundEnabled: (enabled: boolean) => void;
  isPremium: boolean;
  freeQuestionsUsed: number;
  setPremium: (val: boolean) => void;
  incrementFreeQuestions: () => void;
  canAnswerFree: () => boolean;
  freeRemaining: () => number;
  // Streak
  streak: number;
  lastActiveDate: string;
  updateStreak: () => Promise<void>;

  // Last quiz attempt (for review on results screen)
  lastAttempt: {
    questions: any[];
    answers: { questionId: string; selected: string | null; correct: boolean }[];
    mode: string;
    category?: string;
    startedAt: string;
  } | null;
  setLastAttempt: (attempt: AppState['lastAttempt']) => void;
}

const generateDeviceId = () =>
  'device_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);

function resolveTheme(mode: ThemeMode): { colors: ThemeColors; isDark: boolean } {
  if (mode === 'system') {
    const isDark = Appearance.getColorScheme() !== 'light';
    return { colors: isDark ? darkTheme : lightTheme, isDark };
  }
  const isDark = mode === 'dark';
  return { colors: isDark ? darkTheme : lightTheme, isDark };
}

function getDateKey() {
  return new Date().toISOString().split('T')[0]; // YYYY-MM-DD
}

function daysBetween(a: string, b: string) {
  const da = new Date(a + 'T00:00:00Z');
  const db = new Date(b + 'T00:00:00Z');
  return Math.round((db.getTime() - da.getTime()) / 86400000);
}

export const useAppStore = create<AppState>((set, get) => ({
  // ==================== AUTH ====================
  authToken: null,
  user: null,
  isAuthenticated: false,
  authLoading: true,

  login: async (email, password) => {
    const res = await api.login(email, password);
    await AsyncStorage.setItem('authToken', res.token);
    await AsyncStorage.setItem('authUser', JSON.stringify(res.user));
    set({
      authToken: res.token,
      user: res.user,
      isAuthenticated: true,
      isPremium: res.user.is_premium || res.user.is_admin,
    });
    if (res.user.is_premium || res.user.is_admin) {
      await AsyncStorage.setItem('isPremium', 'true');
    }
  },

  signup: async (email, password) => {
    const res = await api.signup(email, password);
    await AsyncStorage.setItem('authToken', res.token);
    await AsyncStorage.setItem('authUser', JSON.stringify(res.user));
    set({
      authToken: res.token,
      user: res.user,
      isAuthenticated: true,
      isPremium: res.user.is_premium || res.user.is_admin,
    });
    if (res.user.is_premium || res.user.is_admin) {
      await AsyncStorage.setItem('isPremium', 'true');
    }
  },

  logout: async () => {
    await AsyncStorage.multiRemove(['authToken', 'authUser']);
    set({ authToken: null, user: null, isAuthenticated: false, isPremium: false });
    await AsyncStorage.setItem('isPremium', 'false');
  },

  restoreSession: async () => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      const userStr = await AsyncStorage.getItem('authUser');
      if (token && userStr) {
        const user: AuthUser = JSON.parse(userStr);
        // Verify token is still valid
        try {
          const freshUser = await api.getMe(token);
          set({
            authToken: token,
            user: freshUser,
            isAuthenticated: true,
            isPremium: freshUser.is_premium || freshUser.is_admin,
            authLoading: false,
          });
        } catch {
          // Token expired
          await AsyncStorage.multiRemove(['authToken', 'authUser']);
          set({ authToken: null, user: null, isAuthenticated: false, authLoading: false });
        }
      } else {
        set({ authLoading: false });
      }
    } catch {
      set({ authLoading: false });
    }
  },

  // ==================== EXISTING STATE ====================
  language: 'no',
  setLanguage: async (lang) => { set({ language: lang }); await AsyncStorage.setItem('language', lang); },

  deviceId: '',
  initDeviceId: async () => {
    let deviceId = await AsyncStorage.getItem('deviceId');
    if (!deviceId) { deviceId = generateDeviceId(); await AsyncStorage.setItem('deviceId', deviceId); }
    set({ deviceId });

    const savedLang = await AsyncStorage.getItem('language');
    if (savedLang) set({ language: savedLang });

    const savedTheme = await AsyncStorage.getItem('themeMode');
    if (savedTheme) { const m = savedTheme as ThemeMode; const { colors, isDark } = resolveTheme(m); set({ themeMode: m, colors, isDark }); }

    const savedSound = await AsyncStorage.getItem('soundEnabled');
    if (savedSound !== null) set({ soundEnabled: savedSound === 'true' });

    const savedPremium = await AsyncStorage.getItem('isPremium');
    if (savedPremium === 'true') set({ isPremium: true });
    const savedFreeUsed = await AsyncStorage.getItem('freeQuestionsUsed');
    if (savedFreeUsed) set({ freeQuestionsUsed: parseInt(savedFreeUsed, 10) || 0 });

    // Load streak
    const savedStreak = await AsyncStorage.getItem('streak');
    const savedLastDate = await AsyncStorage.getItem('lastActiveDate');
    if (savedStreak && savedLastDate) {
      const today = getDateKey();
      const diff = daysBetween(savedLastDate, today);
      if (diff <= 1) {
        set({ streak: parseInt(savedStreak, 10) || 0, lastActiveDate: savedLastDate });
      } else {
        // Streak broken
        set({ streak: 0, lastActiveDate: '' });
        await AsyncStorage.setItem('streak', '0');
      }
    }

    await get().loadBookmarks();

    // Restore auth session
    await get().restoreSession();
  },

  progress: { id: '', device_id: '', total_questions_answered: 0, correct_answers: 0, questions_by_category: {}, last_activity: '', created_at: '' },
  setProgress: (progress) => set({ progress }),

  bookmarks: [],
  loadBookmarks: async () => {
    const { deviceId } = get();
    if (!deviceId) return;
    try { const b = await api.getBookmarks(deviceId); set({ bookmarks: b.map((x) => x.question_id) }); } catch (e) {}
  },
  addBookmark: async (questionId) => {
    const { deviceId, bookmarks } = get();
    if (!deviceId) return;
    try { await api.addBookmark(deviceId, questionId); set({ bookmarks: [...bookmarks, questionId] }); } catch (e) {}
  },
  removeBookmark: async (questionId) => {
    const { deviceId, bookmarks } = get();
    if (!deviceId) return;
    try { await api.removeBookmark(deviceId, questionId); set({ bookmarks: bookmarks.filter((id) => id !== questionId) }); } catch (e) {}
  },
  isBookmarked: (questionId) => get().bookmarks.includes(questionId),

  themeMode: 'dark',
  ...resolveTheme('dark'),
  setThemeMode: async (mode) => { const r = resolveTheme(mode); set({ themeMode: mode, ...r }); await AsyncStorage.setItem('themeMode', mode); },

  soundEnabled: true,
  setSoundEnabled: async (enabled) => { set({ soundEnabled: enabled }); await AsyncStorage.setItem('soundEnabled', enabled.toString()); },

  isPremium: false,
  freeQuestionsUsed: 0,
  setPremium: async (val) => { set({ isPremium: val }); await AsyncStorage.setItem('isPremium', val.toString()); },
  incrementFreeQuestions: async () => { const n = get().freeQuestionsUsed + 1; set({ freeQuestionsUsed: n }); await AsyncStorage.setItem('freeQuestionsUsed', n.toString()); },
  canAnswerFree: () => { const { isPremium, freeQuestionsUsed } = get(); return isPremium || freeQuestionsUsed < 5; },
  freeRemaining: () => { const { isPremium, freeQuestionsUsed } = get(); return isPremium ? Infinity : Math.max(0, 5 - freeQuestionsUsed); },

  // Streak
  streak: 0,
  lastActiveDate: '',
  updateStreak: async () => {
    const today = getDateKey();
    const { lastActiveDate, streak } = get();
    if (lastActiveDate === today) return; // Already updated today

    let newStreak: number;
    if (lastActiveDate && daysBetween(lastActiveDate, today) === 1) {
      newStreak = streak + 1; // Consecutive day
    } else if (lastActiveDate === today) {
      return;
    } else {
      newStreak = 1; // First day or streak broken
    }

    set({ streak: newStreak, lastActiveDate: today });
    await AsyncStorage.setItem('streak', newStreak.toString());
    await AsyncStorage.setItem('lastActiveDate', today);
  },

  // Last quiz attempt (in-memory, for review on results screen)
  lastAttempt: null,
  setLastAttempt: (attempt) => set({ lastAttempt: attempt }),
}));
