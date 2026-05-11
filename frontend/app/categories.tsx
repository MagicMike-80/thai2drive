import React, { useEffect, useRef, useState } from 'react';
import {
  View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator,
  Animated, Easing, Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useAppStore } from '../src/store/appStore';
import { api, Category } from '../src/services/api';
import { AppBrand } from '../src/components/AppBrand';

const { width: SCREEN_W } = Dimensions.get('window');

// ─── Per-category identity: subtle hue + semantic difficulty ───
type CatMeta = {
  icon: keyof typeof Ionicons.glyphMap;
  hue: string;       // accent color (used for tile + glow)
  difficulty: 1 | 2 | 3;
};
const CAT_META: Record<string, CatMeta> = {
  'Skilt':              { icon: 'warning',              hue: '#F59E0B', difficulty: 1 },
  'Trafikkregler':      { icon: 'document-text',        hue: '#3B82F6', difficulty: 2 },
  'Vikeplikt':          { icon: 'git-branch',           hue: '#A855F7', difficulty: 3 },
  'Fartsgrenser':       { icon: 'speedometer',          hue: '#F43F5E', difficulty: 1 },
  'Fart':               { icon: 'speedometer',          hue: '#F43F5E', difficulty: 1 },
  'Sikkerhet':          { icon: 'shield-checkmark',     hue: '#22C55E', difficulty: 2 },
  'Risikoforståelse':   { icon: 'alert-circle',         hue: '#06B6D4', difficulty: 2 },
  'Plassering':         { icon: 'map',                  hue: '#F97316', difficulty: 2 },
  'Nødsituasjon':       { icon: 'flash',                hue: '#EC4899', difficulty: 3 },
  'Parkering':          { icon: 'car',                  hue: '#14B8A6', difficulty: 1 },
  'Kjøreteknikk':       { icon: 'settings',             hue: '#8B5CF6', difficulty: 2 },
  'Lover og regler':    { icon: 'book',                 hue: '#0EA5E9', difficulty: 2 },
  'Miljø':              { icon: 'leaf',                 hue: '#10B981', difficulty: 1 },
};

const TR: Record<string, Record<string, any>> = {
  no: {
    selectCategory: 'Velg kategori', allCategories: 'Alle kategorier',
    practice: 'Øvingsmodus', exam: 'Eksamensmodus',
    allCategoriesSub: 'Alt samlet · beste for full repetisjon',
    completed: 'fullført',
    easy: 'Lett', medium: 'Middels', hard: 'Vanskelig',
    categories: {
      'Skilt': 'Trafikkskilt', 'Trafikkregler': 'Trafikkregler', 'Vikeplikt': 'Vikeplikt',
      'Fartsgrenser': 'Fartsgrenser', 'Fart': 'Fart', 'Sikkerhet': 'Sikkerhet',
      'Risikoforståelse': 'Risikoforståelse', 'Plassering': 'Plassering',
      'Nødsituasjon': 'Nødsituasjon', 'Parkering': 'Parkering',
      'Kjøreteknikk': 'Kjøreteknikk', 'Lover og regler': 'Lover og regler', 'Miljø': 'Miljø',
    },
  },
  th: {
    selectCategory: 'เลือกหมวดหมู่', allCategories: 'ทุกหมวดหมู่',
    practice: 'โหมดฝึกซ้อม', exam: 'โหมดสอบ',
    allCategoriesSub: 'รวมทุกหมวด · เหมาะสำหรับทบทวน',
    completed: 'สำเร็จ',
    easy: 'ง่าย', medium: 'ปานกลาง', hard: 'ยาก',
    categories: {
      'Skilt': 'ป้ายจราจร', 'Trafikkregler': 'กฎจราจร', 'Vikeplikt': 'การให้ทาง',
      'Fartsgrenser': 'ขีดจำกัดความเร็ว', 'Fart': 'ความเร็ว', 'Sikkerhet': 'ความปลอดภัย',
      'Risikoforståelse': 'การรับรู้ความเสี่ยง', 'Plassering': 'การวางตำแหน่ง',
      'Nødsituasjon': 'เหตุฉุกเฉิน', 'Parkering': 'การจอดรถ',
      'Kjøreteknikk': 'เทคนิคการขับขี่', 'Lover og regler': 'กฎหมายและระเบียบ', 'Miljø': 'สิ่งแวดล้อม',
    },
  },
  en: {
    selectCategory: 'Select Category', allCategories: 'All Categories',
    practice: 'Practice Mode', exam: 'Exam Mode',
    allCategoriesSub: 'Everything mixed · best for full review',
    completed: 'completed',
    easy: 'Easy', medium: 'Medium', hard: 'Hard',
    categories: {
      'Skilt': 'Traffic Signs', 'Trafikkregler': 'Road Rules', 'Vikeplikt': 'Right of Way',
      'Fartsgrenser': 'Speed Limits', 'Fart': 'Speed', 'Sikkerhet': 'Safety',
      'Risikoforståelse': 'Risk Awareness', 'Plassering': 'Positioning',
      'Nødsituasjon': 'Emergency', 'Parkering': 'Parking',
      'Kjøreteknikk': 'Driving Technique', 'Lover og regler': 'Laws & Rules', 'Miljø': 'Environment',
    },
  },
};

// ─── Pressable card with spring-scale micro-interaction ───
function PressableCard({ children, onPress, style, testID }: any) {
  const scale = useRef(new Animated.Value(1)).current;
  const glow = useRef(new Animated.Value(0)).current;

  const pressIn = () => {
    Animated.parallel([
      Animated.spring(scale, { toValue: 0.97, useNativeDriver: true, speed: 50, bounciness: 0 }),
      Animated.timing(glow, { toValue: 1, duration: 140, useNativeDriver: true, easing: Easing.out(Easing.quad) }),
    ]).start();
  };
  const pressOut = () => {
    Animated.parallel([
      Animated.spring(scale, { toValue: 1, useNativeDriver: true, speed: 30, bounciness: 6 }),
      Animated.timing(glow, { toValue: 0, duration: 260, useNativeDriver: true, easing: Easing.out(Easing.quad) }),
    ]).start();
  };

  return (
    <Pressable testID={testID} onPress={onPress} onPressIn={pressIn} onPressOut={pressOut}>
      <Animated.View style={[style, { transform: [{ scale }] }]}>
        {children}
        <Animated.View
          pointerEvents="none"
          style={[StyleSheet.absoluteFill, {
            borderRadius: 20,
            backgroundColor: 'rgba(255,255,255,0.08)',
            opacity: glow,
          }]}
        />
      </Animated.View>
    </Pressable>
  );
}

export default function CategoriesScreen() {
  const router = useRouter();
  const { mode } = useLocalSearchParams<{ mode: string }>();
  const { language, colors, progress } = useAppStore();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const t = TR[language] || TR.en;
  const c = colors;
  const isDark = c.bg === '#0F172A' || c.bg === '#0B1222';

  useEffect(() => {
    api.getCategories().then(setCategories).catch(console.error).finally(() => setLoading(false));
  }, []);

  const startQuiz = (cat?: string) => router.push({ pathname: '/quiz', params: { mode, category: cat || 'all' } });

  // Progress per category (0-100). Uses store.progress.questions_by_category.
  const pct = (catName: string, total: number) => {
    const stat = progress.questions_by_category?.[catName];
    if (!stat || stat.answered === 0 || total === 0) return 0;
    return Math.min(100, Math.round((stat.answered / total) * 100));
  };

  // Overall progress for "All categories" card
  const overallPct = (() => {
    const totalQuestions = categories.reduce((s, x) => s + x.count, 0);
    return totalQuestions === 0 ? 0 : Math.min(100, Math.round((progress.total_questions_answered / totalQuestions) * 100));
  })();

  const diffLabel = (d: 1 | 2 | 3) => d === 1 ? t.easy : d === 2 ? t.medium : t.hard;
  const diffColor = (d: 1 | 2 | 3) => d === 1 ? c.correct : d === 2 ? c.accent : c.incorrect;

  if (loading) return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <View style={st.center}><ActivityIndicator size="large" color={c.accent} /></View>
    </SafeAreaView>
  );

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      {/* Dark gradient background (subtle, not flat) */}
      <LinearGradient
        colors={isDark ? ['#0B1222', '#0F172A', '#0B1222'] : ['#F8FAFC', '#FFFFFF', '#F1F5F9']}
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
        <View style={{ marginRight: 12 }}>
          <AppBrand size="md" />
        </View>
        <View style={{ flex: 1 }}>
          <Text style={[st.modeLabel, { color: c.accent }]}>{mode === 'practice' ? t.practice : t.exam}</Text>
          <Text style={[st.title, { color: c.text }]}>{t.selectCategory}</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={st.scroll} showsVerticalScrollIndicator={false}>
        {/* ── ALL CATEGORIES — primary featured card ── */}
        <PressableCard
          testID="all-categories-btn"
          onPress={() => startQuiz()}
          style={[st.allCard, { borderColor: `${c.accent}55`, shadowColor: c.accent }]}
        >
          <LinearGradient
            colors={[`${c.accent}20`, `${c.accent}08`, 'transparent']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={StyleSheet.absoluteFill}
          />
          <View style={st.allRow}>
            <View style={[st.allIcon, { backgroundColor: `${c.accent}1A`, borderColor: `${c.accent}50` }]}>
              <Ionicons name="sparkles" size={26} color={c.accent} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={[st.allTitle, { color: c.text }]}>{t.allCategories}</Text>
              <Text style={[st.allSub, { color: c.textSecondary }]} numberOfLines={1}>{t.allCategoriesSub}</Text>
            </View>
            <View style={[st.chevronPill, { backgroundColor: c.accent }]}>
              <Ionicons name="play" size={14} color="#0F172A" />
            </View>
          </View>
          {/* Overall progress bar */}
          <View style={st.allProgressWrap}>
            <View style={[st.progressTrack, { backgroundColor: `${c.textMuted}25` }]}>
              <View style={[st.progressFill, { width: `${overallPct}%`, backgroundColor: c.accent }]} />
            </View>
            <Text style={[st.progressPct, { color: c.textSecondary }]}>{overallPct}% {t.completed}</Text>
          </View>
        </PressableCard>

        {/* ── CATEGORY GRID ── */}
        <View style={st.grid}>
          {categories.map((cat) => {
            const meta = CAT_META[cat.name] || { icon: 'help-circle' as const, hue: c.accent, difficulty: 2 as const };
            const name = (t.categories as any)[cat.name] || cat.name;
            const completion = pct(cat.name, cat.count);

            return (
              <PressableCard
                key={cat.name}
                testID={`category-${cat.name}`}
                onPress={() => startQuiz(cat.name)}
                style={[st.catCard, { borderColor: `${meta.hue}33`, shadowColor: meta.hue }]}
              >
                {/* Subtle diagonal gradient giving each card its own hue */}
                <LinearGradient
                  colors={[`${meta.hue}22`, `${meta.hue}0A`, 'transparent']}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                  style={StyleSheet.absoluteFill}
                />
                {/* Top-right glow blob */}
                <View style={[st.glowBlob, { backgroundColor: `${meta.hue}1F` }]} pointerEvents="none" />

                <View style={[st.catIcon, { backgroundColor: `${meta.hue}1F`, borderColor: `${meta.hue}55` }]}>
                  <Ionicons name={meta.icon} size={22} color={meta.hue} />
                </View>

                <Text style={[st.catName, { color: c.text }]} numberOfLines={2}>{name}</Text>

                {/* Difficulty row */}
                <View style={st.diffRow}>
                  <View style={st.starsWrap}>
                    {[1, 2, 3].map((i) => (
                      <Ionicons
                        key={i}
                        name="star"
                        size={9}
                        color={i <= meta.difficulty ? diffColor(meta.difficulty) : `${c.textMuted}40`}
                        style={{ marginRight: 2 }}
                      />
                    ))}
                  </View>
                  <Text style={[st.diffLabel, { color: diffColor(meta.difficulty) }]}>
                    {diffLabel(meta.difficulty)}
                  </Text>
                </View>

                {/* Progress bar at the bottom */}
                <View style={st.catProgressWrap}>
                  <View style={[st.progressTrack, { backgroundColor: `${c.textMuted}22` }]}>
                    <View style={[st.progressFill, { width: `${completion}%`, backgroundColor: meta.hue }]} />
                  </View>
                  {completion > 0 && (
                    <Text style={[st.catProgressPct, { color: c.textMuted }]}>{completion}%</Text>
                  )}
                </View>
              </PressableCard>
            );
          })}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const CARD_W = (SCREEN_W - 16 * 2 - 12) / 2; // padding + gap

const st = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },

  header: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 16, paddingVertical: 14,
    borderBottomWidth: 1,
  },
  backBtn: {
    width: 40, height: 40, borderRadius: 12,
    justifyContent: 'center', alignItems: 'center',
    marginRight: 14, borderWidth: 1,
  },
  modeLabel: { fontSize: 11, textTransform: 'uppercase', letterSpacing: 1.5, fontWeight: '800' },
  title: { fontSize: 22, fontWeight: '800', marginTop: 3, letterSpacing: -0.4 },

  scroll: { padding: 16, paddingTop: 18, paddingBottom: 40 },

  // All categories featured card
  allCard: {
    borderRadius: 20, padding: 18, marginBottom: 20,
    borderWidth: 1.5, overflow: 'hidden',
    shadowOpacity: 0.25, shadowRadius: 12, shadowOffset: { width: 0, height: 4 }, elevation: 6,
  },
  allRow: { flexDirection: 'row', alignItems: 'center' },
  allIcon: {
    width: 56, height: 56, borderRadius: 16,
    justifyContent: 'center', alignItems: 'center',
    marginRight: 16, borderWidth: 1.5,
  },
  allTitle: { fontSize: 19, fontWeight: '800', letterSpacing: -0.3 },
  allSub: { fontSize: 12, marginTop: 3, opacity: 0.8 },
  chevronPill: {
    width: 36, height: 36, borderRadius: 18,
    justifyContent: 'center', alignItems: 'center', marginLeft: 8,
  },
  allProgressWrap: { marginTop: 14 },

  // Grid cards
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  catCard: {
    width: CARD_W, minHeight: 172,
    borderRadius: 20, padding: 16,
    borderWidth: 1.5, overflow: 'hidden',
    shadowOpacity: 0.18, shadowRadius: 10, shadowOffset: { width: 0, height: 3 }, elevation: 4,
  },
  glowBlob: {
    position: 'absolute', top: -30, right: -30,
    width: 110, height: 110, borderRadius: 55,
    opacity: 0.7,
  },
  catIcon: {
    width: 44, height: 44, borderRadius: 14,
    justifyContent: 'center', alignItems: 'center',
    marginBottom: 12, borderWidth: 1.5,
  },
  catName: { fontSize: 15, fontWeight: '800', lineHeight: 20, marginBottom: 10, letterSpacing: -0.1 },

  diffRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  starsWrap: { flexDirection: 'row', marginRight: 8 },
  diffLabel: { fontSize: 10, fontWeight: '700', letterSpacing: 0.5, textTransform: 'uppercase' },

  catProgressWrap: { marginTop: 'auto' },
  catProgressPct: { fontSize: 10, fontWeight: '700', marginTop: 4, textAlign: 'right' },

  progressTrack: { height: 4, borderRadius: 2, overflow: 'hidden' },
  progressFill: { height: '100%', borderRadius: 2 },
  progressPct: { fontSize: 11, fontWeight: '600', marginTop: 6 },
});
