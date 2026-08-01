import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Animated, Image, Alert, Platform, useWindowDimensions } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useAppStore } from '../src/store/appStore';
import { api } from '../src/services/api';
import { LanguageSwitcher } from '../src/components/LanguageSwitcher';
import { BottomNavBar } from '../src/components/BottomNavBar';

const T2D_ICON = require('../assets/images/t2d-icon.png');

const TR: Record<string, Record<string, string>> = {
  no: { subtitle: 'Norsk førerprøve', startQuiz: 'Start quiz', exam: 'Eksamen', accuracy: 'Nøyaktighet', answered: 'Besvart', correct: 'Riktige', premiumCta: 'Premium', premiumOffer: 'Ubegrenset tilgang · fra 99 kr', premiumActive: 'Premium aktiv', streak: 'dagers rekke', freeLeft: 'gratis igjen', dailyLimitReached: 'Opprett gratis konto for å fortsette', dailyTest: 'Dagens test', moreOptions: 'Flere', accountTitle: 'Opprett gratis konto for å fortsette', accountBody: 'Du har brukt de 5 gjestespørsmålene. Opprett en gratis konto for 10 spørsmål per dag og behold progresjonen din.', accountSignup: 'Opprett konto', accountLogin: 'Logg inn', accountCancel: 'Avbryt', studyBook: 'Læringsbok', signGallery: 'Trafikkskilt', myStats: 'Min statistikk', smartPractice: 'Smart øving', aiInsights: 'AI Analyse', trafficMath: 'Trafikk-matte', michaelTeacher: 'Trafikklærer', library: 'Bibliotek', glossary: 'Ordliste', social: 'Sosiale', askQuestion: 'Still et spørsmål om trafikk' },
  th: { subtitle: 'สอบใบขับขี่นอร์เวย์', startQuiz: 'เริ่มทำแบบทดสอบ', exam: 'สอบ', accuracy: 'ความแม่นยำ', answered: 'ตอบแล้ว', correct: 'ถูกต้อง', premiumCta: 'พรีเมียม', premiumOffer: 'ใช้งานไม่จำกัด · เริ่มต้น 99 kr', premiumActive: 'Premium ใช้งานอยู่', streak: 'วันติดต่อกัน', freeLeft: 'ฟรีเหลือ', dailyLimitReached: 'สร้างบัญชีฟรีเพื่อเรียนต่อ', dailyTest: 'แบบทดสอบประจำวัน', moreOptions: 'เพิ่มเติม', accountTitle: 'สร้างบัญชีฟรีเพื่อเรียนต่อ', accountBody: 'คุณใช้คำถามสำหรับผู้ใช้ทั่วไปครบ 5 ข้อแล้ว สร้างบัญชีฟรีเพื่อรับ 10 คำถามต่อวันและเก็บความก้าวหน้าของคุณไว้', accountSignup: 'สร้างบัญชี', accountLogin: 'เข้าสู่ระบบ', accountCancel: 'ยกเลิก', studyBook: 'หนังสือเรียน', signGallery: 'ป้ายจราจร', myStats: 'สถิติของฉัน', smartPractice: 'ฝึกอัจฉริยะ', aiInsights: 'AI วิเคราะห์', trafficMath: 'คณิตจราจร', michaelTeacher: 'ครูสอนขับ', library: 'ห้องสมุด', glossary: 'คำศัพท์', social: 'โซเชียล', askQuestion: 'ถามคำถามเกี่ยวกับการจราจร' },
  en: { subtitle: 'Norwegian driving test', startQuiz: 'Start quiz', exam: 'Exam', accuracy: 'Accuracy', answered: 'Answered', correct: 'Correct', premiumCta: 'Premium', premiumOffer: 'Unlimited access · from 99 NOK', premiumActive: 'Premium active', streak: 'day streak', freeLeft: 'free left', dailyLimitReached: 'Create a free account to continue', dailyTest: 'Daily test', moreOptions: 'More', accountTitle: 'Create a free account to continue', accountBody: 'You have used the 5 guest questions. Create a free account for 10 questions per day and keep your progress.', accountSignup: 'Create account', accountLogin: 'Log in', accountCancel: 'Cancel', studyBook: 'Study Book', signGallery: 'Traffic Signs', myStats: 'My Statistics', smartPractice: 'Smart Practice', aiInsights: 'AI Insights', trafficMath: 'Traffic Math', michaelTeacher: 'Instructor', library: 'Library', glossary: 'Glossary', social: 'Social', askQuestion: 'Ask a question about traffic' },
};

export default function HomeScreen() {
  const router = useRouter();
  const { language, deviceId, setProgress, progress, colors, isPremium, isAuthenticated, freeRemaining, streak, updateStreak, setShowTrafficPanel } = useAppStore();
  const [loading, setLoading] = useState(true);
  const [dailyDone, setDailyDone] = useState(false);
  const { width: winWidth } = useWindowDimensions();
  const t = TR[language] || {};
  const c = colors;
  const isDark = c.bg === '#0F172A' || c.bg === '#0B1222';
  // Desktop web = wide viewport inside browser (breaks out of 390px phone frame)
  const isDesktopWeb = Platform.OS === 'web' && winWidth > 700;
  const remaining = freeRemaining();
  const locked = !isPremium && remaining <= 0;

  // Subtle press animation for the main CTA
  const ctaScale = useRef(new Animated.Value(1)).current;
  const pressIn = () => Animated.spring(ctaScale, { toValue: 0.97, useNativeDriver: true, speed: 40, bounciness: 0 }).start();
  const pressOut = () => Animated.spring(ctaScale, { toValue: 1, useNativeDriver: true, speed: 30, bounciness: 6 }).start();

  // Language hint — shows once on first launch
  const [showLangHint, setShowLangHint] = useState(false);
  const hintOpacity = useRef(new Animated.Value(0)).current;
  const hintBounce = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    AsyncStorage.getItem('t2d_lang_hint_shown').then(val => {
      if (!val) {
        setShowLangHint(true);
        // Fade in
        Animated.timing(hintOpacity, { toValue: 1, duration: 400, useNativeDriver: true }).start();
        // Bounce arrow loop
        Animated.loop(
          Animated.sequence([
            Animated.timing(hintBounce, { toValue: -8, duration: 400, useNativeDriver: true }),
            Animated.timing(hintBounce, { toValue: 0, duration: 400, useNativeDriver: true }),
          ])
        ).start();
        // Auto-dismiss after 4 seconds
        setTimeout(() => dismissLangHint(), 4000);
      }
    });
  }, []);

  const dismissLangHint = () => {
    Animated.timing(hintOpacity, { toValue: 0, duration: 300, useNativeDriver: true }).start(() => setShowLangHint(false));
    AsyncStorage.setItem('t2d_lang_hint_shown', '1');
  };

  useEffect(() => { loadData(); }, []);

  const checkDaily = async () => {
    const today = new Date().toISOString().slice(0, 10);
    const result = await AsyncStorage.getItem(`dailyTest_result_${today}`);
    setDailyDone(!!result);
  };

  const loadData = async () => {
    try {
      await api.seedDatabase();
      const p = await api.getProgress(deviceId);
      setProgress(p);
      await updateStreak();
      await checkDaily();
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const accuracy = progress.total_questions_answered > 0
    ? Math.round((progress.correct_answers / progress.total_questions_answered) * 100) : 0;

  // Show the auth/paywall gate when a free user is locked. Guests must
  // sign up or log in first; logged-in free users go straight to paywall.
  const handleLockedNav = () => {
    if (!isAuthenticated) {
      Alert.alert(
        t.accountTitle,
        t.accountBody,
        [
          { text: t.accountCancel, style: 'cancel' },
          { text: t.accountLogin, onPress: () => router.push({ pathname: '/login', params: { redirect: 'paywall' } }) },
          { text: t.accountSignup, onPress: () => router.push({ pathname: '/signup', params: { redirect: 'paywall' } }) },
        ],
        { cancelable: true },
      );
    } else {
      router.push('/paywall');
    }
  };

  const startPractice = () => {
    if (locked) { handleLockedNav(); return; }
    router.push({ pathname: '/categories', params: { mode: 'practice' } });
  };

  if (loading) return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <View style={st.center}><ActivityIndicator testID="home-loading" size="large" color={c.accent} /></View>
    </SafeAreaView>
  );

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      {/* Subtle gradient background — matches categories screen */}
      <LinearGradient
        colors={isDark ? ['#0B1222', '#0F172A', '#0B1222'] : ['#F4F8FD', '#FFFFFF', '#EEF5FB']}
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />
      {/* Language hint overlay — first launch only */}
      {showLangHint && (
        <Animated.View style={[st.langHintWrap, { opacity: hintOpacity }]} pointerEvents="box-none">
          <TouchableOpacity style={st.langHintDismiss} onPress={dismissLangHint} activeOpacity={1}>
            <View style={st.langHintBubble}>
              <Text style={st.langHintText}>🌏  เลือกภาษา · Velg språk · Choose language</Text>
            </View>
            <Animated.Text style={[st.langHintArrow, { transform: [{ translateY: hintBounce }] }]}>
              ↑
            </Animated.Text>
          </TouchableOpacity>
        </Animated.View>
      )}

      <ScrollView contentContainerStyle={st.scroll} showsVerticalScrollIndicator={false}>
        {/* Top bar: streak (left) + language switcher + settings (right) */}
        <View style={st.topBar}>
          <View style={st.topLeft}>
            {/* Mini streak indicator in top bar — number only, no badge */}
            {streak > 0 && (
              <View style={st.topStreak}>
                <Ionicons name="flame" size={12} color="#FF9933" />
                <Text style={st.topStreakNum}>{streak}</Text>
              </View>
            )}
          </View>
          <View style={st.topRight}>
            <LanguageSwitcher size="sm" />
            <TouchableOpacity testID="settings-btn" style={[st.iconBtn, { backgroundColor: c.card, borderColor: c.cardBorder }]} onPress={() => router.push('/settings')}>
              <Ionicons name="settings-outline" size={20} color={c.text} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Brand section */}
        <View style={st.brand}>
          <Image source={T2D_ICON} style={st.brandIcon} accessibilityLabel="Thai2Drive logo" />
          <Text style={[st.title, { color: c.text }]} testID="home-title">Thai2Drive</Text>
          <Text style={[st.subtitle, { color: c.textMuted }]}>{t.subtitle}</Text>
        </View>

        {/* Streak badge — below brand, centered, oval pill (matches web home-top layout) */}
        {streak > 0 && (
          <View style={[st.streakBadge, { backgroundColor: 'rgba(255,153,51,0.11)', borderColor: 'rgba(255,153,51,0.25)' }]}>
            <Text style={st.streakFire}>🔥</Text>
            <Text style={[st.streakNum, { color: '#FF9933' }]}>{streak}</Text>
            <Text style={[st.streakLbl, { color: c.textMuted }]}>{t.streak}</Text>
          </View>
        )}

        {/* PRIMARY CTA: Start Quiz */}
        <Animated.View style={{ transform: [{ scale: ctaScale }] }}>
          <TouchableOpacity
            testID="start-quiz-btn"
            style={[
              st.startBtn,
              {
                backgroundColor: locked ? c.letterBg : c.accent,
                shadowColor: locked ? 'transparent' : c.accent,
                shadowOffset: { width: 0, height: 0 },
                shadowOpacity: locked ? 0 : 0.85,
                shadowRadius: locked ? 0 : 15,
                borderColor: locked ? 'transparent' : c.accent,
                borderWidth: locked ? 0 : 1.5,
                elevation: locked ? 0 : 8,
              }
            ]}
            onPress={startPractice}
            onPressIn={pressIn}
            onPressOut={pressOut}
            activeOpacity={1}
          >
            <Ionicons name={locked ? 'lock-closed' : 'play'} size={22} color={locked ? c.textMuted : '#0F172A'} />
            <Text style={[st.startText, { color: locked ? c.textMuted : '#0F172A' }]}>{t.startQuiz}</Text>
          </TouchableOpacity>
        </Animated.View>

        {/* Free limit hint */}
        {!isPremium && (
          <Text style={[st.freeHint, { color: locked ? c.incorrect : c.textMuted }]}>
            {locked ? t.dailyLimitReached : `${remaining} ${t.freeLeft}`}
          </Text>
        )}

        {/* Horizontal scroll menu — compact hsm-cards (matches web hsm-card design) */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          scrollEventThrottle={16}
          decelerationRate="fast"
          style={st.hsmContainer}
          contentContainerStyle={st.hsmContent}
        >
          {/* Eksamen — with timer display (matches web hsm-exam-timer) */}
          <TouchableOpacity
            testID="exam-mode-btn"
            onPress={() => { if (locked) handleLockedNav(); else router.push({ pathname: '/quiz', params: { mode: 'exam', category: 'all' } }); }}
            activeOpacity={0.7}
            style={[st.hsmCard, { backgroundColor: 'rgba(5,14,38,0.88)', borderColor: 'rgba(0,82,255,0.2)' }]}
          >
            <View style={st.hsmTimer}>
              <Text style={st.hsmTimerText}>90:00</Text>
            </View>
            <Text style={[st.hsmLabel, { color: '#7A90B8' }]}>{t.exam}</Text>
          </TouchableOpacity>

          {/* Daglig test */}
          <TouchableOpacity
            testID="daily-test-btn"
            onPress={() => router.push({ pathname: '/quiz', params: { mode: 'daily', category: 'all' } })}
            activeOpacity={0.7}
            style={[st.hsmCard, { backgroundColor: 'rgba(5,14,38,0.88)', borderColor: 'rgba(0,82,255,0.2)' }]}
          >
            <Text style={st.hsmEmoji}>📅</Text>
            <Text style={[st.hsmLabel, { color: '#7A90B8' }]}>{t.dailyTest}</Text>
          </TouchableOpacity>

          {/* Trafikk-matte */}
          <TouchableOpacity
            testID="traffic-math-btn"
            onPress={() => {
              if (isDesktopWeb) setShowTrafficPanel(true);
              else router.push('/traffic-math');
            }}
            activeOpacity={0.7}
            style={[st.hsmCard, { backgroundColor: 'rgba(5,14,38,0.88)', borderColor: 'rgba(0,82,255,0.2)' }]}
          >
            <Text style={st.hsmEmoji}>🚗</Text>
            <Text style={[st.hsmLabel, { color: '#7A90B8' }]}>{t.trafficMath}</Text>
          </TouchableOpacity>

          {/* Bibliotek */}
          <TouchableOpacity
            testID="library-btn"
            onPress={() => router.push('/library')}
            activeOpacity={0.7}
            style={[st.hsmCard, { backgroundColor: 'rgba(5,14,38,0.88)', borderColor: 'rgba(0,82,255,0.2)' }]}
          >
            <Text style={st.hsmEmoji}>📚</Text>
            <Text style={[st.hsmLabel, { color: '#7A90B8' }]}>{t.library}</Text>
          </TouchableOpacity>
        </ScrollView>

        {/* Michael card — navigates to teacher (matches web home layout) */}
        <TouchableOpacity
          testID="michael-card-btn"
          onPress={() => router.push('/teacher')}
          activeOpacity={0.7}
          style={st.michaelCardOuter}
        >
          <LinearGradient
            colors={['#00F5FF', '#FF00E5', '#00F5FF']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={st.michaelCardBorder}
          >
            <View style={[st.michaelCardInner, { backgroundColor: isDark ? 'rgba(30,58,138,0.35)' : 'rgba(219,234,254,0.60)' }]}>
              <View style={st.michaelCardLeft}>
                <View style={st.michaelCardAvatar}>
                  <Image source={require('../assets/michael_avatar.png')} style={st.michaelAvatarImg} />
                </View>
                <View style={st.michaelCardText}>
                  <Text style={[st.michaelCardName, { color: '#93C5FD' }]}>Michael Trafikklærer</Text>
                  <Text style={[st.michaelCardSub, { color: '#64748B' }]}>{t.askQuestion}</Text>
                </View>
              </View>
              <Text style={[st.michaelCardArrow, { color: '#3B82F6' }]}>›</Text>
            </View>
          </LinearGradient>
        </TouchableOpacity>

        {/* Progress — neon gradient border stats row (matches web .home-stats conic-gradient) */}
        {progress.total_questions_answered > 0 && (
          <LinearGradient
            colors={['#00F5FF', '#FF00E5', '#00F5FF']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={st.statsGradientBorder}
          >
            <View style={[st.statsBlock, { backgroundColor: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(255,255,255,0.92)' }]}>
              <View style={st.statCol}>
                <Text style={[st.statVal, { color: '#FF9933' }]}>{progress.total_questions_answered}</Text>
                <Text style={[st.statLbl, { color: c.textMuted }]}>{t.answered}</Text>
              </View>
              <View style={[st.statDivider, { backgroundColor: c.divider }]} />
              <View style={st.statCol}>
                <Text style={[st.statVal, { color: '#FF9933' }]}>{progress.correct_answers}</Text>
                <Text style={[st.statLbl, { color: c.textMuted }]}>{t.correct}</Text>
              </View>
              <View style={[st.statDivider, { backgroundColor: c.divider }]} />
              <View style={st.statCol}>
                <Text style={[st.statVal, { color: '#FF9933' }]}>{accuracy}%</Text>
                <Text style={[st.statLbl, { color: c.textMuted }]}>{t.accuracy}</Text>
              </View>
            </View>
          </LinearGradient>
        )}

        {/* Premium banner / active */}
        {!isPremium ? (
          <TouchableOpacity
            testID="home-premium-btn"
            style={[
              st.premBanner,
              {
                backgroundColor: 'rgba(16,185,129,0.1)',
                borderColor: 'rgba(16,185,129,0.25)',
              }
            ]}
            onPress={() => router.push('/paywall')}
            activeOpacity={0.85}
          >
            <Text style={{ fontSize: 16 }}>💎</Text>
            <Text style={[st.premTitle, { color: '#10B981' }]}>{t.premiumCta}</Text>
          </TouchableOpacity>
        ) : (
          <View
            style={[
              st.premActive,
              {
                backgroundColor: 'rgba(16,185,129,0.1)',
                borderColor: 'rgba(16,185,129,0.25)',
              }
            ]}
          >
            <Text style={{ fontSize: 14 }}>💎</Text>
            <Text style={[st.premActiveText, { color: '#10B981' }]}>{t.premiumActive}</Text>
          </View>
        )}
      </ScrollView>

      <BottomNavBar activeTab="home" />
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  scroll: { padding: 24, paddingBottom: 110 },
  topBar: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 },
  topLeft: { flex: 1, flexDirection: 'row', alignItems: 'center' },
  // Mini streak in top bar — matches web's #topStreak (compact, always visible when streak>0)
  topStreak: { flexDirection: 'row', alignItems: 'center', gap: 3 },
  topStreakNum: { fontSize: 12, fontWeight: '800', color: '#FF9933' },
  topRight: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  iconBtn: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center', borderWidth: 1 },
  brand: { alignItems: 'center', marginBottom: 24 },
  brandIcon: { width: 64, height: 64, borderRadius: 16, marginBottom: 14 },
  title: { fontSize: 34, fontWeight: '800', letterSpacing: -1 },
  subtitle: { fontSize: 14, marginTop: 4 },
  // Main streak badge — oval pill in content area, below brand (matches web .streak-badge)
  streakBadge: { flexDirection: 'row', alignItems: 'center', alignSelf: 'center', gap: 7, borderRadius: 50, paddingHorizontal: 14, paddingVertical: 5, borderWidth: 1, marginBottom: 24 },
  streakFire: { fontSize: 18 },
  streakNum: { fontSize: 17.6, fontWeight: '900' },
  streakLbl: { fontSize: 12.5, fontWeight: '600' },
  startBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 18, paddingVertical: 20, gap: 10, marginBottom: 8 },
  startText: { fontSize: 18, fontWeight: '800', letterSpacing: 0.2 },
  freeHint: { fontSize: 12, textAlign: 'center', marginBottom: 24 },
  // HSM (Horizontal Scroll Menu) — compact 85px cards matching web hsm-card
  hsmContainer: { marginBottom: 24, marginHorizontal: -24, overflow: 'hidden' },
  hsmContent: { gap: 10, paddingHorizontal: 24, paddingVertical: 6, paddingRight: 28 },
  hsmCard: {
    width: 85,
    height: 85,
    borderRadius: 16,
    borderWidth: 1.5,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingHorizontal: 8,
    paddingVertical: 12,
    // Match web blue glow shadow
    shadowColor: 'rgba(0,82,255,0.25)',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  hsmTimer: {
    backgroundColor: '#1a0000',
    borderWidth: 1.5,
    borderColor: '#FF3B3B',
    borderRadius: 5,
    paddingHorizontal: 4,
    paddingVertical: 2,
  },
  hsmTimerText: {
    fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 2,
    color: '#FF3B3B',
  },
  hsmEmoji: {
    fontSize: 23,
    lineHeight: 26,
  },
  hsmLabel: {
    fontSize: 10,
    fontWeight: '700',
    textAlign: 'center',
    letterSpacing: 0.15,
    lineHeight: 13,
  },
  // Michael card — gradient border, avatar, name, subtitle, arrow
  michaelCardOuter: { width: '100%', marginBottom: 24 },
  michaelCardBorder: { padding: 1.5, borderRadius: 16 },
  michaelCardInner: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', borderRadius: 15, paddingVertical: 10, paddingHorizontal: 14 },
  michaelCardLeft: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  michaelCardAvatar: { marginRight: 12 },
  michaelAvatarImg: { width: 40, height: 40, borderRadius: 20 },
  michaelCardText: { flex: 1 },
  michaelCardName: { fontSize: 15.2, fontWeight: '800' },
  michaelCardSub: { fontSize: 12.8, fontWeight: '500', marginTop: 2 },
  michaelCardArrow: { fontSize: 24, fontWeight: '700', marginLeft: 12 },
  // Stats row — gradient border wrapper (matches web .home-stats conic-gradient)
  statsGradientBorder: {
    padding: 1.5,
    borderRadius: 16,
    marginBottom: 28,
    overflow: 'hidden',
    shadowColor: 'rgba(0,245,255,0.15)',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 4,
  },
  statsBlock: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around', paddingVertical: 14, borderRadius: 15 },
  statCol: { alignItems: 'center', flex: 1 },
  statVal: { fontSize: 25, fontWeight: '900', lineHeight: 28 },
  statLbl: { fontSize: 10, marginTop: 5, letterSpacing: 0.4, textTransform: 'uppercase', fontWeight: '700' },
  statDivider: { width: 1, height: 30 },
  // Premium banner — green pill (matches web .premium-banner)
  premBanner: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    borderRadius: 50, paddingVertical: 10, paddingHorizontal: 20, borderWidth: 1,
  },
  premTitle: { fontSize: 13.6, fontWeight: '800' },
  premSub: { display: 'none' }, // hidden on web too
  premActive: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', borderRadius: 50, paddingVertical: 10, paddingHorizontal: 20, borderWidth: 1, alignSelf: 'center', gap: 6 },
  premActiveText: { fontSize: 13, fontWeight: '700' },
  // Language hint
  langHintWrap: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, zIndex: 99, alignItems: 'flex-start', justifyContent: 'flex-start', paddingTop: 70, paddingLeft: 16 },
  langHintDismiss: { alignItems: 'center' },
  langHintBubble: { backgroundColor: '#FF9933', borderRadius: 14, paddingHorizontal: 16, paddingVertical: 10, maxWidth: 260, shadowColor: '#FF9933', shadowOpacity: 0.4, shadowRadius: 12, shadowOffset: { width: 0, height: 4 }, elevation: 8 },
  langHintText: { color: '#0F172A', fontWeight: '800', fontSize: 13, textAlign: 'center', lineHeight: 20 },
  langHintArrow: { fontSize: 28, color: '#FF9933', marginTop: 2, fontWeight: '900' },
});
