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
  letterText: string;
  divider: string;
  statusBar: 'light' | 'dark';
}

export const darkTheme: ThemeColors = {
  bg: '#0F172A',
  card: '#1A2844',            // richer deep-navy card (was #1E293B)
  cardBorder: 'rgba(42, 68, 108, 0.55)',  // navy-tinted border (was rgba(51,65,85,0.4))
  text: '#F8FAFC',
  textSecondary: '#94A3B8',
  textMuted: '#64748B',
  accent: '#F59E0B',
  accentBg: 'rgba(245, 158, 11, 0.12)',
  correct: '#10B981',
  correctBg: 'rgba(16, 185, 129, 0.07)',
  incorrect: '#EF4444',
  incorrectBg: 'rgba(239, 68, 68, 0.07)',
  progressBg: '#1A2844',
  answerBg: '#1A2844',
  answerBorder: 'rgba(42, 68, 108, 0.55)',
  letterBg: '#243561',        // navy-blue option chips (was #334155)
  letterText: '#F8FAFC',
  divider: 'rgba(42, 68, 108, 0.6)',
  statusBar: 'light',
};

export const lightTheme: ThemeColors = {
  bg: '#F8FAFC',
  card: '#FFFFFF',
  cardBorder: 'rgba(180, 210, 238, 0.9)',  // visible blue-grey border (was rgba(226,232,240,0.8))
  text: '#0F172A',
  textSecondary: '#475569',   // darker for better contrast (was #64748B)
  textMuted: '#5E7A99',       // readable muted (was #94A3B8 — too light)
  accent: '#D97706',
  accentBg: 'rgba(217, 119, 6, 0.09)',
  correct: '#047857',         // slightly richer green (was #059669)
  correctBg: 'rgba(4, 120, 87, 0.07)',
  incorrect: '#DC2626',
  incorrectBg: 'rgba(220, 38, 38, 0.07)',
  progressBg: '#C8DAF0',      // clearly visible track (was #E2E8F0)
  answerBg: '#FFFFFF',
  answerBorder: '#C2D5EC',    // visible separator (was #E2E8F0)
  letterBg: '#DCE8F5',        // clearly distinct from white card (was #F1F5F9)
  letterText: '#0F172A',
  divider: '#BDD0E8',         // clearly visible (was #E2E8F0)
  statusBar: 'dark',
};
