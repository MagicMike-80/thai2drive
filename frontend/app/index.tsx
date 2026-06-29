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
import { CoachBanner } from '../src/components/CoachBanner';
import { BottomNavBar } from '../src/components/BottomNavBar';

const T2D_ICON = require('../assets/images/t2d-icon.png');

const TR: Record<string, Record<string, string>> = {
  no: { subtitle: 'Norsk førerprøve', startQuiz: 'Start quiz', exam: 'Eksamen', accuracy: 'Nøyaktighet', answered: 'Besvart', correct: 'Riktige', premiumCta: 'Premium',  premiumOffer: 'Ubegrenset tilgang · fra 99 kr', premiumActive: 'Premium aktiv', streak: 'dagers rekke', freeLeft: 'gratis igjen', dailyLimitReached: 'Opprett gratis konto for å fortsette', dailyTest: 'Dagens test', moreOptions: 'Flere', accountTitle: 'Opprett gratis konto for å fortsette', accountBody: 'Du har brukt de 5 gjestespørsmålene. Opprett en gratis konto for 10 spørsmål per dag og behold progresjonen din.', accountSignup: 'Opprett konto', accountLogin: 'Logg inn', accountCancel: 'Avbryt', studyBook: 'Læringsbok', signGallery: 'Trafikkskilt', myStats: 'Min statistikk', smartPractice: 'Smart øving', aiInsights: 'AI Analyse', trafficMath: 'Trafikk-matte', michaelTeacher: 'Trafikklærer', library: 'Bibliotek', glossary: 'Ordliste', social: 'Sosiale' },
  th: { subtitle: 'สอบใบขับขี่นอร์เวย์', startQuiz: 'เริ่มทำแบบทดสอบ', exam: 'สอบ', accuracy: 'ความแม่นยำ', answered: 'ตอบแล้ว', correct: 'ถูกต้อง', premiumCta: 'พรีเมียม', premiumOffer: 'ใช้งานไม่จำกัด · เริ่มต้น 99 kr', premiumActive: 'Premium ใช้งานอยู่', streak: 'วันติดต่อกัน', freeLeft: 'ฟรีเหลือ', dailyLimitReached: 'สร้างบัญชีฟรีเพื่อเรียนต่อ', dailyTest: 'แบบทดสอบประจำวัน', moreOptions: 'เพิ่มเติม', accountTitle: 'สร้างบัญชีฟรีเพื่อเรียนต่อ', accountBody: 'คุณใช้คำถามสำหรับผู้ใช้ทั่วไปครบ 5 ข้อแล้ว สร้างบัญชีฟรีเพื่อรับ 10 คำถามต่อวันและเก็บความก้าวหน้าของคุณไว้', accountSignup: 'สร้างบัญชี', accountLogin: 'เข้าสู่ระบบ', accountCancel: 'ยกเลิก', studyBook: 'หนังสือเรียน', signGallery: 'ป้ายจราจร', myStats: 'สถิติของฉัน', smartPractice: 'ฝึกอัจฉริยะ', aiInsights: 'AI วิเคราะห์', trafficMath: 'คณิตจราจร', michaelTeacher: 'ครูสอนขับ', library: 'ห้องสมุด', glossary: 'คำศัพท์', social: 'โซเชียล' },
  en: { subtitle: 'Norwegian driving test', startQuiz: 'Start quiz', exam: 'Exam', accuracy: 'Accuracy', answered: 'Answered', correct: 'Correct', premiumCta: 'Premium', premiumOffer: 'Unlimited access · from 99 NOK', premiumActive: 'Premium active', streak: 'day streak', freeLeft: 'free left', dailyLimitReached: 'Create a free account to continue', dailyTest: 'Daily test', moreOptions: 'More', accountTitle: 'Create a free account to continue', accountBody: 'You have used the 5 guest questions. Create a free account for 10 questions per day and keep your progress.', accountSignup: 'Create account', accountLogin: 'Log in', accountCancel: 'Cancel', studyBook: 'Study Book', signGallery: 'Traffic Signs', myStats: 'My Statistics', smartPractice: 'Smart Practice', aiInsights: 'AI Insights', trafficMath: 'Traffic Math', michaelTeacher: 'Instructor', library: 'Library', glossary: 'Glossary', social: 'Social' },
};

export default function HomeScreen() {
  const router = useRouter();
  const { language, deviceId, setProgress, progress, colors, isPremium, isAuthenticated, freeRemaining, streak, updateStreak, setShowTrafficPanel } = useAppStore();
  const [loading, setLoading] = useState(true);
  const [dailyDone, setDailyDone] = useState(false);
  const [carousel2Tab, setCarousel2Tab] = useState<'history' | 'library'>('history');
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
        {/* Top bar: language + settings */}
        <View style={st.topBar}>
          <View style={st.topRight}>
            <LanguageSwitcher size="sm" />
            <TouchableOpacity testID="settings-btn" style={[st.iconBtn, { backgroundColor: c.card, borderColor: c.cardBorder }]} onPress={() => router.push('/settings')}>
              <Ionicons name="settings-outline" size={20} color={c.text} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Brand */}
        <View style={st.brand}>
          <Image source={T2D_ICON} style={st.brandIcon} accessibilityLabel="Thai2Drive logo" />
          <Text style={[st.title, { color: c.text }]} testID="home-title">Thai2Drive</Text>
          <Text style={[st.subtitle, { color: c.textMuted }]}>{t.subtitle}</Text>
        </View>

        {/* Streak (only if >0) */}
        {streak > 0 && (
          <View style={st.streakPill}>
            <Ionicons name="flame" size={16} color="#FF6B35" />
            <Text style={[st.streakText, { color: c.accent }]}>{streak} {t.streak}</Text>
          </View>
        )}

        {/* AI Coach Banner */}
        <CoachBanner
          deviceId={deviceId}
          lang={language}
          streak={streak}
          colors={c}
        />

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

        {/* CAROUSEL 1: Quick-access buttons — single visible with arrow indicator */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          scrollEventThrottle={16}
          style={st.carousel1Container}
          contentContainerStyle={st.carousel1Content}
        >
          {/* Eksamen */}
          <TouchableOpacity
            testID="exam-mode-btn"
            onPress={() => { if (locked) handleLockedNav(); else router.push({ pathname: '/quiz', params: { mode: 'exam', category: 'all' } }); }}
            activeOpacity={0.7}
          >
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel1GradientBorder}
            >
              <View style={[st.carousel1BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name="school-outline" size={20} color={c.accent} />
                <Text style={[st.carousel1Label, { color: c.text }]}>{t.exam}</Text>
                <Text style={[st.carousel1Arrow, { color: c.accent }]}>›</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>

          {/* Daglig test */}
          <TouchableOpacity
            testID="daily-test-btn"
            onPress={() => router.push({ pathname: '/quiz', params: { mode: 'daily', category: 'all' } })}
            activeOpacity={0.7}
          >
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel1GradientBorder}
            >
              <View style={[st.carousel1BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name={dailyDone ? 'checkmark-circle' : 'today-outline'} size={20} color={dailyDone ? c.correct : c.accent} />
                <Text style={[st.carousel1Label, { color: dailyDone ? c.correct : c.text }]}>{t.dailyTest}</Text>
                <Text style={[st.carousel1Arrow, { color: c.accent }]}>›</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>

          {/* Trafikk-matte */}
          <TouchableOpacity
            testID="traffic-math-btn"
            onPress={() => {
              if (isDesktopWeb) setShowTrafficPanel(true);
              else router.push('/traffic-math');
            }}
            activeOpacity={0.7}
          >
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel1GradientBorder}
            >
              <View style={[st.carousel1BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name="speedometer-outline" size={20} color={c.accent} />
                <Text style={[st.carousel1Label, { color: c.text }]}>{t.trafficMath}</Text>
                <Text style={[st.carousel1Arrow, { color: c.accent }]}>›</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>
        </ScrollView>

        {/* CAROUSEL 2: Toggle buttons — Historikk | Bibliotek */}
        <View style={st.carousel2Container}>
          <TouchableOpacity
            onPress={() => setCarousel2Tab('history')}
            activeOpacity={0.7}
          >
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel2GradientBorder}
            >
              <View style={[st.carousel2BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name="time-outline" size={18} color={carousel2Tab === 'history' ? c.accent : c.textMuted} />
                <Text style={[st.carousel2Label, { color: carousel2Tab === 'history' ? c.text : c.textMuted }]}>Historikk</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => setCarousel2Tab('library')}
            activeOpacity={0.7}
          >
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel2GradientBorder}
            >
              <View style={[st.carousel2BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name="library-outline" size={18} color={carousel2Tab === 'library' ? c.accent : c.textMuted} />
                <Text style={[st.carousel2Label, { color: carousel2Tab === 'library' ? c.text : c.textMuted }]}>Bibliotek</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>
        </View>

        {/* CAROUSEL 3: Navigation buttons — single visible with arrow indicator */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          scrollEventThrottle={16}
          style={st.carousel3Container}
          contentContainerStyle={st.carousel3Content}
        >
          {/* Hjem */}
          <TouchableOpacity onPress={() => router.push('/')} activeOpacity={0.7}>
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel3GradientBorder}
            >
              <View style={[st.carousel3BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name="home-outline" size={20} color={c.accent} />
                <Text style={[st.carousel3Label, { color: c.text }]}>Hjem</Text>
                <Text style={[st.carousel3Arrow, { color: c.accent }]}>›</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>

          {/* Kategorier */}
          <TouchableOpacity onPress={() => router.push('/categories')} activeOpacity={0.7}>
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel3GradientBorder}
            >
              <View style={[st.carousel3BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name="grid-outline" size={20} color={c.accent} />
                <Text style={[st.carousel3Label, { color: c.text }]}>Kategorier</Text>
                <Text style={[st.carousel3Arrow, { color: c.accent }]}>›</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>

          {/* Historikk */}
          <TouchableOpacity onPress={() => router.push('/history')} activeOpacity={0.7}>
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel3GradientBorder}
            >
              <View style={[st.carousel3BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name="time-outline" size={20} color={c.accent} />
                <Text style={[st.carousel3Label, { color: c.text }]}>Historikk</Text>
                <Text style={[st.carousel3Arrow, { color: c.accent }]}>›</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>

          {/* Michael */}
          <TouchableOpacity onPress={() => router.push('/teacher')} activeOpacity={0.7}>
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel3GradientBorder}
            >
              <View style={[st.carousel3BtnInner, { backgroundColor: c.bg }]}>
                <Image source={require('../assets/michael_avatar.png')} style={st.carousel3Avatar} />
                <Text style={[st.carousel3Label, { color: c.accent, fontWeight: '700' }]}>Michael</Text>
                <Text style={[st.carousel3Arrow, { color: c.accent }]}>›</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>

          {/* Trafikkskilt */}
          <TouchableOpacity onPress={() => router.push('/signs')} activeOpacity={0.7}>
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel3GradientBorder}
            >
              <View style={[st.carousel3BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name="warning-outline" size={20} color={c.accent} />
                <Text style={[st.carousel3Label, { color: c.text }]}>Skilt</Text>
                <Text style={[st.carousel3Arrow, { color: c.accent }]}>›</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>

          {/* Studiebøk */}
          <TouchableOpacity onPress={() => router.push('/book')} activeOpacity={0.7}>
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel3GradientBorder}
            >
              <View style={[st.carousel3BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name="book-outline" size={20} color={c.accent} />
                <Text style={[st.carousel3Label, { color: c.text }]}>Bok</Text>
                <Text style={[st.carousel3Arrow, { color: c.accent }]}>›</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>

          {/* Bokmerker */}
          <TouchableOpacity onPress={() => router.push('/bookmarks')} activeOpacity={0.7}>
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel3GradientBorder}
            >
              <View style={[st.carousel3BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name="bookmark-outline" size={20} color={c.accent} />
                <Text style={[st.carousel3Label, { color: c.text }]}>Merker</Text>
                <Text style={[st.carousel3Arrow, { color: c.accent }]}>›</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>

          {/* Innstillinger */}
          <TouchableOpacity onPress={() => router.push('/settings')} activeOpacity={0.7}>
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel3GradientBorder}
            >
              <View style={[st.carousel3BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name="settings-outline" size={20} color={c.accent} />
                <Text style={[st.carousel3Label, { color: c.text }]}>Instill</Text>
                <Text style={[st.carousel3Arrow, { color: c.accent }]}>›</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>

          {/* Profil → går til statistikk (profilside finnes ikke som egen rute) */}
          <TouchableOpacity onPress={() => router.push('/stats')} activeOpacity={0.7}>
            <LinearGradient
              colors={['#06FFA5', '#00BFFF', '#9D4EDD', '#FF1493', '#06FFA5']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={st.carousel3GradientBorder}
            >
              <View style={[st.carousel3BtnInner, { backgroundColor: c.bg }]}>
                <Ionicons name="bar-chart-outline" size={20} color={c.accent} />
                <Text style={[st.carousel3Label, { color: c.text }]}>Statistikk</Text>
                <Text style={[st.carousel3Arrow, { color: c.accent }]}>›</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>
        </ScrollView>

        {/* Progress — single clean row, no card nesting */}
        {progress.total_questions_answered > 0 && (
          <View style={st.statsBlock}>
            <View style={st.statCol}>
              <Text style={[st.statVal, { color: c.text }]}>{progress.total_questions_answered}</Text>
              <Text style={[st.statLbl, { color: c.textMuted }]}>{t.answered}</Text>
            </View>
            <View style={[st.divider, { backgroundColor: c.divider }]} />
            <View style={st.statCol}>
              <Text style={[st.statVal, { color: c.text }]}>{progress.correct_answers}</Text>
              <Text style={[st.statLbl, { color: c.textMuted }]}>{t.correct}</Text>
            </View>
            <View style={[st.divider, { backgroundColor: c.divider }]} />
            <View style={st.statCol}>
              <Text style={[st.statVal, { color: accuracy >= 70 ? c.correct : c.text }]}>{accuracy}%</Text>
              <Text style={[st.statLbl, { color: c.textMuted }]}>{t.accuracy}</Text>
            </View>
          </View>
        )}

        {/* Premium banner / active */}
        {!isPremium ? (
          <TouchableOpacity
            testID="home-premium-btn"
            style={[
              st.premBanner,
              {
                backgroundColor: c.card,
                borderColor: c.accent,
              }
            ]}
            onPress={() => router.push('/paywall')}
            activeOpacity={0.85}
          >
            <Ionicons name="diamond" size={18} color={c.accent} />
            <View style={{ flex: 1, marginLeft: 10 }}>
              <Text style={[st.premTitle, { color: c.accent }]}>{t.premiumCta}</Text>
              <Text style={[st.premSub, { color: c.textSecondary }]}>{t.premiumOffer}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={c.accent} />
          </TouchableOpacity>
        ) : (
          <View
            style={[
              st.premActive,
              {
                backgroundColor: c.card,
                borderColor: c.correct,
              }
            ]}
          >
            <Ionicons name="diamond" size={16} color={c.correct} />
            <Text style={[st.premActiveText, { color: c.correct }]}>{t.premiumActive}</Text>
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
  topBar: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 },
  topRight: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  iconBtn: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center', borderWidth: 1 },
  brand: { alignItems: 'center', marginBottom: 20 },
  brandIcon: { width: 64, height: 64, borderRadius: 16, marginBottom: 14 },
  title: { fontSize: 34, fontWeight: '800', letterSpacing: -1 },
  subtitle: { fontSize: 14, marginTop: 4 },
  streakPill: { flexDirection: 'row', alignItems: 'center', alignSelf: 'center', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 14, gap: 6, marginBottom: 20 },
  streakText: { fontSize: 13, fontWeight: '700' },
  startBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 18, paddingVertical: 20, gap: 10, marginBottom: 8 },
  startText: { fontSize: 18, fontWeight: '800', letterSpacing: 0.2 },
  freeHint: { fontSize: 12, textAlign: 'center', marginBottom: 24 },
  // Carousel 1 — single button visible with arrow indicator
  carousel1Container: { marginBottom: 32, marginHorizontal: -24, paddingHorizontal: 24, overflow: 'hidden' },
  carousel1Content: { gap: 12, paddingRight: 24 },
  carousel1GradientBorder: { padding: 2, borderRadius: 12, width: 350, minWidth: 350 },
  carousel1BtnInner: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12, borderRadius: 11, paddingHorizontal: 18, paddingVertical: 16, width: '100%' },
  carousel1Label: { fontSize: 16, fontWeight: '600', flex: 1, marginLeft: 8 },
  carousel1Arrow: { fontSize: 24, fontWeight: '700', opacity: 0.8 },
  // Carousel 2 — toggle buttons (Historikk | Bibliotek)
  carousel2Container: { flexDirection: 'row', gap: 12, marginBottom: 28, justifyContent: 'space-between' },
  carousel2GradientBorder: { padding: 2, borderRadius: 12, flex: 1 },
  carousel2BtnInner: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, borderRadius: 11, paddingHorizontal: 16, paddingVertical: 14, width: '100%' },
  carousel2Label: { fontSize: 14, fontWeight: '600' },
  statsBlock: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around', paddingVertical: 6, marginBottom: 28 },
  statCol: { alignItems: 'center', flex: 1 },
  statVal: { fontSize: 24, fontWeight: '800' },
  statLbl: { fontSize: 11, marginTop: 4, textTransform: 'uppercase', letterSpacing: 0.8 },
  divider: { width: 1, height: 30 },
  premBanner: { flexDirection: 'row', alignItems: 'center', borderRadius: 14, paddingHorizontal: 16, paddingVertical: 14, borderWidth: 1 },
  premTitle: { fontSize: 15, fontWeight: '800' },
  premSub: { fontSize: 12, marginTop: 2 },
  premActive: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', borderRadius: 12, paddingVertical: 10, gap: 6, borderWidth: 1 },
  premActiveText: { fontSize: 13, fontWeight: '700' },
  // Carousel 3 — single button visible with arrow indicator
  carousel3Container: { marginBottom: 28, marginHorizontal: -24, paddingHorizontal: 24, overflow: 'hidden' },
  carousel3Content: { gap: 12, paddingRight: 24 },
  carousel3GradientBorder: { padding: 2, borderRadius: 12, width: 350, minWidth: 350 },
  carousel3BtnInner: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12, borderRadius: 11, paddingHorizontal: 18, paddingVertical: 16, width: '100%' },
  carousel3Label: { fontSize: 16, fontWeight: '600', flex: 1, marginLeft: 8 },
  carousel3Arrow: { fontSize: 24, fontWeight: '700', opacity: 0.8 },
  carousel3Avatar: { width: 28, height: 28, borderRadius: 14 },
  // Language hint
  langHintWrap: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, zIndex: 99, alignItems: 'flex-start', justifyContent: 'flex-start', paddingTop: 70, paddingLeft: 16 },
  langHintDismiss: { alignItems: 'center' },
  langHintBubble: { backgroundColor: '#FF9933', borderRadius: 14, paddingHorizontal: 16, paddingVertical: 10, maxWidth: 260, shadowColor: '#FF9933', shadowOpacity: 0.4, shadowRadius: 12, shadowOffset: { width: 0, height: 4 }, elevation: 8 },
  langHintText: { color: '#0F172A', fontWeight: '800', fontSize: 13, textAlign: 'center', lineHeight: 20 },
  langHintArrow: { fontSize: 28, color: '#FF9933', marginTop: 2, fontWeight: '900' },
});
