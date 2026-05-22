/**
 * Traffic Math Screen — Thai2Drive
 * ----------------------------------
 * Screen responsibility: layout + input state only.
 * All calculation logic lives in useTrafficMath.
 * All visual components live in src/components/traffic/.
 * All constants live in src/constants/trafficMath.ts.
 */
import React, { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, TextInput, Pressable, ScrollView,
  ActivityIndicator, Platform, Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

import { useAppStore } from '../src/store/appStore';
import { useTrafficMath, prewarmTrafficMath } from '../src/hooks/useTrafficMath';
import { StepCard, DangerBar, ConditionChips } from '../src/components/traffic';
import {
  CONDITIONS,
  SPEED_PRESETS,
  CONTENT_MAX_W,
  DEFAULT_CONDITION,
  type ConditionKey,
  type Lang,
  getConditionMeta,
} from '../src/constants/trafficMath';

// ─── Translations ─────────────────────────────────────────────────────────────

const TR: Record<string, Record<string, string>> = {
  no: {
    title:       'Trafikk-matte',
    subtitle:    'Stoppeavstand-kalkulator',
    speedLabel:  'Fart (km/t)',
    condLabel:   'Veibane',
    tapHint:     'Trykk på et steg for forklaring',
    totalStop:   'Stoppeavstand',
    carLengths:  'bilers lengde',
    followTitle: 'Følgeavstand',
    followSub:   '2-sekunders regel (minimum)',
    follow2s:    '2 sek',
    follow3s:    '3 sek',
    emptyHint:   'Skriv inn en fart for å starte',
    offline:     'Beregning utilgjengelig — sjekk tilkobling',
  },
  th: {
    title:       'คณิตศาสตร์จราจร',
    subtitle:    'คำนวณระยะหยุดรถ',
    speedLabel:  'ความเร็ว (กม./ชม.)',
    condLabel:   'สภาพถนน',
    tapHint:     'กดที่ขั้นตอนเพื่อดูคำอธิบาย',
    totalStop:   'ระยะหยุดรวม',
    carLengths:  'คันรถ',
    followTitle: 'ระยะห่างจากรถคันหน้า',
    followSub:   'กฎ 2 วินาที (ขั้นต่ำ)',
    follow2s:    '2 วิ',
    follow3s:    '3 วิ',
    emptyHint:   'พิมพ์ความเร็วเพื่อเริ่มคำนวณ',
    offline:     'คำนวณไม่ได้ — ตรวจสอบการเชื่อมต่อ',
  },
  en: {
    title:       'Traffic Math',
    subtitle:    'Stopping distance calculator',
    speedLabel:  'Speed (km/h)',
    condLabel:   'Road condition',
    tapHint:     'Tap a step for explanation',
    totalStop:   'Total stopping distance',
    carLengths:  'car lengths',
    followTitle: 'Following distance',
    followSub:   '2-second rule (minimum)',
    follow2s:    '2 sec',
    follow3s:    '3 sec',
    emptyHint:   'Enter a speed to begin',
    offline:     'Calculation unavailable — check connection',
  },
};

// ─── Screen ───────────────────────────────────────────────────────────────────

export default function TrafficMathScreen() {
  const router = useRouter();
  const { language, colors } = useAppStore();
  const c   = colors;
  const t   = TR[language] ?? TR.en;
  const lang = (['no', 'th', 'en'].includes(language) ? language : 'en') as Lang;
  const isDark = c.bg === '#0F172A' || c.bg === '#0B1222';

  // ── Input state ──────────────────────────────────────────────────────────────
  const [speedText,  setSpeedText]  = useState('80');
  const [condition,  setCondition]  = useState<ConditionKey>(DEFAULT_CONDITION);
  const [followSecs, setFollowSecs] = useState<2 | 3>(2);

  const speedNum    = parseFloat(speedText) || 0;
  const condInfo    = getConditionMeta(condition);
  const accentColor = condInfo.color;

  // ── Data ─────────────────────────────────────────────────────────────────────
  const { result, loading, error, isStale } = useTrafficMath(
    speedNum > 0 ? speedNum : null,
    condition,
  );

  // Pre-warm common speeds on mount — silent, fire-and-forget
  useEffect(() => { prewarmTrafficMath(condition); }, []);

  // ── Derived values ────────────────────────────────────────────────────────────
  // Following distance: trivial inline math, no API call
  const followDist = speedNum > 0
    ? Math.round((speedNum / 3.6) * followSecs * 10) / 10
    : null;
  const followCars = followDist ? Math.round(followDist / 4.5) : 0;

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <LinearGradient
        colors={isDark ? ['#0B1222', '#0F172A', '#0B1222'] : ['#F4F8FD', '#FFFFFF', '#EEF5FB']}
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />

      {/* ── Header ── */}
      <View style={[st.header, { borderBottomColor: `${c.divider}70` }]}>
        <Pressable
          style={({ pressed }) => [
            st.backBtn,
            { backgroundColor: c.card, borderColor: c.cardBorder, opacity: pressed ? 0.7 : 1 },
          ]}
          onPress={() => router.back()}
          hitSlop={8}
        >
          <Ionicons name="arrow-back" size={20} color={c.text} />
        </Pressable>
        <View style={{ flex: 1, marginLeft: 12 }}>
          <Text style={[st.headerTitle, { color: c.text }]}>{t.title}</Text>
          <Text style={[st.headerSub,   { color: c.textMuted }]}>{t.subtitle}</Text>
        </View>
        <View style={[st.condBadge, { backgroundColor: `${accentColor}20`, borderColor: `${accentColor}40` }]}>
          <Ionicons name={condInfo.iconName as any} size={16} color={accentColor} />
        </View>
      </View>

      {/* ── Content ── */}
      <ScrollView
        contentContainerStyle={[st.scroll, { alignItems: 'center' }]}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <View style={{ width: Math.min(Dimensions.get('window').width, CONTENT_MAX_W), gap: 12 }}>

          {/* Speed input card */}
          <View style={[st.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={[st.sectionLabel, { color: c.textMuted }]}>{t.speedLabel}</Text>

            <View style={st.speedRow}>
              <TextInput
                style={[
                  st.speedInput,
                  { color: c.text },
                  Platform.OS === 'web' ? ({ outlineWidth: 0 } as any) : undefined,
                ]}
                value={speedText}
                onChangeText={v => setSpeedText(v.replace(/[^0-9]/g, '').slice(0, 3))}
                keyboardType="numeric"
                maxLength={3}
                selectTextOnFocus
                placeholderTextColor={c.textMuted}
                placeholder="—"
              />
              <Text style={[st.speedUnit, { color: c.textSecondary }]}>km/h</Text>

              {/* Subtle loading indicator — doesn't move any layout */}
              {loading && (
                <ActivityIndicator
                  size="small"
                  color={accentColor}
                  style={{ marginLeft: 8 }}
                />
              )}
            </View>

            {/* Speed presets */}
            <View style={st.presetRow}>
              {SPEED_PRESETS.map(p => {
                const active = speedText === String(p);
                return (
                  <Pressable
                    key={p}
                    style={[
                      st.presetChip,
                      {
                        backgroundColor: active ? accentColor : `${accentColor}14`,
                        borderColor:     active ? accentColor : `${accentColor}35`,
                      },
                    ]}
                    onPress={() => setSpeedText(String(p))}
                  >
                    <Text style={[st.presetText, { color: active ? '#fff' : accentColor }]}>
                      {p}
                    </Text>
                  </Pressable>
                );
              })}
            </View>
          </View>

          {/* Condition chips */}
          <View style={[st.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={[st.sectionLabel, { color: c.textMuted }]}>{t.condLabel}</Text>
            <ConditionChips
              value={condition}
              onChange={setCondition}
              lang={lang}
              textMuted={c.textMuted}
              textSecondary={c.textSecondary}
            />
          </View>

          {/* Empty state */}
          {!speedNum && (
            <Text style={[st.emptyHint, { color: c.textMuted }]}>{t.emptyHint}</Text>
          )}

          {/* Offline / error state — only shown when there's no result to display */}
          {error && !result && speedNum > 0 && (
            <Text style={[st.emptyHint, { color: c.textMuted }]}>{t.offline}</Text>
          )}

          {/* Results — stay visible while isStale (new result loading) */}
          {result && (
            <>
              {/* Step-by-step breakdown */}
              <View style={{ gap: 8 }}>
                <Text style={[st.tapHint, { color: c.textMuted }]}>{t.tapHint}</Text>
                {result.steps.map(step => (
                  <StepCard
                    key={step.order}
                    step={step}
                    lang={lang}
                    cardBg={isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)'}
                    textColor={c.text}
                    textSecondary={c.textSecondary}
                    textMuted={c.textMuted}
                    dimmed={isStale}
                  />
                ))}
              </View>

              {/* Total stopping distance + danger bar */}
              <View style={[st.dangerCard, { backgroundColor: `${accentColor}12`, borderColor: `${accentColor}45` }]}>
                <View style={st.dangerTop}>
                  <View>
                    <Text style={[st.dangerLabel, { color: accentColor }]}>{t.totalStop}</Text>
                    <Text style={[st.dangerValue, { color: c.text }]}>
                      {result.results.stopping_distance_m}
                      <Text style={[st.dangerUnit, { color: c.textSecondary }]}> m</Text>
                    </Text>
                  </View>
                  <View style={{ alignItems: 'flex-end' }}>
                    <Text style={[st.carsNum, { color: accentColor }]}>
                      {result.danger_context.car_lengths}
                    </Text>
                    <Text style={[st.carsSub, { color: c.textMuted }]}>{t.carLengths}</Text>
                  </View>
                </View>

                <DangerBar
                  carLengths={result.danger_context.car_lengths}
                  color={accentColor}
                  trackColor={isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.08)'}
                />

                <Text style={[st.dangerDesc, { color: c.textSecondary }]}>
                  {result.danger_context.description[lang]}
                </Text>
              </View>

              {/* Following distance */}
              <View style={[st.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
                <View style={st.followRow}>
                  <View style={{ flex: 1 }}>
                    <Text style={[st.sectionLabel, { color: c.textMuted }]}>{t.followTitle}</Text>
                    <Text style={[st.followSub, { color: c.textSecondary }]}>{t.followSub}</Text>
                  </View>
                  {/* 2s / 3s toggle */}
                  <View style={[st.toggle, { backgroundColor: `${c.textMuted}18` }]}>
                    {([2, 3] as const).map(s => (
                      <Pressable
                        key={s}
                        style={[st.toggleBtn, followSecs === s && { backgroundColor: accentColor }]}
                        onPress={() => setFollowSecs(s)}
                      >
                        <Text style={[st.toggleText, { color: followSecs === s ? '#fff' : c.textSecondary }]}>
                          {s === 2 ? t.follow2s : t.follow3s}
                        </Text>
                      </Pressable>
                    ))}
                  </View>
                </View>

                {followDist !== null && (
                  <View style={[st.followResult, { borderColor: `${accentColor}28` }]}>
                    <Text style={[st.followDist, { color: accentColor }]}>{followDist} m</Text>
                    <Text style={[st.followCars, { color: c.textMuted }]}>
                      ≈ {followCars} {t.carLengths}
                    </Text>
                  </View>
                )}
              </View>
            </>
          )}

          <View style={{ height: 40 }} />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const st = StyleSheet.create({
  container:    { flex: 1 },
  header:       {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 16, paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  backBtn:      {
    width: 38, height: 38, borderRadius: 12,
    justifyContent: 'center', alignItems: 'center', borderWidth: 1,
  },
  headerTitle:  { fontSize: 17, fontWeight: '700', letterSpacing: -0.3 },
  headerSub:    { fontSize: 12, marginTop: 1 },
  condBadge:    {
    width: 36, height: 36, borderRadius: 10,
    justifyContent: 'center', alignItems: 'center', borderWidth: 1,
  },

  scroll:       { padding: 16, paddingBottom: 32 },
  card:         { borderRadius: 16, borderWidth: 1, padding: 16, gap: 10 },
  sectionLabel: { fontSize: 11, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.8 },

  // Speed
  speedRow:     { flexDirection: 'row', alignItems: 'baseline', gap: 4 },
  speedInput:   { fontSize: 52, fontWeight: '800', letterSpacing: -2, minWidth: 80 },
  speedUnit:    { fontSize: 20, fontWeight: '600', paddingBottom: 4 },
  presetRow:    { flexDirection: 'row', gap: 8, flexWrap: 'wrap' },
  presetChip:   { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8, borderWidth: 1 },
  presetText:   { fontSize: 13, fontWeight: '700' },

  // Hints
  tapHint:      { fontSize: 11, textAlign: 'center' },
  emptyHint:    { textAlign: 'center', fontSize: 13, paddingVertical: 32 },

  // Danger block
  dangerCard:   { borderRadius: 16, borderWidth: 1, padding: 16, gap: 10 },
  dangerTop:    { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  dangerLabel:  { fontSize: 11, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 2 },
  dangerValue:  { fontSize: 40, fontWeight: '800', letterSpacing: -1.5 },
  dangerUnit:   { fontSize: 20, fontWeight: '600' },
  carsNum:      { fontSize: 28, fontWeight: '800', letterSpacing: -1 },
  carsSub:      { fontSize: 11, marginTop: 2 },
  dangerDesc:   { fontSize: 13, lineHeight: 18 },

  // Following
  followRow:    { flexDirection: 'row', alignItems: 'center', gap: 10 },
  followSub:    { fontSize: 11, marginTop: 2 },
  toggle:       { flexDirection: 'row', borderRadius: 8, padding: 3, gap: 3 },
  toggleBtn:    { paddingHorizontal: 12, paddingVertical: 5, borderRadius: 6 },
  toggleText:   { fontSize: 12, fontWeight: '600' },
  followResult: { borderTopWidth: StyleSheet.hairlineWidth, paddingTop: 10, flexDirection: 'row', alignItems: 'baseline', gap: 8 },
  followDist:   { fontSize: 28, fontWeight: '800', letterSpacing: -0.8 },
  followCars:   { fontSize: 13 },
});
