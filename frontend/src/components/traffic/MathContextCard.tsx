/**
 * MathContextCard — quiz-safe traffic math integration point
 * -----------------------------------------------------------
 * This is the ONLY component that quiz.tsx is allowed to import
 * from the traffic math subsystem.
 *
 * Isolation contract:
 *   - Accepts exactly: speedKmh, condition, visible, lang, colors
 *   - Returns: nothing (no callbacks, no state refs, no context writes)
 *   - Error boundary inside: any crash is swallowed here, never propagates
 *   - Own data fetching: uses useTrafficMath directly, shares session cache
 *   - Lazy: only fetches when visible = true
 *
 * Quiz performance contract:
 *   - Does NOT fetch during quiz.tsx's loadQ() or handleCheck()
 *   - Only mounts when the user explicitly requests it (visible = true)
 *   - Uses React.memo — quiz list scroll causes zero re-renders here
 *   - No global state reads or writes
 *
 * Loading UX:
 *   - Hidden before first visible=true
 *   - Two shimmer lines while loading (same height as result — no layout shift)
 *   - Silently omitted on error
 */
import React, { Component, memo, type ReactNode } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';

import { useTrafficMath } from '../../hooks/useTrafficMath';
import { SpeedSummary } from './SpeedSummary';
import type { Lang } from '../../constants/trafficMath';

// ─── Error boundary ───────────────────────────────────────────────────────────
// Class component — the only way to catch render errors in React.
// If SpeedSummary or anything inside crashes, we return null silently.

interface BoundaryState { crashed: boolean }

class MathErrorBoundary extends Component<{ children: ReactNode }, BoundaryState> {
  state: BoundaryState = { crashed: false };

  static getDerivedStateFromError(): BoundaryState {
    return { crashed: true };
  }

  componentDidCatch(e: Error): void {
    // Log for debugging, never surface to user
    console.warn('[MathContextCard] render error (suppressed):', e.message);
  }

  render(): ReactNode {
    return this.state.crashed ? null : this.props.children;
  }
}

// ─── Inner component ──────────────────────────────────────────────────────────

interface MathContextCardProps {
  /** Speed extracted from the question. If undefined/0: renders nothing. */
  speedKmh?:  number;
  /** Road condition key. Defaults to 'dry'. */
  condition?: string;
  /** Only fetches + renders when true. Flip to true on user request. */
  visible:    boolean;
  lang:       Lang;
  /** Pass theme colors from the quiz parent. */
  colors: {
    card:          string;
    cardBorder:    string;
    text:          string;
    textSecondary: string;
    textMuted:     string;
    accent:        string;
  };
}

function MathContextCardInner({
  speedKmh, condition = 'dry', visible, lang, colors,
}: MathContextCardProps) {
  const speed = visible && speedKmh && speedKmh > 0 ? speedKmh : null;
  const { result, loading, error } = useTrafficMath(speed, condition);

  // Not requested yet — render nothing (no layout space consumed)
  if (!visible || !speedKmh || speedKmh <= 0) return null;

  // Loading — placeholder block (same min-height as result → no layout shift)
  if (loading && !result) {
    return (
      <View style={[st.placeholder, { borderColor: `${colors.accent}25` }]}>
        <ActivityIndicator size="small" color={colors.accent} />
        <View style={[st.shimLine, { backgroundColor: `${colors.textMuted}20`, width: '70%' }]} />
        <View style={[st.shimLine, { backgroundColor: `${colors.textMuted}12`, width: '50%' }]} />
      </View>
    );
  }

  // Error or no result — silent omission (quiz is unaffected)
  if (error || !result) return null;

  return (
    <SpeedSummary
      result={result}
      lang={lang}
      accentColor={colors.accent}
      textColor={colors.text}
      textSecondary={colors.textSecondary}
      textMuted={colors.textMuted}
      cardBg={colors.card}
      cardBorder={colors.cardBorder}
    />
  );
}

// React.memo: quiz list scroll never re-renders this
const MathContextCardMemo = memo(MathContextCardInner);

// ─── Public export — wrapped in error boundary ─────────────────────────────────

export function MathContextCard(props: MathContextCardProps) {
  return (
    <MathErrorBoundary>
      <MathContextCardMemo {...props} />
    </MathErrorBoundary>
  );
}

const st = StyleSheet.create({
  placeholder: {
    borderRadius: 12,
    borderWidth: 1,
    borderStyle: 'dashed',
    padding: 14,
    gap: 8,
    alignItems: 'center',
    minHeight: 80,
    justifyContent: 'center',
  },
  shimLine: {
    height: 8,
    borderRadius: 4,
  },
});
