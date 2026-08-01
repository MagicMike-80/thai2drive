/**
 * SpeedSummary — compact read-only stopping distance result
 * ----------------------------------------------------------
 * Used inside MathContextCard for quiz context.
 * Intentionally compact — 3 key numbers only. No step breakdown,
 * no condition selector, no following distance.
 *
 * Design: mobile readability > visual complexity.
 * This is a quick reference, not a lesson. The full Traffic Math
 * screen is the lesson.
 *
 * React.memo: stable if result + lang don't change (quiz scroll safe).
 */
import React, { memo } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import type { StoppingDistanceResult } from '../../services/trafficMath';
import type { Lang } from '../../constants/trafficMath';
import { CAR_LENGTH_M } from '../../constants/trafficMath';

const LABELS: Record<Lang, { reaction: string; braking: string; total: string; cars: string }> = {
  no: { reaction: 'Reaksjon', braking: 'Bremsing', total: 'Stoppeavstand', cars: 'billengder' },
  th: { reaction: 'ปฏิกิริยา', braking: 'เบรก', total: 'ระยะหยุดรวม', cars: 'คัน' },
  en: { reaction: 'Reaction', braking: 'Braking', total: 'Stopping distance', cars: 'cars' },
};

interface SpeedSummaryProps {
  result:      StoppingDistanceResult;
  lang:        Lang;
  accentColor: string;
  textColor:      string;
  textSecondary:  string;
  textMuted:      string;
  cardBg:         string;
  cardBorder:     string;
}

function SpeedSummaryInner({
  result, lang, accentColor,
  textColor, textSecondary, textMuted, cardBg, cardBorder,
}: SpeedSummaryProps) {
  const l = LABELS[lang];
  const r = result.results;
  const carLengths = Math.round(r.stopping_distance_m / CAR_LENGTH_M);
  // Språkrenhet: kun aktivt språk. Mangler teksten, skjules den (Fail-Stop).
  const condNote   = result.condition_info.note[lang] ?? '';
  const condLabel  = result.condition_info.label[lang] ?? '';

  return (
    <View style={[st.wrap, { backgroundColor: cardBg, borderColor: `${accentColor}35` }]}>
      {/* Speed headline */}
      <View style={st.headline}>
        <Ionicons name="speedometer-outline" size={15} color={accentColor} />
        <Text style={[st.speed, { color: accentColor }]}>
          {result.input.speed_kmh} km/h
        </Text>
        {condLabel ? (
          <Text style={[st.condLabel, { color: textMuted }]}>
            · {condLabel}
          </Text>
        ) : null}
      </View>

      {/* Three numbers */}
      <View style={st.row}>
        <NumCell value={r.reaction_distance_m} unit="m" label={l.reaction} color="#F59E0B" textMuted={textMuted} />
        <View style={[st.divider, { backgroundColor: cardBorder }]} />
        <NumCell value={r.braking_distance_m}  unit="m" label={l.braking}  color="#F97316" textMuted={textMuted} />
        <View style={[st.divider, { backgroundColor: cardBorder }]} />
        <NumCell value={r.stopping_distance_m} unit="m" label={l.total}    color={accentColor} textMuted={textMuted} bold />
      </View>

      {/* Car-length context */}
      <Text style={[st.context, { color: textSecondary }]}>
        ≈ {carLengths} {l.cars}{condNote ? ` · ${condNote}` : ''}
      </Text>
    </View>
  );
}

function NumCell({
  value, unit, label, color, textMuted, bold = false,
}: {
  value: number; unit: string; label: string; color: string; textMuted: string; bold?: boolean;
}) {
  return (
    <View style={st.cell}>
      <Text style={[st.num, { color }, bold && { fontSize: 20 }]}>{value}</Text>
      <Text style={[st.unitText, { color: textMuted }]}>{unit}</Text>
      <Text style={[st.cellLabel, { color: textMuted }]}>{label}</Text>
    </View>
  );
}

export const SpeedSummary = memo(SpeedSummaryInner);

const st = StyleSheet.create({
  wrap:      { borderRadius: 12, borderWidth: 1, padding: 12, gap: 10 },
  headline:  { flexDirection: 'row', alignItems: 'center', gap: 6 },
  speed:     { fontSize: 15, fontWeight: '700' },
  condLabel: { fontSize: 12 },
  row:       { flexDirection: 'row', alignItems: 'center' },
  divider:   { width: StyleSheet.hairlineWidth, alignSelf: 'stretch', marginHorizontal: 8 },
  cell:      { flex: 1, alignItems: 'center', gap: 2 },
  num:       { fontSize: 18, fontWeight: '800', letterSpacing: -0.5 },
  unitText:  { fontSize: 10, marginTop: -2 },
  cellLabel: { fontSize: 10, textAlign: 'center' },
  context:   { fontSize: 11, lineHeight: 16 },
});
