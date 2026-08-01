import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import {
  View, Text, StyleSheet, Pressable, ActivityIndicator,
  Animated, Easing, Dimensions, PanResponder, Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useAppStore } from '../src/store/appStore';
import { api, Category } from '../src/services/api';
import { AppBrand } from '../src/components/AppBrand';
import { BottomNavBar } from '../src/components/BottomNavBar';

const { width: SCREEN_W } = Dimensions.get('window');

// ─── 3D Carousel dimensions (matches webapp.py) ───
const CARD_W = 155;
const CARD_H = 200;
const SPACING = 72;
const DRAG_THRESHOLD = 85; // px per index step
const ANGLE_STEP = 48;     // degrees per item offset

// ─── Per-category neon color themes (from webapp.py lines 786-828) ───
interface CatColor {
  color: string;
  glow: string;
  bg1: string;
  bg2: string;
}

const CAT_COLORS: Record<string, CatColor> = {
  '__all__':               { color: '#00F5FF', glow: 'rgba(0,245,255,.45)', bg1: 'rgba(0,20,35,.95)',  bg2: 'rgba(0,8,16,.99)' },
  'Speed Limits':          { color: '#FF6A00', glow: 'rgba(255,106,0,.50)', bg1: 'rgba(50,15,0,.95)',  bg2: 'rgba(20,5,0,.99)' },
  'Road Rules':            { color: '#FF4500', glow: 'rgba(255,69,0,.48)',  bg1: 'rgba(45,10,0,.95)',  bg2: 'rgba(18,4,0,.99)' },
  'Traffic Signs':         { color: '#FFD700', glow: 'rgba(255,215,0,.48)', bg1: 'rgba(40,30,0,.95)',  bg2: 'rgba(15,12,0,.99)' },
  'Right of Way':          { color: '#AAFF00', glow: 'rgba(170,255,0,.48)', bg1: 'rgba(12,32,0,.95)',  bg2: 'rgba(4,14,0,.99)' },
  'Traffic Rules':         { color: '#CC44FF', glow: 'rgba(204,68,255,.48)',bg1: 'rgba(28,5,40,.95)',  bg2: 'rgba(10,0,18,.99)' },
  'Situations':            { color: '#00FF6A', glow: 'rgba(0,255,106,.45)', bg1: 'rgba(0,30,12,.95)',  bg2: 'rgba(0,12,5,.99)' },
  'Safety':                { color: '#00AAFF', glow: 'rgba(0,170,255,.48)', bg1: 'rgba(0,18,40,.95)',  bg2: 'rgba(0,6,18,.99)' },
  'Driving Conditions':    { color: '#00C8FF', glow: 'rgba(0,200,255,.45)', bg1: 'rgba(0,20,35,.95)',  bg2: 'rgba(0,8,16,.99)' },
  'Road Conditions':       { color: '#00C8FF', glow: 'rgba(0,200,255,.45)', bg1: 'rgba(0,20,35,.95)',  bg2: 'rgba(0,8,16,.99)' },
  'Pedestrians and Cyclists': { color: '#FF9800', glow: 'rgba(255,152,0,.48)', bg1: 'rgba(40,20,0,.95)',  bg2: 'rgba(16,7,0,.99)' },
  'Vehicle Knowledge':     { color: '#4FC3F7', glow: 'rgba(79,195,247,.42)',bg1: 'rgba(0,18,30,.95)',  bg2: 'rgba(0,6,14,.99)' },
  'Environment and Economy': { color: '#00E676', glow: 'rgba(0,230,118,.45)',bg1: 'rgba(0,26,14,.95)',  bg2: 'rgba(0,10,5,.99)' },
  'Alcohol':               { color: '#FF3D71', glow: 'rgba(255,61,113,.45)',bg1: 'rgba(40,0,12,.95)',  bg2: 'rgba(16,0,5,.99)' },
  'Highway':               { color: '#00E5FF', glow: 'rgba(0,229,255,.45)', bg1: 'rgba(0,22,32,.95)',  bg2: 'rgba(0,8,14,.99)' },
  'Overtaking':            { color: '#00FF80', glow: 'rgba(0,255,128,.45)', bg1: 'rgba(0,28,14,.95)',  bg2: 'rgba(0,10,5,.99)' },
  'Intersections':         { color: '#FF8C00', glow: 'rgba(255,140,0,.48)', bg1: 'rgba(42,18,0,.95)',  bg2: 'rgba(16,6,0,.99)' },
  'Parking':               { color: '#00E5FF', glow: 'rgba(0,229,255,.42)', bg1: 'rgba(0,20,30,.95)',  bg2: 'rgba(0,7,12,.99)' },
  'Lights':                { color: '#FFE033', glow: 'rgba(255,224,51,.45)', bg1: 'rgba(38,28,0,.95)',  bg2: 'rgba(14,10,0,.99)' },
  'Tires':                 { color: '#B0C4DE', glow: 'rgba(176,196,222,.38)',bg1: 'rgba(12,16,22,.95)',bg2: 'rgba(4,6,10,.99)' },
  'Pedestrians':           { color: '#FF9800', glow: 'rgba(255,152,0,.48)', bg1: 'rgba(40,20,0,.95)',  bg2: 'rgba(16,7,0,.99)' },
  'Environment':           { color: '#00E676', glow: 'rgba(0,230,118,.45)',bg1: 'rgba(0,26,14,.95)',  bg2: 'rgba(0,10,5,.99)' },
};

const FALLBACK_COLOR: CatColor = { color: '#FF9933', glow: 'rgba(255,153,51,.45)', bg1: 'rgba(30,20,10,.95)', bg2: 'rgba(12,8,4,.99)' };

// ─── Per-category icons (Ionicons) ───
const CAT_ICONS: Record<string, keyof typeof Ionicons.glyphMap> = {
  'Speed Limits':          'speedometer',
  'Road Rules':            'document-text',
  'Traffic Signs':         'warning',
  'Right of Way':          'git-branch',
  'Traffic Rules':         'book',
  'Situations':            'bulb',
  'Safety':                'shield-checkmark',
  'Driving Conditions':    'rainy',
  'Road Conditions':       'cloudy',
  'Pedestrians and Cyclists': 'walk',
  'Vehicle Knowledge':     'car',
  'Environment and Economy': 'leaf',
  'Alcohol':               'flask',
  'Highway':               'navigate',
  'Overtaking':            'arrow-forward-circle',
  'Intersections':         'git-merge',
  'Parking':               'map',
  'Lights':                'flash',
  'Tires':                 'ellipse',
  'Pedestrians':           'walk',
  'Environment':           'leaf',
};

// ─── Trilingual texts ───
const TR: Record<string, Record<string, any>> = {
  no: {
    selectCategory: 'Velg kategori',
    allCategories: 'Alle kategorier',
    practice: 'Øvingsmodus',
    exam: 'Eksamensmodus',
    questions: 'spørsmål',
    swipeHint: 'Sveip å bla',
    categories: {
      'Speed Limits': 'Fartsgrenser',
      'Road Rules': 'Trafikkregler',
      'Traffic Signs': 'Trafikkskilt',
      'Right of Way': 'Vikeplikt',
      'Traffic Rules': 'Grunnregler',
      'Situations': 'Situasjoner',
      'Safety': 'Sikkerhet',
      'Driving Conditions': 'Kjøreforhold',
      'Road Conditions': 'Veiforhold',
      'Pedestrians and Cyclists': 'Gående/Syklister',
      'Vehicle Knowledge': 'Kjøretøy',
      'Environment and Economy': 'Miljø/Økonomi',
      'Alcohol': 'Rus',
      'Highway': 'Motorvei',
      'Overtaking': 'Forbikjøring',
      'Intersections': 'Kryss',
      'Parking': 'Parkering',
      'Lights': 'Lys',
      'Tires': 'Dekk',
      'Pedestrians': 'Fotgjengere',
      'Environment': 'Miljø',
    },
  },
  th: {
    selectCategory: 'เลือกหมวดหมู่',
    allCategories: 'ทุกหมวดหมู่',
    practice: 'โหมดฝึกซ้อม',
    exam: 'โหมดสอบ',
    questions: 'ข้อ',
    swipeHint: 'ปัดเพื่อเรียกดู',
    categories: {
      'Speed Limits': 'ขีดจำกัดความเร็ว',
      'Road Rules': 'กฎจราจร',
      'Traffic Signs': 'ป้ายจราจร',
      'Right of Way': 'การให้ทาง',
      'Traffic Rules': 'กฎพื้นฐาน',
      'Situations': 'สถานการณ์',
      'Safety': 'ความปลอดภัย',
      'Driving Conditions': 'สภาพการขับขี่',
      'Road Conditions': 'สภาพถนน',
      'Pedestrians and Cyclists': 'คนเดิน/จักรยาน',
      'Vehicle Knowledge': 'ความรู้รถ',
      'Environment and Economy': 'สิ่งแวดล้อม',
      'Alcohol': 'แอลกอฮอล์',
      'Highway': 'ทางหลวง',
      'Overtaking': 'การแซง',
      'Intersections': 'ทางแยก',
      'Parking': 'ที่จอดรถ',
      'Lights': 'ไฟ',
      'Tires': 'ยาง',
      'Pedestrians': 'คนเดินเท้า',
      'Environment': 'สิ่งแวดล้อม',
    },
  },
  en: {
    selectCategory: 'Select Category',
    allCategories: 'All Categories',
    practice: 'Practice Mode',
    exam: 'Exam Mode',
    questions: 'questions',
    swipeHint: 'Swipe to browse',
    categories: {
      'Speed Limits': 'Speed Limits',
      'Road Rules': 'Road Rules',
      'Traffic Signs': 'Traffic Signs',
      'Right of Way': 'Right of Way',
      'Traffic Rules': 'Traffic Rules',
      'Situations': 'Situations',
      'Safety': 'Safety',
      'Driving Conditions': 'Driving Conditions',
      'Road Conditions': 'Road Conditions',
      'Pedestrians and Cyclists': 'Pedestrians & Cyclists',
      'Vehicle Knowledge': 'Vehicle Knowledge',
      'Environment and Economy': 'Environment & Economy',
      'Alcohol': 'Alcohol & Drugs',
      'Highway': 'Highway Driving',
      'Overtaking': 'Overtaking',
      'Intersections': 'Intersections',
      'Parking': 'Parking',
      'Lights': 'Lights',
      'Tires': 'Tires',
      'Pedestrians': 'Pedestrians',
      'Environment': 'Environment',
    },
  },
};

export default function CategoriesScreen() {
  const router = useRouter();
  const { mode } = useLocalSearchParams<{ mode: string }>();
  const { language, colors: c } = useAppStore();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [stageHeight, setStageHeight] = useState(0);
  const [showHint, setShowHint] = useState(true);
  const t = TR[language] || {};
  const isDark = c.bg === '#0F172A' || c.bg === '#0B1222';

  useEffect(() => {
    api.getCategories()
      .then((data) => setCategories(data.sort((a, b) => b.count - a.count)))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // ── Build carousel items with All Categories prepended ──
  const items = useMemo(() => {
    if (!categories.length) return [];
    const totalCount = categories.reduce((s, x) => s + x.count, 0);
    const allColor = CAT_COLORS['__all__'] || FALLBACK_COLOR;
    return [
      {
        key: '__all__',
        dbName: '__all__',
        title: t.allCategories,
        count: totalCount,
        icon: 'sparkles' as const,
        colorMeta: allColor,
      },
      ...categories.map((cat) => {
        const colorMeta = CAT_COLORS[cat.name] || FALLBACK_COLOR;
        return {
          key: cat.name,
          dbName: cat.name,
          title: (t.categories as any)[cat.name] || cat.name,
          count: cat.count,
          icon: (CAT_ICONS[cat.name] || 'help-circle') as keyof typeof Ionicons.glyphMap,
          colorMeta,
        };
      }),
    ];
  }, [categories, language]);

  const maxIdx = Math.max(0, items.length - 1);

  // ── Animated values: activeIndex controls all item transforms ──
  const activeIndex = useRef(new Animated.Value(0)).current;
  const currentSnapRef = useRef(0);
  const rawOffsetRef = useRef(0);
  const dragStartRef = useRef(0);

  // Continuous gradient rotation for the active ring (conic-gradient substitute)
  const spinAnim = useRef(new Animated.Value(0)).current;
  const spinDeg = spinAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  useEffect(() => {
    Animated.loop(
      Animated.timing(spinAnim, {
        toValue: 1,
        duration: 2400,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    ).start();
  }, []);

  // Swipe hint fades after 5s (matching web's setTimeout)
  useEffect(() => {
    const timer = setTimeout(() => setShowHint(false), 5000);
    return () => clearTimeout(timer);
  }, []);

  const clamp = (v: number, min: number, max: number) => Math.min(Math.max(v, min), max);

  const snapTo = useCallback((idx: number) => {
    const s = Math.round(clamp(idx, 0, maxIdx));
    currentSnapRef.current = s;
    rawOffsetRef.current = s;
    Animated.spring(activeIndex, {
      toValue: s,
      tension: 100,
      friction: 10,
      useNativeDriver: true,
    }).start();
  }, [maxIdx, activeIndex]);

  // ── PanResponder: horizontal drag rotates the cylinder ──
  const panResponder = useRef(PanResponder.create({
    onStartShouldSetPanResponder: () => false,
    onMoveShouldSetPanResponder: (_, g) =>
      Math.abs(g.dx) > 10 && Math.abs(g.dx) > Math.abs(g.dy) * 2,
    onPanResponderGrant: () => {
      dragStartRef.current = rawOffsetRef.current;
    },
    onPanResponderMove: (_, g) => {
      const raw = dragStartRef.current - g.dx / DRAG_THRESHOLD;
      const clamped = clamp(raw, 0, maxIdx);
      activeIndex.setValue(clamped);
      rawOffsetRef.current = clamped;
    },
    onPanResponderRelease: (_, g) => {
      if (Math.abs(g.dx) < 5 && Math.abs(g.dy) < 5) return; // tap, handled by Pressable
      snapTo(Math.round(clamp(rawOffsetRef.current, 0, maxIdx)));
    },
    onPanResponderTerminate: () => {
      snapTo(Math.round(clamp(rawOffsetRef.current, 0, maxIdx)));
    },
  })).current;

  // ── Navigate to quiz ──
  const startQuiz = useCallback((dbName: string) => {
    const category = dbName === '__all__' ? 'all' : dbName;
    router.push({ pathname: '/quiz', params: { mode, category } });
  }, [mode, router]);

  // ── Tap handler: active item starts quiz, non-active snaps to center ──
  const handleItemPress = useCallback((idx: number) => {
    if (idx === currentSnapRef.current) {
      startQuiz(items[idx]?.dbName || '');
    } else {
      snapTo(idx);
    }
  }, [items, startQuiz, snapTo]);

  // ── Interpolation factories ──
  const interpTranslateX = (i: number) =>
    activeIndex.interpolate({
      inputRange: [i - 3, i - 2, i - 1, i, i + 1, i + 2, i + 3],
      outputRange: [-SPACING * 3, -SPACING * 2, -SPACING, 0, SPACING, SPACING * 2, SPACING * 3],
      extrapolate: 'clamp',
    });

  const interpScale = (i: number) =>
    activeIndex.interpolate({
      inputRange: [i - 3, i - 2, i - 1, i, i + 1, i + 2, i + 3],
      outputRange: [0.40, 0.55, 0.78, 1.05, 0.78, 0.55, 0.40],
      extrapolate: 'clamp',
    });

  const interpOpacity = (i: number) =>
    activeIndex.interpolate({
      inputRange: [i - 3, i - 2, i - 1, i, i + 1, i + 2, i + 3],
      outputRange: [0, 0.20, 0.55, 1, 0.55, 0.20, 0],
      extrapolate: 'clamp',
    });

  const interpRotateY = (i: number) =>
    activeIndex.interpolate({
      inputRange: [i - 2, i - 1, i, i + 1, i + 2],
      outputRange: [
        `${ANGLE_STEP * 2}deg`,
        `${ANGLE_STEP}deg`,
        '0deg',
        `-${ANGLE_STEP}deg`,
        `-${ANGLE_STEP * 2}deg`,
      ],
      extrapolate: 'clamp',
    });

  const interpRingOpacity = (i: number) =>
    activeIndex.interpolate({
      inputRange: [i - 0.5, i, i + 0.5],
      outputRange: [0, 1, 0],
      extrapolate: 'clamp',
    });

  // ═══════════════ RENDER ═══════════════

  if (loading) {
    return (
      <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
        <View style={st.center}><ActivityIndicator size="large" color={c.accent} /></View>
      </SafeAreaView>
    );
  }

  if (!items.length) {
    return (
      <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
        <View style={st.center}>
          <Text style={{ fontSize: 48 }}>📭</Text>
          <Text style={[st.emptyText, { color: c.textMuted }]}>Ingen kategorier tilgjengelig</Text>
        </View>
        <BottomNavBar activeTab="categories" />
      </SafeAreaView>
    );
  }

  const currentSnap = currentSnapRef.current;

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <LinearGradient
        colors={isDark ? ['#0B1222', '#0F172A', '#0B1222'] : ['#F8FAFC', '#FFFFFF', '#F1F5F9']}
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
        <View style={{ marginRight: 12 }}>
          <AppBrand size="md" />
        </View>
        <View style={{ flex: 1 }}>
          <Text style={[st.modeLabel, { color: c.accent }]}>
            {mode === 'exam' ? t.exam : t.practice}
          </Text>
          <Text style={[st.title, { color: c.text }]}>
            {t.selectCategory}
          </Text>
        </View>
      </View>

      {/* ── 3D Cylinder Carousel ── */}
      <View
        style={st.carouselArea}
        onLayout={(e) => setStageHeight(e.nativeEvent.layout.height)}
        {...panResponder.panHandlers}
      >
        {/* Edge fades */}
        <LinearGradient
          colors={[c.bg, 'transparent']}
          start={{ x: 0, y: 0.5 }}
          end={{ x: 1, y: 0.5 }}
          style={st.fadeLeft}
          pointerEvents="none"
        />
        <LinearGradient
          colors={['transparent', c.bg]}
          start={{ x: 0, y: 0.5 }}
          end={{ x: 1, y: 0.5 }}
          style={st.fadeRight}
          pointerEvents="none"
        />

        {/* Swipe hint */}
        {showHint && (
          <Text style={st.swipeHint}>{t.swipeHint}</Text>
        )}

        {/* Stage — items centred and stacked */}
        <View style={[st.stage, { height: stageHeight || 340 }]}>
          {items.map((cat, i) => {
            const tx = interpTranslateX(i);
            const sc = interpScale(i);
            const op = interpOpacity(i);
            const ry = interpRotateY(i);
            const ringOp = interpRingOpacity(i);
            const cc = cat.colorMeta;

            return (
              <Pressable
                key={cat.key}
                onPress={() => handleItemPress(i)}
                style={[
                  st.cardOuter,
                  {
                    width: CARD_W,
                    height: CARD_H,
                    top: stageHeight ? (stageHeight - CARD_H) / 2 : 110,
                    left: (SCREEN_W - CARD_W) / 2,
                    zIndex: Math.max(1, 100 - Math.abs(i - rawOffsetRef.current) * 10),
                  },
                ]}
              >
                <Animated.View
                  style={{
                    width: '100%',
                    height: '100%',
                    transform: [
                      { perspective: 1000 },
                      { translateX: tx },
                      { scale: sc },
                      { rotateY: ry },
                    ],
                    opacity: op,
                  }}
                >
                  {/* Neon active ring (rotating gradient) */}
                  <Animated.View
                    style={[st.ringBase, { opacity: ringOp }]}
                    pointerEvents="none"
                  >
                    <Animated.View
                      style={[
                        StyleSheet.absoluteFill,
                        { borderRadius: 22, transform: [{ rotate: spinDeg }] },
                      ]}
                    >
                      <LinearGradient
                        colors={[
                          'transparent',
                          cc.color,
                          'rgba(255,255,255,0.92)',
                          cc.color,
                          'transparent',
                        ]}
                        locations={[0, 0.18, 0.24, 0.30, 0.48]}
                        style={StyleSheet.absoluteFill}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 1 }}
                      />
                    </Animated.View>
                  </Animated.View>

                  {/* Card face */}
                  <View style={[st.cardFace, { borderColor: 'rgba(255,255,255,0.08)' }]}>
                    <LinearGradient
                      colors={
                        isDark
                          ? [cc.bg1, cc.bg2]
                          : ['rgba(255,255,255,0.92)', 'rgba(241,245,249,0.96)']
                      }
                      style={[StyleSheet.absoluteFill, { borderRadius: 20 }]}
                    />

                    {/* Subtle grid overlay (dark mode only) */}
                    {isDark && (
                      <View style={st.gridOverlay} pointerEvents="none" />
                    )}

                    {/* Icon */}
                    <View style={[st.iconWrap, { shadowColor: cc.color }]}>
                      <Ionicons
                        name={cat.key === '__all__' ? 'sparkles' : cat.icon}
                        size={32}
                        color={cc.color}
                      />
                    </View>

                    {/* Category label */}
                    <Text
                      style={[st.cardLabel, { color: isDark ? '#E2E8F0' : '#0F172A' }]}
                      numberOfLines={2}
                      adjustsFontSizeToFit
                    >
                      {cat.title}
                    </Text>

                    {/* Question count */}
                    <Text style={[st.cardCount, { color: '#64748B' }]}>
                      {cat.count} {t.questions}
                    </Text>
                  </View>
                </Animated.View>
              </Pressable>
            );
          })}
        </View>

        {/* ── Dots indicator ── */}
        {items.length > 1 && (
          <View style={[st.dotsRow, { bottom: 16 }]} pointerEvents="none">
            {items.map((_, i) => {
              const dist = Math.abs(i - rawOffsetRef.current);
              const isActiveDot = dist < 0.4;
              const isAdjacent = dist < 1.4 && !isActiveDot;
              return (
                <View
                  key={i}
                  style={[
                    st.dot,
                    {
                      width: isActiveDot ? 20 : isAdjacent ? 8 : 6,
                      backgroundColor: isActiveDot
                        ? '#FF9933'
                        : isAdjacent
                          ? 'rgba(255,255,255,0.30)'
                          : 'rgba(255,255,255,0.18)',
                    },
                  ]}
                />
              );
            })}
          </View>
        )}
      </View>

      <BottomNavBar activeTab="categories" />
    </SafeAreaView>
  );
}

// ════════════════════════════════════════════
//  STYLES
// ════════════════════════════════════════════

const st = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  emptyText: { fontSize: 15, textAlign: 'center', marginTop: 12 },

  // Header
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
  },
  backBtn: {
    width: 40, height: 40, borderRadius: 12,
    justifyContent: 'center', alignItems: 'center',
    marginRight: 14, borderWidth: 1,
  },
  modeLabel: { fontSize: 11, textTransform: 'uppercase', letterSpacing: 1.5, fontWeight: '800' },
  title: { fontSize: 22, fontWeight: '800', marginTop: 3, letterSpacing: -0.4 },

  // Carousel area
  carouselArea: {
    flex: 1,
    position: 'relative',
    overflow: 'hidden',
  },

  // Edge fades
  fadeLeft: {
    position: 'absolute',
    left: 0, top: 0, bottom: 0,
    width: 50,
    zIndex: 10,
  },
  fadeRight: {
    position: 'absolute',
    right: 0, top: 0, bottom: 0,
    width: 50,
    zIndex: 10,
  },

  // Swipe hint
  swipeHint: {
    position: 'absolute',
    bottom: 44,
    alignSelf: 'center',
    fontSize: 12,
    color: 'rgba(255,255,255,0.20)',
    fontWeight: '500',
    letterSpacing: 0.5,
    zIndex: 10,
  },

  // Stage holds all cards
  stage: {
    position: 'relative',
    width: '100%',
  },

  // Card outer (positioned absolute in centre)
  cardOuter: {
    position: 'absolute',
  },

  // Neon ring around active card
  ringBase: {
    position: 'absolute',
    top: -3,
    left: -3,
    right: -3,
    bottom: -3,
    borderRadius: 23,
  },

  // Card face
  cardFace: {
    width: '100%',
    height: '100%',
    borderRadius: 20,
    borderWidth: 1.5,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    gap: 6,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 6,
  },

  // Subtle grid overlay (dark mode only)
  gridOverlay: {
    position: 'absolute',
    top: 0, left: 0, right: 0, bottom: 0,
    opacity: 0.06,
    borderRadius: 20,
    backgroundColor: 'rgba(0,245,255,0.03)',
  },

  // Icon container
  iconWrap: {
    width: 56,
    height: 56,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 2,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 4,
  },

  // Category label
  cardLabel: {
    fontSize: 15,
    fontWeight: '800',
    lineHeight: 19,
    textAlign: 'center',
    letterSpacing: -0.2,
  },

  // Question count
  cardCount: {
    fontSize: 12,
    fontWeight: '600',
  },

  // Dots
  dotsRow: {
    position: 'absolute',
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 6,
    zIndex: 5,
  },
  dot: {
    height: 6,
    borderRadius: 3,
  },
});
