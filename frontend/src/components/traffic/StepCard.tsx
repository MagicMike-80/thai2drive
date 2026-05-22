/**
 * StepCard — one calculation step with formula + expandable note
 * ---------------------------------------------------------------
 * Mobile readability principles:
 *   - No height animation (causes layout reflows on weak devices)
 *   - No width animation
 *   - Opacity toggle for the note is instant (native driver not needed
 *     for a simple boolean show/hide — just conditional render)
 *   - React.memo: re-renders only when step data or lang changes
 *
 * Used by: traffic-math.tsx, SpeedSummary (detail mode)
 * NOT used by: quiz.tsx (use SpeedSummary / MathContextCard instead)
 */
import React, { memo, useState } from 'react';
import { View, Text, Pressable, StyleSheet, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import type { StoppingDistanceResult } from '../../services/trafficMath';
import type { Lang } from '../../constants/trafficMath';
import { STEP_COLORS } from '../../constants/trafficMath';

interface StepCardProps {
  step:    StoppingDistanceResult['steps'][number];
  lang:    Lang;
  /** Background + border colors from theme. */
  cardBg:  string;
  textColor:      string;
  textSecondary:  string;
  textMuted:      string;
  /** Dims the card slightly when a new result is loading (stale state). */
  dimmed?: boolean;
}

function StepCardInner({
  step, lang, cardBg, textColor, textSecondary, textMuted, dimmed = false,
}: StepCardProps) {
  const [open, setOpen] = useState(false);

  const color   = STEP_COLORS[step.order - 1] ?? '#10B981';
  const label   = step.label[lang]   ?? step.label.en;
  const note    = step.note[lang]    ?? step.note.en;

  return (
    <Pressable
      onPress={() => setOpen(v => !v)}
      style={({ pressed }) => [
        st.card,
        {
          backgroundColor: cardBg,
          borderColor: `${color}30`,
          opacity: pressed ? 0.85 : dimmed ? 0.6 : 1,
        },
      ]}
      accessible
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityHint="Tap to expand explanation"
    >
      {/* Left accent bar */}
      <View style={[st.accent, { backgroundColor: color }]} />

      <View style={st.body}>
        {/* ── Top row: order badge · label · formula · result ── */}
        <View style={st.row}>
          <View style={[st.badge, { backgroundColor: `${color}20` }]}>
            <Text style={[st.badgeText, { color }]}>{step.order}</Text>
          </View>

          <Text style={[st.label, { color: textColor }]} numberOfLines={1}>
            {label}
          </Text>

          <Text style={[st.formula, { color: textSecondary }]} numberOfLines={1}>
            {step.formula}
          </Text>

          <View style={st.resultWrap}>
            <Text style={[st.result, { color }]}>{step.result}</Text>
            <Text style={[st.unit, { color: textMuted }]}> {step.unit}</Text>
          </View>
        </View>

        {/* ── Expandable note — no animation, just conditional render ── */}
        {open && (
          <Text style={[st.note, { color: textSecondary }]}>{note}</Text>
        )}
      </View>

      <Ionicons
        name={open ? 'chevron-up' : 'chevron-down'}
        size={13}
        color={textMuted}
        style={st.chevron}
      />
    </Pressable>
  );
}

export const StepCard = memo(StepCardInner);

const st = StyleSheet.create({
  card:       {
    flexDirection: 'row',
    borderRadius: 12,
    borderWidth: 1,
    overflow: 'hidden',
    paddingVertical: 11,
    paddingRight: 10,
    gap: 8,
    alignItems: 'flex-start',
  },
  accent:     { width: 4, alignSelf: 'stretch', borderRadius: 2 },
  body:       { flex: 1, gap: 6 },
  row:        {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    flexWrap: 'wrap',
  },
  badge:      {
    width: 22,
    height: 22,
    borderRadius: 6,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText:  { fontSize: 11, fontWeight: '800' },
  label:      { fontSize: 13, fontWeight: '600', flex: 1, minWidth: 80 },
  formula:    {
    fontSize: 11,
    fontFamily: Platform.select({ ios: 'Menlo', android: 'monospace', default: 'monospace' }),
  },
  resultWrap: { flexDirection: 'row', alignItems: 'baseline', marginLeft: 'auto' },
  result:     { fontSize: 15, fontWeight: '800' },
  unit:       { fontSize: 11 },
  note:       { fontSize: 12, lineHeight: 18 },
  chevron:    { marginTop: 4, flexShrink: 0 },
});
