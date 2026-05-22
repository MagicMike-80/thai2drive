/**
 * Traffic Math Screen — Thai2Drive
 * ----------------------------------
 * Interactive stopping-distance calculator.
 * Mobile-first layout; centered max-width container on web.
 *
 * UX principles:
 *   - Feel like a driving instructor explaining danger, not a formula sheet
 *   - Auto-calculate on every input change (no button needed)
 *   - Condition switch makes the danger jump instantly visible
 *   - Car-length bar makes abstract metres feel real
 */
import React, { useEffect, useRef, useState } from 'react';
import {
  View, Text, StyleSheet, TextInput, Pressable, ScrollView,
  ActivityIndicator, Animated, Platform, Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useAppStore } from '../src/store/appStore';
import { trafficMathApi, StoppingDistanceResult } from '../src/services/trafficMath';

// ─── Constants ────────────────────────────────────────────────────────────────

const SCREEN_W  = Dimensions.get('window').width;
const CONTENT_W = Math.min(SCREEN_W, 600);   // cap at 600 on wide screens / web

const PRESETS = [30, 50, 80, 100, 120];

const CONDITIONS = [
  { key: 'dry',  iconName: 'sunny',        color: '#22C55E', no: 'Tørr', th: 'แห้ง',   en: 'Dry'  },
  { key: 'wet',  iconName: 'rainy',        color: '#3B82F6', no: 'Våt',  th: 'เปียก', en: 'Wet'  },
  { key: 'snow', iconName: 'snow',         color: '#A855F7', no: 'Snø',  th: 'หิมะ',  en: 'Snow' },
  { key: 'ice',  iconName: 'thermometer',  color: '#EF4444', no: 'Is',   th: 'น้ำแข็ง', en: 'Ice'  },
] as const;

// Visual "danger escalation" — greens at step 1, reds at step 4
const STEP_COLORS = ['#10B981', '#F59E0B', '#F97316', '#EF4444'];

// ─── Translations ─────────────────────────────────────────────────────────────

const TR: Record<string, Record<string, string>> = {
  no: {
    title:         'Trafikk-matte',
    subtitle:      'Stoppe­avstand kalkulator',
    speed:         'Fart (km/t)',
    condition:     'Veibane',
    calculating:   'Beregner…',
    totalStop:     'Stoppeavstand',
    carLengths:    'bilers lengde',
    busLengths:    'busslengder',
    followTitle:   'Følgeavstand',
    followSub:     '2-sekunders regel (minimum)',
    follow2s:      '2 sek',
    follow3s:      '3 sek',
    tapHint:       'Trykk på et steg for mer info',
    emptyHint:     'Skriv inn en fart for å se beregningen',
  },
  th: {
    title:         'คณิตศาสตร์จราจร',
    subtitle:      'คำนวณระยะหยุดรถ',
    speed:         'ความเร็ว (กม./ชม.)',
    condition:     'สภาพถนน',
    calculating:   'กำลังคำนวณ…',
    totalStop:     'ระยะหยุดรวม',
    carLengths:    'คันรถ',
    busLengths:    'คันรถบัส',
    followTitle:   'ระยะห่างจากรถคันหน้า',
    followSub:     'กฎ 2 วินาที (ขั้นต่ำ)',
    follow2s:      '2 วิ',
    follow3s:      '3 วิ',
    tapHint:       'กดที่ขั้นตอนเพื่อดูรายละเอียด',
    emptyHint:     'พิมพ์ความเร็วเพื่อดูการคำนวณ',
  },
  en: {
    title:         'Traffic Math',
    subtitle:      'Stopping distance calculator',
    speed:         'Speed (km/h)',
    condition:     'Road condition',
    calculating:   'Calculating…',
    totalStop:     'Total stopping distance',
    carLengths:    'car lengths',
    busLengths:    'bus lengths',
    followTitle:   'Following distance',
    followSub:     '2-second rule (minimum)',
    follow2s:      '2 sec',
    follow3s:      '3 sec',
    tapHint:       'Tap a step for details',
    emptyHint:     'Enter a speed to see the calculation',
  },
};

// ─── Sub-components ───────────────────────────────────────────────────────────

/** Single step card — tappable to reveal the note. */
function StepCard({
  step, lang, c, isDark,
}: {
  step: StoppingDistanceResult['steps'][number];
  lang: string;
  c: any;
  isDark: boolean;
}) {
  const [open, setOpen] = useState(false);
  const anim = useRef(new Animated.Value(0)).current;
  const color = STEP_COLORS[step.order - 1] || c.accent;
  const label = step.label[lang as keyof typeof step.label] || step.label.en;
  const note  = step.note[lang as keyof typeof step.note]  || step.note.en;

  const toggle = () => {
    setOpen(v => !v);
    Animated.timing(anim, {
      toValue: open ? 0 : 1,
      duration: 200,
      useNativeDriver: true,
    }).start();
  };

  return (
    <Pressable onPress={toggle} style={[sst.stepCard, { borderColor: `${color}35`, backgroundColor: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)' }]}>
      {/* Left accent bar */}
      <View style={[sst.stepAccent, { backgroundColor: color }]} />

      <View style={{ flex: 1 }}>
        {/* Header row */}
        <View style={sst.stepHeader}>
          <View style={[sst.stepOrderBadge, { backgroundColor: `${color}20` }]}>
            <Text style={[sst.stepOrder, { color }]}>{step.order}</Text>
          </View>
          <Text style={[sst.stepLabel, { color: c.text }]}>{label}</Text>
          <Text style={[sst.stepFormula, { color: c.textSecondary }]}>{step.formula}</Text>
          <Text style={[sst.stepResult, { color }]}>{step.result} <Text style={[sst.stepUnit, { color: c.textMuted }]}>{step.unit}</Text></Text>
        </View>

        {/* Expandable note */}
        {open && (
          <Animated.View style={{ opacity: anim, marginTop: 8 }}>
            <Text style={[sst.stepNote, { color: c.textSecondary }]}>{note}</Text>
          </Animated.View>
        )}
      </View>

      <Ionicons name={open ? 'chevron-up' : 'chevron-down'} size={14} color={c.textMuted} style={{ marginTop: 2 }} />
    </Pressable>
  );
}

/** Car-length danger bar — visual metaphor for the total distance. */
function DangerBar({ carLengths, color }: { carLengths: number; color: string }) {
  const anim = useRef(new Animated.Value(0)).current;
  const filled = Math.min(Math.round(carLengths), 20);  // cap visual at 20 cars

  useEffect(() => {
    anim.setValue(0);
    Animated.timing(anim, { toValue: 1, duration: 600, useNativeDriver: false }).start();
  }, [carLengths]);

  const widthPct = anim.interpolate({ inputRange: [0, 1], outputRange: ['0%', `${Math.min((filled / 20) * 100, 100)}%`] });

  return (
    <View style={sst.dangerBarWrap}>
      <View style={sst.dangerTrack}>
        <Animated.View style={[sst.dangerFill, { width: widthPct, backgroundColor: color }]} />
      </View>
    </View>
  );
}

// ─── Main screen ──────────────────────────────────────────────────────────────

export default function TrafficMathScreen() {
  const router     = useRouter();
  const { language, colors } = useAppStore();
  const t  = TR[language] || TR.en;
  const c  = colors;
  const isDark = c.bg === '#0F172A' || c.bg === '#0B1222';

  const [speedText,  setSpeedText]  = useState('80');
  const [condition,  setCondition]  = useState<string>('dry');
  const [followSecs, setFollowSecs] = useState<2 | 3>(2);
  const [result,     setResult]     = useState<StoppingDistanceResult | null>(null);
  const [loading,    setLoading]    = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const condInfo = CONDITIONS.find(x => x.key === condition) ?? CONDITIONS[0];
  const accentColor = condInfo.color;

  // Auto-calculate with 350 ms debounce
  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    const speed = parseFloat(speedText);
    if (!speed || speed <= 0 || speed > 250) { setResult(null); setLoading(false); return; }

    setLoading(true);
    timerRef.current = setTimeout(async () => {
      const data = await trafficMathApi.getStoppingDistance(speed, condition);
      setResult(data);
      setLoading(false);
    }, 350);

    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [speedText, condition]);

  const followResult = result
    ? Math.round((parseFloat(speedText) / 3.6) * followSecs * 10) / 10
    : null;

  const lang3 = (language === 'no' || language === 'th' || language === 'en') ? language : 'en';

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      {/* Gradient */}
      <LinearGradient
        colors={isDark ? ['#0B1222', '#0F172A', '#0B1222'] : ['#F4F8FD', '#FFFFFF', '#EEF5FB']}
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />

      {/* Header */}
      <View style={[st.header, { borderBottomColor: `${c.divider}70` }]}>
        <Pressable
          style={({ pressed }) => [st.backBtn, { backgroundColor: c.card, borderColor: c.cardBorder, opacity: pressed ? 0.7 : 1 }]}
          onPress={() => router.back()}
          hitSlop={8}
        >
          <Ionicons name="arrow-back" size={20} color={c.text} />
        </Pressable>
        <View style={{ flex: 1, marginLeft: 12 }}>
          <Text style={[st.headerTitle, { color: c.text }]}>{t.title}</Text>
          <Text style={[st.headerSub, { color: c.textMuted }]}>{t.subtitle}</Text>
        </View>
        <View style={[st.headerBadge, { backgroundColor: `${accentColor}20`, borderColor: `${accentColor}40` }]}>
          <Ionicons name={condInfo.iconName as any} size={16} color={accentColor} />
        </View>
      </View>

      <ScrollView
        contentContainerStyle={[st.scroll, { alignItems: 'center' }]}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <View style={[st.contentWrap, { width: CONTENT_W }]}>

          {/* ── Speed input ── */}
          <View style={[st.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={[st.sectionLabel, { color: c.textMuted }]}>{t.speed}</Text>

            {/* Big speed display */}
            <View style={st.speedRow}>
              <TextInput
                style={[st.speedInput, { color: c.text }]}
                value={speedText}
                onChangeText={v => setSpeedText(v.replace(/[^0-9]/g, '').slice(0, 3))}
                keyboardType="numeric"
                maxLength={3}
                selectTextOnFocus
                placeholderTextColor={c.textMuted}
                placeholder="—"
                // Web: prevent default browser outline
                {...(Platform.OS === 'web' ? { style: [st.speedInput, { color: c.text, outlineWidth: 0 } as any] } : {})}
              />
              <Text style={[st.speedUnit, { color: c.textSecondary }]}>km/h</Text>
            </View>

            {/* Preset chips */}
            <View style={st.presetRow}>
              {PRESETS.map(p => {
                const active = speedText === String(p);
                return (
                  <Pressable
                    key={p}
                    style={[st.presetChip, {
                      backgroundColor: active ? accentColor : `${accentColor}14`,
                      borderColor:     active ? accentColor : `${accentColor}35`,
                    }]}
                    onPress={() => setSpeedText(String(p))}
                  >
                    <Text style={[st.presetText, { color: active ? '#fff' : accentColor }]}>{p}</Text>
                  </Pressable>
                );
              })}
            </View>
          </View>

          {/* ── Condition selector ── */}
          <View style={[st.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={[st.sectionLabel, { color: c.textMuted }]}>{t.condition}</Text>
            <View style={st.condRow}>
              {CONDITIONS.map(cond => {
                const active = condition === cond.key;
                const label  = cond[lang3 as keyof typeof cond] as string;
                return (
                  <Pressable
                    key={cond.key}
                    style={[st.condChip, {
                      flex: 1,
                      backgroundColor: active ? `${cond.color}20` : 'transparent',
                      borderColor:     active ? cond.color : `${c.textMuted}30`,
                    }]}
                    onPress={() => setCondition(cond.key)}
                  >
                    <Ionicons name={cond.iconName as any} size={18} color={active ? cond.color : c.textMuted} />
                    <Text style={[st.condLabel, { color: active ? cond.color : c.textSecondary }]}>{label}</Text>
                  </Pressable>
                );
              })}
            </View>
          </View>

          {/* ── Results ── */}
          {loading && (
            <View style={st.loadingRow}>
              <ActivityIndicator size="small" color={accentColor} />
              <Text style={[st.loadingText, { color: c.textMuted }]}>{t.calculating}</Text>
            </View>
          )}

          {!loading && !result && (
            <Text style={[st.emptyHint, { color: c.textMuted }]}>{t.emptyHint}</Text>
          )}

          {!loading && result && (
            <>
              {/* Step cards */}
              <View style={st.stepsWrap}>
                <Text style={[st.tapHint, { color: c.textMuted }]}>{t.tapHint}</Text>
                {result.steps.map(step => (
                  <StepCard key={step.order} step={step} lang={lang3} c={c} isDark={isDark} />
                ))}
              </View>

              {/* Total danger block */}
              <View style={[st.dangerCard, { backgroundColor: `${accentColor}12`, borderColor: `${accentColor}45` }]}>
                <View style={st.dangerTop}>
                  <View>
                    <Text style={[st.dangerLabel, { color: accentColor }]}>{t.totalStop}</Text>
                    <Text style={[st.dangerValue, { color: c.text }]}>
                      {result.results.stopping_distance_m} <Text style={[st.dangerUnit, { color: c.textSecondary }]}>m</Text>
                    </Text>
                  </View>
                  <View style={{ alignItems: 'flex-end' }}>
                    <Text style={[st.dangerCarsNum, { color: accentColor }]}>
                      {result.danger_context.car_lengths}
                    </Text>
                    <Text style={[st.dangerCarsSub, { color: c.textMuted }]}>{t.carLengths}</Text>
                  </View>
                </View>
                <DangerBar carLengths={result.danger_context.car_lengths} color={accentColor} />
                <Text style={[st.dangerDesc, { color: c.textSecondary }]}>
                  {result.danger_context.description[lang3]}
                </Text>
              </View>

              {/* ── Following distance ── */}
              <View style={[st.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
                <View style={st.followHeader}>
                  <View>
                    <Text style={[st.sectionLabel, { color: c.textMuted }]}>{t.followTitle}</Text>
                    <Text style={[st.followSub, { color: c.textSecondary }]}>{t.followSub}</Text>
                  </View>
                  {/* Toggle 2s / 3s */}
                  <View style={[st.secToggle, { backgroundColor: `${c.textMuted}20` }]}>
                    {([2, 3] as const).map(s => (
                      <Pressable
                        key={s}
                        style={[st.secToggleBtn, followSecs === s && { backgroundColor: accentColor }]}
                        onPress={() => setFollowSecs(s)}
                      >
                        <Text style={[st.secToggleText, { color: followSecs === s ? '#fff' : c.textSecondary }]}>
                          {s === 2 ? t.follow2s : t.follow3s}
                        </Text>
                      </Pressable>
                    ))}
                  </View>
                </View>

                {followResult !== null && (
                  <View style={[st.followResult, { borderColor: `${accentColor}30` }]}>
                    <Text style={[st.followDist, { color: accentColor }]}>{followResult} m</Text>
                    <Text style={[st.followCars, { color: c.textMuted }]}>
                      ≈ {Math.round(followResult / 4.5)} {t.carLengths}
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
  container:   { flex: 1 },
  header:      { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: StyleSheet.hairlineWidth },
  backBtn:     { width: 38, height: 38, borderRadius: 12, justifyContent: 'center', alignItems: 'center', borderWidth: 1 },
  headerTitle: { fontSize: 17, fontWeight: '700', letterSpacing: -0.3 },
  headerSub:   { fontSize: 12, marginTop: 1 },
  headerBadge: { width: 36, height: 36, borderRadius: 10, justifyContent: 'center', alignItems: 'center', borderWidth: 1 },

  scroll:      { padding: 16, paddingBottom: 32 },
  contentWrap: { gap: 12 },

  card:        { borderRadius: 16, borderWidth: 1, padding: 16, gap: 10 },
  sectionLabel: { fontSize: 11, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.8 },

  // Speed input
  speedRow:    { flexDirection: 'row', alignItems: 'baseline', gap: 8 },
  speedInput:  { fontSize: 52, fontWeight: '800', letterSpacing: -2, minWidth: 80 },
  speedUnit:   { fontSize: 20, fontWeight: '600', paddingBottom: 4 },
  presetRow:   { flexDirection: 'row', gap: 8, flexWrap: 'wrap' },
  presetChip:  { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8, borderWidth: 1 },
  presetText:  { fontSize: 13, fontWeight: '700' },

  // Condition
  condRow:     { flexDirection: 'row', gap: 6 },
  condChip:    { alignItems: 'center', gap: 4, paddingVertical: 10, paddingHorizontal: 6, borderRadius: 10, borderWidth: 1 },
  condLabel:   { fontSize: 11, fontWeight: '600' },

  // Steps
  stepsWrap:   { gap: 8 },
  tapHint:     { fontSize: 11, textAlign: 'center', marginBottom: 4 },

  // Danger card
  dangerCard:  { borderRadius: 16, borderWidth: 1, padding: 16, gap: 10 },
  dangerTop:   { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  dangerLabel: { fontSize: 11, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 2 },
  dangerValue: { fontSize: 40, fontWeight: '800', letterSpacing: -1.5 },
  dangerUnit:  { fontSize: 20, fontWeight: '600' },
  dangerCarsNum: { fontSize: 28, fontWeight: '800', letterSpacing: -1 },
  dangerCarsSub: { fontSize: 11, marginTop: 2 },
  dangerDesc:  { fontSize: 13, lineHeight: 18 },

  // Danger bar
  dangerBarWrap: { height: 10, borderRadius: 6, overflow: 'hidden' },
  dangerTrack:   { flex: 1, backgroundColor: 'rgba(255,255,255,0.12)', borderRadius: 6, overflow: 'hidden' },
  dangerFill:    { height: '100%', borderRadius: 6 },

  // Following
  followHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 10 },
  followSub:    { fontSize: 11, marginTop: 2 },
  secToggle:    { flexDirection: 'row', borderRadius: 8, padding: 3, gap: 3 },
  secToggleBtn: { paddingHorizontal: 12, paddingVertical: 5, borderRadius: 6 },
  secToggleText: { fontSize: 12, fontWeight: '600' },
  followResult: { borderTopWidth: StyleSheet.hairlineWidth, paddingTop: 10, flexDirection: 'row', alignItems: 'baseline', gap: 8 },
  followDist:   { fontSize: 28, fontWeight: '800', letterSpacing: -0.8 },
  followCars:   { fontSize: 13 },

  // Loading / empty
  loadingRow:  { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, paddingVertical: 20 },
  loadingText: { fontSize: 13 },
  emptyHint:   { textAlign: 'center', fontSize: 13, paddingVertical: 32 },
});

// Step card styles (separate namespace)
const sst = StyleSheet.create({
  stepCard:    { flexDirection: 'row', borderRadius: 12, borderWidth: 1, overflow: 'hidden', padding: 12, paddingLeft: 0, gap: 10, alignItems: 'flex-start' },
  stepAccent:  { width: 4, alignSelf: 'stretch', borderRadius: 2, marginRight: 6 },
  stepHeader:  { flexDirection: 'row', alignItems: 'center', gap: 8, flexWrap: 'wrap' },
  stepOrderBadge: { width: 22, height: 22, borderRadius: 6, justifyContent: 'center', alignItems: 'center' },
  stepOrder:   { fontSize: 11, fontWeight: '800' },
  stepLabel:   { fontSize: 13, fontWeight: '600', flex: 1, minWidth: 80 },
  stepFormula: { fontSize: 11, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
  stepResult:  { fontSize: 15, fontWeight: '800', marginLeft: 'auto' },
  stepUnit:    { fontSize: 11, fontWeight: '400' },
  stepNote:    { fontSize: 12, lineHeight: 18 },
});
