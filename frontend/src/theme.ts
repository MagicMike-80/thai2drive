// Theme definitions for Thai2Drive
export type ThemeMode = 'light' | 'dark' | 'system';

export interface ThemeColors {
  bg: string;
  card: string;
  cardBorder: string;
  text: string;
  textSecondary: string;
  textMuted: string;
  accent: string;
  accentBg: string;
  correct: string;
  correctBg: string;
  incorrect: string;
  incorrectBg: string;
  progressBg: string;
  answerBg: string;
  answerBorder: string;
  letterBg: string;
  divider: string;
  statusBar: 'light' | 'dark';
}

export const darkTheme: ThemeColors = {
  bg: '#0F172A',
  card: '#1E293B',
  cardBorder: 'rgba(51, 65, 85, 0.4)',
  text: '#F8FAFC',
  textSecondary: '#94A3B8',
  textMuted: '#64748B',
  accent: '#F59E0B',
  accentBg: 'rgba(245, 158, 11, 0.1)',
  correct: '#10B981',
  correctBg: 'rgba(16, 185, 129, 0.06)',
  incorrect: '#EF4444',
  incorrectBg: 'rgba(239, 68, 68, 0.06)',
  progressBg: '#1E293B',
  answerBg: '#1E293B',
  answerBorder: 'rgba(51, 65, 85, 0.4)',
  letterBg: '#334155',
  divider: 'rgba(51, 65, 85, 0.5)',
  statusBar: 'light',
};

export const lightTheme: ThemeColors = {
  bg: '#F8FAFC',
  card: '#FFFFFF',
  cardBorder: 'rgba(226, 232, 240, 0.8)',
  text: '#0F172A',
  textSecondary: '#64748B',
  textMuted: '#94A3B8',
  accent: '#D97706',
  accentBg: 'rgba(217, 119, 6, 0.08)',
  correct: '#059669',
  correctBg: 'rgba(5, 150, 105, 0.06)',
  incorrect: '#DC2626',
  incorrectBg: 'rgba(220, 38, 38, 0.06)',
  progressBg: '#E2E8F0',
  answerBg: '#FFFFFF',
  answerBorder: '#E2E8F0',
  letterBg: '#F1F5F9',
  divider: '#E2E8F0',
  statusBar: 'dark',
};
