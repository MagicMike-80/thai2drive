/**
 * AI Learning Dashboard — Thai2Drive
 *
 * Shows:
 *   • Exam readiness score (large prominent %)
 *   • Category accuracy bars
 *   • Coaching messages
 *   • SRS (spaced repetition) queue info
 *   • Improvement trend indicator
 *   • "Start Smart Practice" CTA
 */
import React, { useEffect, useState, useRef } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, Animated,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { aiLearningApi, AIDashboard, CategoryStat } from '../src/services/aiLearning';
import { AppBrand } from '../src/components/AppBrand';
import { Lang, asLang, tr, missingNotice } from '../src/constants/i18n';
import { categoryLabel, localizeCategoryMentions } from '../src/constants/categoryLabels';

// ─── Translations ─────────────────────────────────────────────────────────────
// Fail-Stop: mangler en nøkkel på elevens språk, skjules elementet (eller vi
// viser `missingNotice`). Ingen fallback til norsk/engelsk. Se src/constants/i18n.ts.
const TR: Record<Lang, Record<string, string>> = {
  no: {
    title:          'AI Læringsanalyse',
    back:           'Tilbake',
    readiness:      'Eksamensklarhet',
    readinessHint:  'Basert på dine siste svar',
    excellent:      'Eksamensmoden!',
    good:           'Nesten klar!',
    fair:           'God fremgang',
    needsWork:      'Fortsett å øve',
    categories:     'Kategorier',
    weakCategory:   'Svakest',
    strongCategory: 'Sterkest',
    coaching:       'AI Lærer',
    srsSection:     'Planlagt repetisjon',
    srsReady:       'spørsmål klare for repetisjon',
    srsNone:        'Ingen spørsmål klare for repetisjon nå.',
    smartPractice:  'Start Smart Øving',
    totalAnswered:  'Besvart totalt',
    recentAccuracy: 'Nylig nøyaktighet',
    trend:          'Trend',
    improving:      '↑ Forbedring',
    stable:         '→ Stabil',
    declining:      '↓ Nedgang',
    noData:         'Svar på noen spørsmål for å se læringsanalysen din.',
    correct:        'riktige',
    questions:      'spørsmål',
  },
  th: {
    title:          'การวิเคราะห์การเรียนรู้ AI',
    back:           'กลับ',
    readiness:      'ความพร้อมสอบ',
    readinessHint:  'อ้างอิงจากคำตอบล่าสุดของคุณ',
    excellent:      'พร้อมสอบแล้ว!',
    good:           'ใกล้พร้อมแล้ว!',
    fair:           'ก้าวหน้าดี',
    needsWork:      'ฝึกต่อไปนะ',
    categories:     'หมวดหมู่',
    weakCategory:   'อ่อนที่สุด',
    strongCategory: 'แข็งที่สุด',
    coaching:       'AI ครู',
    srsSection:     'การทบทวนแบบเว้นระยะ',
    srsReady:       'คำถามรอทบทวน',
    srsNone:        'ยังไม่มีคำถามรอทบทวนตอนนี้',
    smartPractice:  'เริ่มการฝึกอัจฉริยะ',
    totalAnswered:  'ตอบทั้งหมด',
    recentAccuracy: 'ความแม่นยำล่าสุด',
    trend:          'แนวโน้ม',
    improving:      '↑ กำลังพัฒนา',
    stable:         '→ คงที่',
    declining:      '↓ ลดลง',
    noData:         'ตอบคำถามสักหน่อยเพื่อดูการวิเคราะห์ของคุณ',
    correct:        'ถูก',
    questions:      'คำถาม',
  },
  en: {
    title:          'AI Learning Insights',
    back:           'Back',
    readiness:      'Exam Readiness',
    readinessHint:  'Based on your recent answers',
    excellent:      'Exam-Ready!',
    good:           'Almost there!',
    fair:           'Good progress',
    needsWork:      'Keep practicing',
    categories:     'Categories',
    weakCategory:   'Weakest',
    strongCategory: 'Strongest',
    coaching:       'AI Coach',
    srsSection:     'Spaced Repetition',
    srsReady:       'questions ready for review',
    srsNone:        'No questions due for review right now.',
    smartPractice:  'Start Smart Practice',
    totalAnswered:  'Total answered',
    recentAccuracy: 'Recent accuracy',
    trend:          'Trend',
    improving:      '↑ Improving',
    stable:         '→ Stable',
    declining:      '↓ Declining',
    noData:         'Answer some questions to see your learning insights.',
    correct:        'correct',
    questions:      'questions',
  },
};

// ─── Helpers ──────────────────────────────────────────────────────────────────
function readinessLabel(score: number, t: Record<string, string>): string | null {
  if (score >= 85) return tr(t, 'excellent');
  if (score >= 70) return tr(t, 'good');
  if (score >= 55) return tr(t, 'fair');
  return tr(t, 'needsWork');
}

function readinessColor(score: number): string {
  if (score >= 85) return '#10B981';
  if (score >= 70) return '#F59E0B';
  if (score >= 55) return '#3B82F6';
  return '#EF4444';
}

function trendIcon(trend: string): keyof typeof Ionicons.glyphMap {
  if (trend === 'improving') return 'trending-up';
  if (trend === 'declining') return 'trending-down';
  return 'remove-outline';
}

function trendColor(trend: string, c: any): string {
  if (trend === 'improving') return c.correct;
  if (trend === 'declining') return c.incorrect;
  return c.textMuted;
}

// ─── Category Bar ─────────────────────────────────────────────────────────────
function CategoryBar({
  stat, lang, colors: c
}: { stat: CategoryStat; lang: Lang; colors: any }) {
  const barAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(barAnim, {
      toValue: stat.accuracy / 100,
      duration: 600,
      useNativeDriver: false,
    }).start();
  }, [stat.accuracy]);

  // Fail-Stop: har vi ikke kategorinavnet på elevens språk, viser vi ingenting
  // heller enn den rå databasenøkkelen ('Right of Way', 'fart_og_bremsing').
  const name = categoryLabel(stat.category, lang);
  if (!name) return null;

  const barColor =
    stat.accuracy >= 80 ? '#10B981' :
    stat.accuracy >= 60 ? '#F59E0B' : '#EF4444';

  return (
    <View style={catStyles.row}>
      <Text style={[catStyles.name, { color: c.text }]} numberOfLines={1}>
        {name}
      </Text>
      <View style={[catStyles.track, { backgroundColor: c.progressBg }]}>
        <Animated.View
          style={[
            catStyles.fill,
            {
              backgroundColor: barColor,
              width: barAnim.interpolate({ inputRange: [0, 1], outputRange: ['0%', '100%'] }),
            },
          ]}
        />
      </View>
      <Text style={[catStyles.pct, { color: barColor }]}>
        {Math.round(stat.accuracy)}%
      </Text>
    </View>
  );
}

const catStyles = StyleSheet.create({
  row:   { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 10 },
  name:  { width: 110, fontSize: 12, fontWeight: '600' },
  track: { flex: 1, height: 8, borderRadius: 4, overflow: 'hidden' },
  fill:  { height: '100%', borderRadius: 4 },
  pct:   { width: 38, fontSize: 12, fontWeight: '700', textAlign: 'right' },
});

// ─── Main Screen ──────────────────────────────────────────────────────────────
export default function AIDashboardScreen() {
  const router = useRouter();
  const { language, colors: c, deviceId, streak } = useAppStore();
  const lang = asLang(language);
  const t = TR[lang];
  const isDark = c.bg === '#0F172A' || c.bg === '#0B1222';

  // Thai skrives ikke med versaler, og letterSpacing river fra hverandre
  // kombinerende tegn — derfor kun på latinsk skrift.
  const capStyle = lang === 'th'
    ? { textTransform: 'none' as const, letterSpacing: 0 }
    : null;

  const [loading, setLoading]   = useState(true);
  const [data, setData]         = useState<AIDashboard | null>(null);
  const scaleAnim = useRef(new Animated.Value(0.8)).current;

  useEffect(() => {
    (async () => {
      const d = await aiLearningApi.getDashboard(deviceId, language, streak);
      setData(d);
      setLoading(false);
      Animated.spring(scaleAnim, {
        toValue: 1, speed: 12, bounciness: 6, useNativeDriver: true,
      }).start();
    })();
  }, [deviceId, language, streak]);

  // Rå kategorinøkler fra databasen oversettes her — aldri i JSX.
  const strongestLabel = categoryLabel(data?.strongest_category, lang);
  const weakestLabel   = categoryLabel(data?.weakest_category, lang);

  // Backend interpolerer rå kategorinavn inn i coaching-setningene
  // ('คุณยังอ่อนในหมวด: Right of Way'). Vi bytter dem ut lokalt og forkaster
  // meldinger som fortsatt ikke er rene på elevens språk.
  const coachingMessages = (data?.coaching_messages ?? [])
    .map((msg) => localizeCategoryMentions(msg, lang, data?.all_categories ?? []))
    .filter((msg): msg is string => msg !== null);

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <LinearGradient
        colors={isDark ? ['#0B1222', '#0F172A', '#0B1222'] : ['#F4F8FD', '#FFFFFF', '#EEF5FB']}
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />

      {/* Header */}
      <View style={[st.header, { borderBottomColor: c.divider }]}>
        <TouchableOpacity
          style={[st.backBtn, { backgroundColor: c.card }]}
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={20} color={c.text} />
        </TouchableOpacity>
        <AppBrand size="md" />
        <View style={{ width: 40 }} />
      </View>

      {loading ? (
        <View style={st.center}>
          <ActivityIndicator size="large" color={c.accent} />
        </View>
      ) : !data || data.total_attempts < 3 ? (
        /* No data yet */
        <View style={st.center}>
          <Ionicons name="analytics-outline" size={48} color={c.textMuted} />
          <Text style={[st.noDataTxt, { color: c.textMuted }]}>
            {tr(t, 'noData') ?? missingNotice(lang)}
          </Text>
        </View>
      ) : (
        <ScrollView contentContainerStyle={st.scroll} showsVerticalScrollIndicator={false}>

          {/* ── Exam Readiness Hero ── */}
          <Animated.View style={[st.heroCard, { transform: [{ scale: scaleAnim }] }]}>
            <View style={[
              st.readinessRing,
              { borderColor: readinessColor(data.exam_readiness) },
            ]}>
              <Text style={[st.readinessNum, { color: readinessColor(data.exam_readiness) }]}>
                {data.exam_readiness}%
              </Text>
            </View>
            <Text style={[st.readinessLabel, { color: c.text }]}>
              {tr(t, 'readiness') ?? missingNotice(lang)}
            </Text>
            {readinessLabel(data.exam_readiness, t) && (
              <Text style={[st.readinessDesc, { color: readinessColor(data.exam_readiness) }]}>
                {readinessLabel(data.exam_readiness, t)}
              </Text>
            )}
            {tr(t, 'readinessHint') && (
              <Text style={[st.readinessHint, { color: c.textMuted }]}>
                {tr(t, 'readinessHint')}
              </Text>
            )}
          </Animated.View>

          {/* ── Quick Stats Row ── */}
          {/* Hver kolonne skjules i sin helhet hvis tittelen mangler på elevens
              språk — et tall uten forståelig etikett hjelper ingen. */}
          <View style={[st.statsRow, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            {tr(t, 'totalAnswered') && (
              <View style={st.statCol}>
                <Text style={[st.statVal, { color: c.text }]}>{data.total_attempts}</Text>
                <Text style={[st.statLbl, capStyle, { color: c.textMuted }]}>
                  {tr(t, 'totalAnswered')}
                </Text>
              </View>
            )}
            <View style={[st.statDiv, { backgroundColor: c.divider }]} />
            {tr(t, 'recentAccuracy') && (
              <View style={st.statCol}>
                <Text style={[st.statVal, { color: c.accent }]}>{data.recent_accuracy}%</Text>
                <Text style={[st.statLbl, capStyle, { color: c.textMuted }]}>
                  {tr(t, 'recentAccuracy')}
                </Text>
              </View>
            )}
            <View style={[st.statDiv, { backgroundColor: c.divider }]} />
            {tr(t, 'trend') && (
              <View style={st.statCol}>
                <View style={st.trendRow}>
                  <Ionicons
                    name={trendIcon(data.trend)}
                    size={18}
                    color={trendColor(data.trend, c)}
                  />
                </View>
                <Text style={[st.statLbl, capStyle, { color: c.textMuted }]}>
                  {tr(t, 'trend')}
                </Text>
                {tr(t, data.trend) && (
                  <Text style={[st.trendTxt, { color: trendColor(data.trend, c) }]}>
                    {tr(t, data.trend)}
                  </Text>
                )}
              </View>
            )}
          </View>

          {/* ── Strongest / Weakest ── */}
          {/* Vises kun når både overskriften og kategorinavnet finnes på
              elevens språk. Ellers skjules raden (Fail-Stop). */}
          {((strongestLabel && tr(t, 'strongCategory')) || (weakestLabel && tr(t, 'weakCategory'))) && (
            <View style={[st.section, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
              {strongestLabel && tr(t, 'strongCategory') && (
                <View style={st.keyRow}>
                  <Ionicons name="trophy-outline" size={18} color="#10B981" />
                  <View style={{ flex: 1 }}>
                    <Text style={[st.keyLabel, capStyle, { color: c.textMuted }]}>
                      {tr(t, 'strongCategory')}
                    </Text>
                    <Text style={[st.keyVal, { color: c.text }]}>{strongestLabel}</Text>
                  </View>
                </View>
              )}
              {weakestLabel && tr(t, 'weakCategory') && (
                <View style={[st.keyRow, { marginTop: strongestLabel ? 10 : 0 }]}>
                  <Ionicons name="alert-circle-outline" size={18} color="#EF4444" />
                  <View style={{ flex: 1 }}>
                    <Text style={[st.keyLabel, capStyle, { color: c.textMuted }]}>
                      {tr(t, 'weakCategory')}
                    </Text>
                    <Text style={[st.keyVal, { color: c.text }]}>{weakestLabel}</Text>
                  </View>
                </View>
              )}
            </View>
          )}

          {/* ── Category Breakdown ── */}
          {data.category_stats.length > 0 && tr(t, 'categories') && (
            <View style={[st.section, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
              <View style={st.sectionHeader}>
                <Ionicons name="bar-chart-outline" size={18} color={c.accent} />
                <Text style={[st.sectionTitle, { color: c.text }]}>{tr(t, 'categories')}</Text>
              </View>
              {data.category_stats.map((stat) => (
                <CategoryBar key={stat.category} stat={stat} lang={lang} colors={c} />
              ))}
            </View>
          )}

          {/* ── AI Coaching Messages ── */}
          {coachingMessages.length > 0 && tr(t, 'coaching') && (
            <View style={[st.section, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
              <View style={st.sectionHeader}>
                <Ionicons name="sparkles" size={18} color={c.accent} />
                <Text style={[st.sectionTitle, { color: c.text }]}>{tr(t, 'coaching')}</Text>
              </View>
              {coachingMessages.map((msg, i) => (
                <View key={i} style={[st.coachRow, { borderLeftColor: c.accent }]}>
                  <Text style={[st.coachMsg, { color: c.textSecondary }]}>{msg}</Text>
                </View>
              ))}
            </View>
          )}

          {/* ── SRS Queue ── */}
          {tr(t, 'srsSection') && (
            <View style={[st.section, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
              <View style={st.sectionHeader}>
                <Ionicons name="repeat-outline" size={18} color={c.accent} />
                <Text style={[st.sectionTitle, { color: c.text }]}>{tr(t, 'srsSection')}</Text>
              </View>
              {data.srs_due_count > 0 ? (
                <View style={st.srsRow}>
                  <View style={[st.srsBadge, { backgroundColor: `${c.accent}18` }]}>
                    <Text style={[st.srsBadgeNum, { color: c.accent }]}>{data.srs_due_count}</Text>
                  </View>
                  <Text style={[st.srsTxt, { color: c.textSecondary }]}>
                    {tr(t, 'srsReady') ?? missingNotice(lang)}
                  </Text>
                </View>
              ) : (
                <Text style={[st.srsNone, { color: c.textMuted }]}>
                  {tr(t, 'srsNone') ?? missingNotice(lang)}
                </Text>
              )}
            </View>
          )}

          {/* ── Smart Practice CTA ── */}
          {/* En knapp uten forståelig tekst er verre enn ingen knapp. */}
          {tr(t, 'smartPractice') && (
            <TouchableOpacity
              style={[st.ctaBtn, { backgroundColor: c.accent }]}
              onPress={() => router.push({ pathname: '/quiz', params: { mode: 'smart', category: 'all' } })}
              activeOpacity={0.85}
            >
              <Ionicons name="flash" size={20} color="#0F172A" />
              <Text style={st.ctaTxt}>{tr(t, 'smartPractice')}</Text>
            </TouchableOpacity>
          )}

        </ScrollView>
      )}
    </SafeAreaView>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────
const st = StyleSheet.create({
  container: { flex: 1 },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1,
  },
  backBtn: { width: 40, height: 40, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  center:  { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 16, paddingHorizontal: 32 },
  noDataTxt: { fontSize: 15, textAlign: 'center', lineHeight: 22, marginTop: 8 },
  scroll:  { padding: 16, gap: 12, paddingBottom: 40 },

  heroCard: { alignItems: 'center', paddingVertical: 24, gap: 6 },
  readinessRing: {
    width: 130, height: 130, borderRadius: 65, borderWidth: 6,
    justifyContent: 'center', alignItems: 'center', marginBottom: 4,
  },
  readinessNum:  { fontSize: 40, fontWeight: '900', letterSpacing: -1 },
  readinessLabel:{ fontSize: 16, fontWeight: '700' },
  readinessDesc: { fontSize: 18, fontWeight: '800' },
  readinessHint: { fontSize: 12, marginTop: 2 },

  statsRow: {
    flexDirection: 'row', alignItems: 'center', borderRadius: 16,
    borderWidth: 1, paddingVertical: 14,
  },
  statCol:  { flex: 1, alignItems: 'center' },
  statVal:  { fontSize: 22, fontWeight: '800' },
  statLbl:  { fontSize: 11, marginTop: 3, textTransform: 'uppercase', letterSpacing: 0.6 },
  statDiv:  { width: 1, height: 36 },
  trendRow: { alignItems: 'center', marginBottom: 2 },
  trendTxt: { fontSize: 11, fontWeight: '700', marginTop: 2 },

  section: { borderRadius: 16, padding: 16, borderWidth: 1, gap: 0 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 14 },
  sectionTitle: { fontSize: 15, fontWeight: '700' },

  keyRow:   { flexDirection: 'row', alignItems: 'flex-start', gap: 10 },
  keyLabel: { fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.6, marginBottom: 2 },
  keyVal:   { fontSize: 14, fontWeight: '700' },

  coachRow: { borderLeftWidth: 3, paddingLeft: 12, marginBottom: 10 },
  coachMsg: { fontSize: 14, lineHeight: 20 },

  srsRow:     { flexDirection: 'row', alignItems: 'center', gap: 12 },
  srsBadge:   { width: 48, height: 48, borderRadius: 14, justifyContent: 'center', alignItems: 'center' },
  srsBadgeNum:{ fontSize: 22, fontWeight: '900' },
  srsTxt:     { flex: 1, fontSize: 14 },
  srsNone:    { fontSize: 13, fontStyle: 'italic' },

  ctaBtn: {
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center',
    borderRadius: 16, paddingVertical: 18, gap: 10, marginTop: 4,
  },
  ctaTxt: { fontSize: 17, fontWeight: '800', color: '#0F172A' },
});
