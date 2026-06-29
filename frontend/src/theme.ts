// Theme definitions for Thai2Drive — matches webapp.py CSS variables
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
  neonCyan: string;
  neonCyanGlow: string;
  neonMagenta: string;
  neonMagentaGlow: string;
  neonOrange: string;
  neonOrangeGlow: string;
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
  bg: '#0B1226',                         // --bg (webapp.py)
  card: '#111827',                        // --bg2 (webapp.py)
  cardBorder: 'rgba(255,255,255,0.09)',   // --border (webapp.py)
  text: '#E2E8F0',                        // --text (webapp.py)
  textSecondary: '#94A3B8',               // --muted (webapp.py)
  textMuted: '#64748B',
  accent: '#FF9933',                      // --orange (webapp.py)
  accentBg: 'rgba(255,153,51,0.18)',      // --orange-glow (webapp.py)
  neonCyan: '#3B82F6',                    // --blue (webapp.py) — kept for compat
  neonCyanGlow: 'rgba(59,130,246,0.2)',
  neonMagenta: '#FF9933',                 // mapped to orange for compat
  neonMagentaGlow: 'rgba(255,153,51,0.18)',
  neonOrange: '#e6891f',                  // --orange-dk (webapp.py)
  neonOrangeGlow: 'rgba(230,137,31,0.2)',
  correct: '#10B981',                     // --green (webapp.py)
  correctBg: 'rgba(16,185,129,0.08)',
  incorrect: '#EF4444',                   // --red (webapp.py)
  incorrectBg: 'rgba(239,68,68,0.08)',
  progressBg: 'rgba(255,255,255,0.08)',
  answerBg: '#111827',
  answerBorder: 'rgba(255,255,255,0.09)',
  letterBg: '#1a2235',
  letterText: '#E2E8F0',
  divider: 'rgba(255,255,255,0.09)',
  statusBar: 'light',
};

export const lightTheme: ThemeColors = {
  bg: '#F1F5F9',                          // --bg light (webapp.py)
  card: '#FFFFFF',                         // --card2 light
  cardBorder: 'rgba(0,0,0,0.08)',          // --border light (webapp.py)
  text: '#0F172A',                         // --text light (webapp.py)
  textSecondary: '#475569',
  textMuted: '#64748B',                    // --muted light (webapp.py)
  accent: '#FF9933',                       // --orange (same in both modes)
  accentBg: 'rgba(255,153,51,0.12)',
  neonCyan: '#3B82F6',
  neonCyanGlow: 'rgba(59,130,246,0.2)',
  neonMagenta: '#e6891f',
  neonMagentaGlow: 'rgba(230,137,31,0.2)',
  neonOrange: '#e6891f',
  neonOrangeGlow: 'rgba(230,137,31,0.2)',
  correct: '#047857',
  correctBg: 'rgba(4,120,87,0.08)',
  incorrect: '#DC2626',
  incorrectBg: 'rgba(220,38,38,0.08)',
  progressBg: '#E2E8F0',
  answerBg: '#FFFFFF',
  answerBorder: 'rgba(0,0,0,0.08)',
  letterBg: '#E2E8F0',
  letterText: '#0F172A',
  divider: 'rgba(0,0,0,0.08)',
  statusBar: 'dark',
};
