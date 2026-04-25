import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Animated, Image, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { api } from '../src/services/api';
import { LanguageSwitcher } from '../src/components/LanguageSwitcher';
import { AppBrand } from '../src/components/AppBrand';

const T2D_ICON = require('../assets/images/t2d-icon.png');

const TR: Record<string, Record<string, string>> = {
  no: { subtitle: 'Norsk førerprøve', startQuiz: 'Start quiz', exam: 'Eksamen', accuracy: 'Nøyaktighet', answered: 'Besvart', correct: 'Riktige', premiumCta: 'Premium',  premiumOffer: 'Ubegrenset tilgang · fra 199 kr', premiumActive: 'Premium aktiv', streak: 'dagers rekke', freeLeft: 'gratis igjen', dailyLimitReached: 'Opprett konto for å fortsette', dailyTest: 'Dagens test', moreOptions: 'Flere', accountTitle: 'Opprett konto for å fortsette', accountBody: 'Du har brukt opp 10 gratis spørsmål. Opprett en konto for å fortsette.', accountSignup: 'Opprett konto', accountLogin: 'Logg inn', accountCancel: 'Avbryt' },
  th: { subtitle: 'สอบใบขับขี่นอร์เวย์', startQuiz: 'เริ่มทำแบบทดสอบ', exam: 'สอบ', accuracy: 'ความแม่นยำ', answered: 'ตอบแล้ว', correct: 'ถูกต้อง', premiumCta: 'พรีเมียม', premiumOffer: 'ใช้งานไม่จำกัด · เริ่มต้น 199 kr', premiumActive: 'Premium ใช้งานอยู่', streak: 'วันติดต่อกัน', freeLeft: 'ฟรีเหลือ', dailyLimitReached: 'สร้างบัญชีเพื่อดำเนินการต่อ', dailyTest: 'แบบทดสอบประจำวัน', moreOptions: 'เพิ่มเติม', accountTitle: 'สร้างบัญชีเพื่อดำเนินการต่อ', accountBody: 'คุณใช้คำถามฟรี 10 ข้อหมดแล้ว สร้างบัญชีเพื่อดำเนินการต่อ', accountSignup: 'สร้างบัญชี', accountLogin: 'เข้าสู่ระบบ', accountCancel: 'ยกเลิก' },
  en: { subtitle: 'Norwegian driving test', startQuiz: 'Start quiz', exam: 'Exam', accuracy: 'Accuracy', answered: 'Answered', correct: 'Correct', premiumCta: 'Premium', premiumOffer: 'Unlimited access · from 199 NOK', premiumActive: 'Premium active', streak: 'day streak', freeLeft: 'free left', dailyLimitReached: 'Create account to continue', dailyTest: 'Daily test', moreOptions: 'More', accountTitle: 'Create an account to continue', accountBody: 'You have used your 10 free questions. Create an account to continue.', accountSignup: 'Create account', accountLogin: 'Log in', accountCancel: 'Cancel' },
};

export default function HomeScreen() {
  const router = useRouter();
  const { language, deviceId, setProgress, progress, colors, isPremium, isAuthenticated, freeRemaining, streak, updateStreak } = useAppStore();
  const [loading, setLoading] = useState(true);
  const [dailyDone, setDailyDone] = useState(false);
  const t = TR[language] || TR.en;
  const c = colors;
  const remaining = freeRemaining();
  const locked = !isPremium && remaining <= 0;

  // Subtle press animation for the main CTA
  const ctaScale = useRef(new Animated.Value(1)).current;
  const pressIn = () => Animated.spring(ctaScale, { toValue: 0.97, useNativeDriver: true, speed: 40, bounciness: 0 }).start();
  const pressOut = () => Animated.spring(ctaScale, { toValue: 1, useNativeDriver: true, speed: 30, bounciness: 6 }).start();

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
      <ScrollView contentContainerStyle={st.scroll} showsVerticalScrollIndicator={false}>
        {/* Top bar: brand + language + settings */}
        <View style={st.topBar}>
          <AppBrand size="md" />
          <View style={st.topRight}>
            <LanguageSwitcher size="sm" />
            <TouchableOpacity testID="settings-btn" style={[st.iconBtn, { backgroundColor: c.card, borderColor: c.cardBorder }]} onPress={() => router.push('/settings')}>
              <Ionicons name="settings-outline" size={20} color={c.text} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Brand */}
        <View style={st.brand}>
          <Image source={T2D_ICON} style={st.brandIcon} />
          <Text style={[st.title, { color: c.text }]} testID="home-title">Thai2Drive</Text>
          <Text style={[st.subtitle, { color: c.textMuted }]}>{t.subtitle}</Text>
        </View>

        {/* Streak (only if >0) */}
        {streak > 0 && (
          <View style={st.streakPill}>
            <Text style={st.streakFire}>🔥</Text>
            <Text style={[st.streakText, { color: c.accent }]}>{streak} {t.streak}</Text>
          </View>
        )}

        {/* PRIMARY CTA: Start Quiz */}
        <Animated.View style={{ transform: [{ scale: ctaScale }] }}>
          <TouchableOpacity
            testID="start-quiz-btn"
            style={[st.startBtn, { backgroundColor: locked ? c.letterBg : c.accent }]}
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

        {/* Secondary row: Exam + Daily Test  (subtle, not cards-in-cards) */}
        <View style={st.secondaryRow}>
          <TouchableOpacity
            testID="exam-mode-btn"
            style={[st.secBtn, { borderColor: c.cardBorder }]}
            onPress={() => { if (locked) handleLockedNav(); else router.push({ pathname: '/quiz', params: { mode: 'exam', category: 'all' } }); }}
            activeOpacity={0.7}
          >
            <Ionicons name="school-outline" size={18} color={c.text} />
            <Text style={[st.secText, { color: c.text }]}>{t.exam}</Text>
          </TouchableOpacity>
          <TouchableOpacity
            testID="daily-test-btn"
            style={[st.secBtn, { borderColor: dailyDone ? `${c.correct}60` : c.cardBorder }]}
            onPress={() => router.push({ pathname: '/quiz', params: { mode: 'daily', category: 'all' } })}
            activeOpacity={0.7}
          >
            <Ionicons name={dailyDone ? 'checkmark-circle' : 'today-outline'} size={18} color={dailyDone ? c.correct : c.text} />
            <Text style={[st.secText, { color: dailyDone ? c.correct : c.text }]}>{t.dailyTest}</Text>
          </TouchableOpacity>
        </View>

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
          <TouchableOpacity testID="home-premium-btn" style={[st.premBanner, { backgroundColor: c.accentBg, borderColor: `${c.accent}80` }]} onPress={() => router.push('/paywall')} activeOpacity={0.85}>
            <Ionicons name="diamond" size={18} color={c.accent} />
            <View style={{ flex: 1, marginLeft: 10 }}>
              <Text style={[st.premTitle, { color: c.accent }]}>{t.premiumCta}</Text>
              <Text style={[st.premSub, { color: c.textSecondary }]}>{t.premiumOffer}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={c.accent} />
          </TouchableOpacity>
        ) : (
          <View style={[st.premActive, { backgroundColor: `${c.correct}14`, borderColor: `${c.correct}40` }]}>
            <Ionicons name="diamond" size={16} color={c.correct} />
            <Text style={[st.premActiveText, { color: c.correct }]}>{t.premiumActive}</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  scroll: { padding: 24, paddingBottom: 40 },
  topBar: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 },
  topRight: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  iconBtn: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center', borderWidth: 1 },
  brand: { alignItems: 'center', marginBottom: 20 },
  brandIcon: { width: 64, height: 64, borderRadius: 16, marginBottom: 14 },
  title: { fontSize: 34, fontWeight: '800', letterSpacing: -1 },
  subtitle: { fontSize: 14, marginTop: 4 },
  streakPill: { flexDirection: 'row', alignItems: 'center', alignSelf: 'center', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 14, gap: 6, marginBottom: 20 },
  streakFire: { fontSize: 15 },
  streakText: { fontSize: 13, fontWeight: '700' },
  startBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 18, paddingVertical: 20, gap: 10, marginBottom: 8 },
  startText: { fontSize: 18, fontWeight: '800', letterSpacing: 0.2 },
  freeHint: { fontSize: 12, textAlign: 'center', marginBottom: 24 },
  secondaryRow: { flexDirection: 'row', gap: 10, marginBottom: 32 },
  secBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, paddingVertical: 13, borderRadius: 12, borderWidth: 1 },
  secText: { fontSize: 14, fontWeight: '600' },
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
});
