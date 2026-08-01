/**
 * TrafficMathDesktopPanel
 * ────────────────────────────────────────────────────────────────────────────
 * Wide two-column panel for desktop web only.
 * Uses react-dom createPortal to render at document.body level, completely
 * bypassing the 390 px WebAppShell frame and its overflow:hidden.
 *
 * Left column  — speed input, road conditions, step-by-step breakdown
 * Right column — stopping distance visualisation (diagram + numbers)
 *
 * Mobile: not rendered (caller falls back to router.push('/traffic-math'))
 */

import React, { useState, useEffect, memo } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

import { useTrafficMath, prewarmTrafficMath } from '../../hooks/useTrafficMath';
import { StepCard, DangerBar, ConditionChips } from './index';
import {
  SPEED_PRESETS,
  DEFAULT_CONDITION,
  type ConditionKey,
  type Lang,
  getConditionMeta,
} from '../../constants/trafficMath';

// ─── Web portal helper ────────────────────────────────────────────────────────
// Renders at document.body level, bypassing ALL ancestor overflow:hidden
// including the 390 px WebAppShell phone frame.
let _portal: ((node: React.ReactNode, container: Element) => any) | null = null;
if (Platform.OS === 'web') {
  try { _portal = require('react-dom').createPortal; } catch {}
}

// ─── Translations ─────────────────────────────────────────────────────────────

const TR: Record<string, Record<string, string>> = {
  no: {
    title:        'Trafikk-matte',
    subtitle:     'Stoppeavstand-kalkulator',
    speedLabel:   'Fart (km/t)',
    condLabel:    'Veibane',
    tapHint:      'Trykk på et steg for forklaring',
    totalStop:    'Stoppeavstand',
    carLengths:   'bilers lengde',
    followTitle:  'Følgeavstand',
    followSub:    '2-sekunders regel (minimum)',
    follow2s:     '2 sek',
    follow3s:     '3 sek',
    emptyHint:    'Skriv inn en fart for å starte',
    offline:      'Beregning utilgjengelig',
    reaction:     'Reaksjonstid',
    braking:      'Bremselengde',
    vizTitle:     'Stoppeavstand',
    atSpeed:      'ved',
    carLen:       'bilers lengde',
    condition:    'Kjøreforhold',
  },
  th: {
    title:        'คณิตศาสตร์จราจร',
    subtitle:     'คำนวณระยะหยุดรถ',
    speedLabel:   'ความเร็ว (กม./ชม.)',
    condLabel:    'สภาพถนน',
    tapHint:      'กดที่ขั้นตอนเพื่อดูคำอธิบาย',
    totalStop:    'ระยะหยุดรวม',
    carLengths:   'คันรถ',
    followTitle:  'ระยะห่างจากรถคันหน้า',
    followSub:    'กฎ 2 วินาที (ขั้นต่ำ)',
    follow2s:     '2 วิ',
    follow3s:     '3 วิ',
    emptyHint:    'พิมพ์ความเร็วเพื่อเริ่มคำนวณ',
    offline:      'คำนวณไม่ได้',
    reaction:     'ปฏิกิริยา',
    braking:      'เบรก',
    vizTitle:     'ระยะหยุดรวม',
    atSpeed:      'ที่',
    carLen:       'คัน',
    condition:    'สภาพถนน',
  },
  en: {
    title:        'Traffic Math',
    subtitle:     'Stopping distance calculator',
    speedLabel:   'Speed (km/h)',
    condLabel:    'Road condition',
    tapHint:      'Tap a step for explanation',
    totalStop:    'Total stopping distance',
    carLengths:   'car lengths',
    followTitle:  'Following distance',
    followSub:    '2-second rule (minimum)',
    follow2s:     '2 sec',
    follow3s:     '3 sec',
    emptyHint:    'Enter a speed to begin',
    offline:      'Calculation unavailable',
    reaction:     'Reaction',
    braking:      'Braking',
    vizTitle:     'Stopping distance',
    atSpeed:      'at',
    carLen:       'car lengths',
    condition:    'Road condition',
  },
};

// ─── Stopping distance road visualisation ────────────────────────────────────

interface VizProps {
  result:      ReturnType<typeof useTrafficMath>['result'];
  accentColor: string;
  textColor:   string;
  textMuted:   string;
  textSec:     string;
  isDark:      boolean;
  lang:        Lang;
  t:           Record<string, string>;
}

const StoppingDistanceViz = memo(function StoppingDistanceViz({
  result, accentColor, textColor, textMuted, textSec, isDark, lang, t,
}: VizProps) {
  if (!result) {
    return (
      <View style={viz.empty}>
        <Ionicons name="speedometer-outline" size={56} color={accentColor} style={{ opacity: 0.35 }} />
        <Text style={[viz.emptyText, { color: textMuted }]}>{t.emptyHint}</Text>
      </View>
    );
  }

  const total    = result.results.stopping_distance_m;
  const reaction = result.results.reaction_distance_m;
  const braking  = result.results.braking_distance_m;
  const carLen   = result.danger_context.car_lengths;

  const reactionFrac = total > 0 ? reaction / total : 0.38;
  const brakingFrac  = total > 0 ? braking  / total : 0.62;

  // Språkrenhet: kun aktivt språk. Mangler teksten, skjules den (Fail-Stop).
  const condLabel = result.condition_info.label[lang] ?? '';
  const condNote  = result.condition_info.note[lang]  ?? '';

  return (
    <View style={viz.wrap}>

      {/* ── Big speed pill ── */}
      <View style={[viz.speedPill, { borderColor: `${accentColor}50`, backgroundColor: isDark ? `${accentColor}14` : `${accentColor}0D` }]}>
        <Text style={[viz.speedNum, { color: accentColor }]}>{result.input.speed_kmh}</Text>
        <Text style={[viz.speedUnit, { color: textMuted }]}>km/h</Text>
      </View>

      {/* ── Road diagram ── */}
      <View style={viz.roadWrap}>
        {/* Road surface */}
        <View style={[viz.road, { backgroundColor: isDark ? '#1E293B' : '#374151' }]}>
          {/* Dashes */}
          {[...Array(7)].map((_, i) => (
            <View
              key={i}
              style={[viz.dash, { backgroundColor: isDark ? 'rgba(255,255,255,0.15)' : 'rgba(255,255,255,0.25)' }]}
            />
          ))}
        </View>

        {/* Distance bars — sit on top of the road via absolute positioning */}
        <View style={viz.bars}>
          {/* Reaction bar */}
          <View style={[viz.bar, { flex: reactionFrac, backgroundColor: '#F59E0B', opacity: 0.88 }]}>
            <Text style={viz.barLabel}>{reaction}m</Text>
          </View>
          {/* Braking bar */}
          <View style={[viz.bar, { flex: brakingFrac, backgroundColor: '#EF4444', opacity: 0.88 }]}>
            <Text style={viz.barLabel}>{braking}m</Text>
          </View>
        </View>

        {/* Car icon — left edge */}
        <View style={[viz.carIcon, { backgroundColor: isDark ? '#0F172A' : '#fff', borderColor: accentColor }]}>
          <Ionicons name="car-sport" size={20} color={accentColor} />
        </View>
        {/* Stop icon — right edge */}
        <View style={[viz.stopIcon, { backgroundColor: '#EF4444' }]}>
          <Ionicons name="hand-left" size={16} color="#fff" />
        </View>
      </View>

      {/* ── Legend ── */}
      <View style={viz.legend}>
        <View style={viz.legendItem}>
          <View style={[viz.dot, { backgroundColor: '#F59E0B' }]} />
          <Text style={[viz.legendText, { color: textSec }]}>{t.reaction}: {reaction} m</Text>
        </View>
        <View style={viz.legendItem}>
          <View style={[viz.dot, { backgroundColor: '#EF4444' }]} />
          <Text style={[viz.legendText, { color: textSec }]}>{t.braking}: {braking} m</Text>
        </View>
      </View>

      {/* ── Total stopping distance — hero number ── */}
      <View style={[viz.totalCard, { backgroundColor: `${accentColor}12`, borderColor: `${accentColor}40` }]}>
        <View style={viz.totalRow}>
          <View>
            <Text style={[viz.totalLabel, { color: accentColor }]}>{t.vizTitle}</Text>
            <View style={viz.totalNumRow}>
              <Text style={[viz.totalNum, { color: textColor }]}>{total}</Text>
              <Text style={[viz.totalUnit, { color: textSec }]}>  m</Text>
            </View>
          </View>
          <View style={viz.carLenBlock}>
            <Text style={[viz.carLenNum, { color: accentColor }]}>{carLen}</Text>
            <Text style={[viz.carLenSub, { color: textMuted }]}>{t.carLen}</Text>
          </View>
        </View>
        <DangerBar
          carLengths={carLen}
          color={accentColor}
          trackColor={isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.08)'}
        />
        {!!condNote && <Text style={[viz.condNote, { color: textSec }]}>{condNote}</Text>}
      </View>

      {/* ── Condition pill ── */}
      {!!condLabel && (
        <View style={[viz.condPill, { backgroundColor: `${accentColor}14`, borderColor: `${accentColor}35` }]}>
          <Text style={[viz.condText, { color: accentColor }]}>{t.condition}: {condLabel}</Text>
        </View>
      )}

    </View>
  );
});

// ─── Main panel ───────────────────────────────────────────────────────────────

export interface TrafficMathDesktopPanelProps {
  visible:  boolean;
  onClose:  () => void;
  language: string;
  colors:   {
    bg:           string;
    card:         string;
    cardBorder:   string;
    text:         string;
    textSecondary:string;
    textMuted:    string;
    accent:       string;
    accentBg:     string;
    divider:      string;
  };
  isDark:   boolean;
}

export function TrafficMathDesktopPanel({
  visible, onClose, language, colors: c, isDark,
}: TrafficMathDesktopPanelProps) {

  const t    = TR[language] ?? {};
  const lang = (['no', 'th', 'en'].includes(language) ? language : 'en') as Lang;

  // ── Input state ───────────────────────────────────────────────────────────
  const [speedText,  setSpeedText]  = useState('80');
  const [condition,  setCondition]  = useState<ConditionKey>(DEFAULT_CONDITION);
  const [followSecs, setFollowSecs] = useState<2 | 3>(2);

  const speedNum    = parseFloat(speedText) || 0;
  const condInfo    = getConditionMeta(condition);
  const accentColor = condInfo.color;

  // ── Data ─────────────────────────────────────────────────────────────────
  const { result, loading, error, isStale } = useTrafficMath(
    speedNum > 0 ? speedNum : null,
    condition,
  );

  useEffect(() => {
    if (visible) prewarmTrafficMath(condition);
  }, [visible]);

  // ── Following distance ────────────────────────────────────────────────────
  const followDist = speedNum > 0
    ? Math.round((speedNum / 3.6) * followSecs * 10) / 10
    : null;
  const followCars = followDist ? Math.round(followDist / 4.5) : 0;

  // ── Nothing to render on native or when hidden ───────────────────────────
  if (Platform.OS !== 'web' || !visible) return null;

  const overlayContent = (
    // Full-viewport overlay rendered via portal at document.body level,
    // so it is guaranteed to escape the 390 px WebAppShell overflow:hidden.
    <View style={st.overlay}>
      {/* ── Backdrop ── */}
      <Pressable style={st.backdrop} onPress={onClose}>
        {/* Stop the close event bubbling from inside the panel */}
        <Pressable
          style={[st.panel, { backgroundColor: c.bg }]}
          onPress={() => { /* absorb */ }}
        >
          {/* Subtle gradient overlay */}
          <LinearGradient
            colors={isDark
              ? ['rgba(22,40,95,0.18)', 'transparent']
              : ['rgba(244,248,253,0.6)', 'transparent']}
            style={st.panelGradient}
          />

          {/* ── Panel header ── */}
          <View style={[st.panelHeader, { borderBottomColor: c.divider }]}>
            <View style={[st.condBadge, { backgroundColor: `${accentColor}20`, borderColor: `${accentColor}40` }]}>
              <Ionicons name={condInfo.iconName as any} size={16} color={accentColor} />
            </View>
            <View style={st.panelTitleWrap}>
              <Text style={[st.panelTitle, { color: c.text }]}>{t.title}</Text>
              <Text style={[st.panelSubtitle, { color: c.textMuted }]}>{t.subtitle}</Text>
            </View>
            <TouchableOpacity
              style={[st.closeBtn, { backgroundColor: c.card, borderColor: c.cardBorder }]}
              onPress={onClose}
              activeOpacity={0.7}
            >
              <Ionicons name="close" size={20} color={c.text} />
            </TouchableOpacity>
          </View>

          {/* ── Two-column body ── */}
          <View style={st.body}>

            {/* ── LEFT COLUMN — controls + calculations ── */}
            <ScrollView
              style={[st.leftCol, { borderRightColor: c.divider }]}
              contentContainerStyle={st.leftContent}
              showsVerticalScrollIndicator={false}
              keyboardShouldPersistTaps="handled"
            >

              {/* Speed input card */}
              <View style={[st.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
                <Text style={[st.sectionLabel, { color: c.textMuted }]}>{t.speedLabel}</Text>
                <View style={st.speedRow}>
                  <TextInput
                    style={[st.speedInput, { color: c.text },
                      Platform.OS === 'web' ? ({ outlineWidth: 0 } as any) : undefined]}
                    value={speedText}
                    onChangeText={v => setSpeedText(v.replace(/[^0-9]/g, '').slice(0, 3))}
                    keyboardType="numeric"
                    maxLength={3}
                    selectTextOnFocus
                    placeholderTextColor={c.textMuted}
                    placeholder="—"
                  />
                  <Text style={[st.speedUnit, { color: c.textSecondary }]}>km/h</Text>
                  {loading && (
                    <ActivityIndicator size="small" color={accentColor} style={{ marginLeft: 8 }} />
                  )}
                </View>
                <View style={st.presetRow}>
                  {SPEED_PRESETS.map(p => {
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

              {/* Empty / offline states */}
              {!speedNum && (
                <Text style={[st.hint, { color: c.textMuted }]}>{t.emptyHint}</Text>
              )}
              {error && !result && speedNum > 0 && (
                <Text style={[st.hint, { color: c.textMuted }]}>{t.offline}</Text>
              )}

              {/* Step-by-step breakdown */}
              {result && (
                <>
                  <Text style={[st.tapHint, { color: c.textMuted }]}>{t.tapHint}</Text>
                  <View style={{ gap: 8 }}>
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

                  {/* Following distance */}
                  <View style={[st.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
                    <View style={st.followRow}>
                      <View style={{ flex: 1 }}>
                        <Text style={[st.sectionLabel, { color: c.textMuted }]}>{t.followTitle}</Text>
                        <Text style={[st.followSub, { color: c.textSecondary }]}>{t.followSub}</Text>
                      </View>
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

              <View style={{ height: 32 }} />
            </ScrollView>

            {/* ── RIGHT COLUMN — visualisation ── */}
            <ScrollView
              style={st.rightCol}
              contentContainerStyle={st.rightContent}
              showsVerticalScrollIndicator={false}
            >
              <StoppingDistanceViz
                result={result ?? null}
                accentColor={accentColor}
                textColor={c.text}
                textMuted={c.textMuted}
                textSec={c.textSecondary}
                isDark={isDark}
                lang={lang}
                t={t}
              />
              <View style={{ height: 32 }} />
            </ScrollView>

          </View>
        </Pressable>
      </Pressable>
    </View>
  );

  // Use portal to render at document.body — guaranteed to escape overflow:hidden
  if (_portal && typeof document !== 'undefined' && document.body) {
    return _portal(overlayContent, document.body);
  }
  return overlayContent;
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const st = StyleSheet.create({
  // Full-viewport overlay — position:fixed escapes overflow:hidden on the
  // 390 px WebAppShell frame and covers the entire browser viewport.
  // Using 'as any' because RN types only know 'absolute'|'relative', but
  // React Native Web passes this straight through to CSS where 'fixed' works.
  overlay: {
    position: 'fixed' as any,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 9999,
  },
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.72)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  panel: {
    width: '100%',
    maxWidth: 980,
    maxHeight: '88%' as any,
    borderRadius: 24,
    overflow: 'hidden',
    // Crisp shadow for the panel — web only
    ...(Platform.OS === 'web' ? {
      boxShadow: '0 24px 80px rgba(0,0,0,0.5), 0 8px 24px rgba(0,0,0,0.35)',
    } as any : {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 12 },
      shadowOpacity: 0.45,
      shadowRadius: 32,
      elevation: 20,
    }),
  },
  panelGradient: {
    position: 'absolute', top: 0, left: 0, right: 0, height: 120,
  },
  panelHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: StyleSheet.hairlineWidth,
    gap: 12,
  },
  condBadge: {
    width: 36, height: 36, borderRadius: 10,
    justifyContent: 'center', alignItems: 'center', borderWidth: 1,
  },
  panelTitleWrap: { flex: 1 },
  panelTitle:    { fontSize: 17, fontWeight: '800', letterSpacing: -0.3 },
  panelSubtitle: { fontSize: 12, marginTop: 1 },
  closeBtn: {
    width: 36, height: 36, borderRadius: 10,
    justifyContent: 'center', alignItems: 'center', borderWidth: 1,
  },

  body: {
    flexDirection: 'row',
    flex: 1,
    minHeight: 0,
  },

  // Left column
  leftCol:     { flex: 52, borderRightWidth: StyleSheet.hairlineWidth },
  leftContent: { padding: 16, gap: 10 },

  // Right column
  rightCol:     { flex: 48 },
  rightContent: { padding: 16 },

  card:         { borderRadius: 16, borderWidth: 1, padding: 16, gap: 10 },
  sectionLabel: { fontSize: 11, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.8 },
  speedRow:     { flexDirection: 'row', alignItems: 'baseline', gap: 4 },
  speedInput:   { fontSize: 52, fontWeight: '800', letterSpacing: -2, minWidth: 80 },
  speedUnit:    { fontSize: 20, fontWeight: '600', paddingBottom: 4 },
  presetRow:    { flexDirection: 'row', gap: 8, flexWrap: 'wrap' },
  presetChip:   { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8, borderWidth: 1 },
  presetText:   { fontSize: 13, fontWeight: '700' },
  hint:         { textAlign: 'center', fontSize: 13, paddingVertical: 24 },
  tapHint:      { fontSize: 11, textAlign: 'center' },
  followRow:    { flexDirection: 'row', alignItems: 'center', gap: 10 },
  followSub:    { fontSize: 11, marginTop: 2 },
  toggle:       { flexDirection: 'row', borderRadius: 8, padding: 3, gap: 3 },
  toggleBtn:    { paddingHorizontal: 12, paddingVertical: 5, borderRadius: 6 },
  toggleText:   { fontSize: 12, fontWeight: '600' },
  followResult: { borderTopWidth: StyleSheet.hairlineWidth, paddingTop: 10, flexDirection: 'row', alignItems: 'baseline', gap: 8 },
  followDist:   { fontSize: 28, fontWeight: '800', letterSpacing: -0.8 },
  followCars:   { fontSize: 13 },
});

// ─── Visualisation styles ─────────────────────────────────────────────────────

const viz = StyleSheet.create({
  wrap: { gap: 16, paddingTop: 4 },

  empty: { alignItems: 'center', justifyContent: 'center', paddingVertical: 80, gap: 12 },
  emptyText: { fontSize: 13, textAlign: 'center', maxWidth: 200 },

  // Speed pill
  speedPill: {
    alignSelf: 'center',
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: 6,
    paddingHorizontal: 24,
    paddingVertical: 14,
    borderRadius: 24,
    borderWidth: 1.5,
  },
  speedNum: { fontSize: 64, fontWeight: '900', letterSpacing: -3, lineHeight: 68 },
  speedUnit: { fontSize: 22, fontWeight: '600', paddingBottom: 4 },

  // Road diagram
  roadWrap: {
    height: 80,
    borderRadius: 14,
    overflow: 'hidden',
    position: 'relative',
  },
  road: {
    flex: 1,
    height: 80,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-evenly',
    paddingHorizontal: 48,
  },
  dash: {
    width: 24,
    height: 3,
    borderRadius: 2,
  },

  // Proportional distance bars — overlay on road
  bars: {
    position: 'absolute',
    left: 48,
    right: 48,
    top: 28,
    height: 24,
    flexDirection: 'row',
    borderRadius: 6,
    overflow: 'hidden',
  },
  bar: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  barLabel: {
    fontSize: 10,
    fontWeight: '800',
    color: '#fff',
    textShadowColor: 'rgba(0,0,0,0.3)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },

  // Car / stop icons at road edges
  carIcon: {
    position: 'absolute',
    left: 8,
    top: 22,
    width: 36,
    height: 36,
    borderRadius: 10,
    borderWidth: 1.5,
    justifyContent: 'center',
    alignItems: 'center',
  },
  stopIcon: {
    position: 'absolute',
    right: 8,
    top: 24,
    width: 32,
    height: 32,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },

  // Legend
  legend: { flexDirection: 'row', gap: 16, paddingHorizontal: 4 },
  legendItem: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  dot: { width: 8, height: 8, borderRadius: 4 },
  legendText: { fontSize: 12, fontWeight: '600' },

  // Total stopping distance card
  totalCard: {
    borderRadius: 16,
    borderWidth: 1,
    padding: 16,
    gap: 10,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  totalLabel: {
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 2,
  },
  totalNumRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  totalNum:  { fontSize: 52, fontWeight: '900', letterSpacing: -2, lineHeight: 56 },
  totalUnit: { fontSize: 24, fontWeight: '600' },
  carLenBlock: { alignItems: 'flex-end' },
  carLenNum: { fontSize: 32, fontWeight: '900', letterSpacing: -1 },
  carLenSub: { fontSize: 11, marginTop: 2 },
  condNote:  { fontSize: 12, lineHeight: 17 },

  // Condition pill
  condPill: {
    alignSelf: 'flex-start',
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
  },
  condText: { fontSize: 12, fontWeight: '700' },
});
