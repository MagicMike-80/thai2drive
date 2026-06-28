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
  bg: '#0a0f1c',              // Deep matte dark blue (design spec)
  card: '#131a2e',            // Secondary surface (design spec)
  cardBorder: 'rgba(0, 217, 255, 0.15)',  // Subtle cyan border
  text: '#e8eaed',            // Light gray text (design spec)
  textSecondary: '#94A3B8',
  textMuted: '#64748B',
  accent: '#ff0080',          // Magenta primary action
  accentBg: 'rgba(255, 0, 128, 0.12)',    // Magenta-tinted background
  neonCyan: '#00d9ff',        // Cyan neon (active states, highlights)
  neonCyanGlow: 'rgba(0, 217, 255, 0.4)', // Cyan glow for box-shadow
  neonMagenta: '#ff0080',     // Magenta neon (interactive elements, CTA)
  neonMagentaGlow: 'rgba(255, 0, 128, 0.4)', // Magenta glow
  neonOrange: '#ff8c00',      // Orange neon (warnings, secondary actions)
  neonOrangeGlow: 'rgba(255, 140, 0, 0.4)', // Orange glow
  correct: '#10B981',
  correctBg: 'rgba(16, 185, 129, 0.07)',
  incorrect: '#EF4444',
  incorrectBg: 'rgba(239, 68, 68, 0.07)',
  progressBg: '#1A2844',
  answerBg: '#1A2844',
  answerBorder: 'rgba(0, 217, 255, 0.25)',  // Cyan border for answer options
  letterBg: '#243561',        // Navy-blue option chips
  letterText: '#F8FAFC',
  divider: 'rgba(0, 217, 255, 0.2)',     // Subtle cyan dividers
  statusBar: 'light',
};

export const lightTheme: ThemeColors = {
  bg: '#F8FAFC',
  card: '#FFFFFF',
  cardBorder: 'rgba(0, 217, 255, 0.2)',     // Subtle cyan border
  text: '#0F172A',
  textSecondary: '#475569',   // Darker for better contrast
  textMuted: '#5E7A99',       // Readable muted
  accent: '#ff0080',          // Magenta primary action
  accentBg: 'rgba(255, 0, 128, 0.09)',      // Magenta-tinted background
  neonCyan: '#00b8cc',        // Cyan (darker for light mode)
  neonCyanGlow: 'rgba(0, 184, 204, 0.3)',   // Cyan glow
  neonMagenta: '#e01e5a',     // Magenta (darker for light mode)
  neonMagentaGlow: 'rgba(224, 30, 90, 0.3)', // Magenta glow
  neonOrange: '#dd6620',      // Orange (darker for light mode)
  neonOrangeGlow: 'rgba(221, 102, 32, 0.3)', // Orange glow
  correct: '#047857',         // Richer green
  correctBg: 'rgba(4, 120, 87, 0.07)',
  incorrect: '#DC2626',
  incorrectBg: 'rgba(220, 38, 38, 0.07)',
  progressBg: '#C8DAF0',      // Clearly visible track
  answerBg: '#FFFFFF',
  answerBorder: 'rgba(0, 184, 204, 0.3)',   // Cyan border
  letterBg: '#DCE8F5',        // Clearly distinct from card
  letterText: '#0F172A',
  divider: 'rgba(0, 184, 204, 0.15)',       // Subtle cyan dividers
  statusBar: 'dark',
};
