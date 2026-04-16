import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { api } from '../src/services/api';

const LANGS = [
  { code: 'th', flag: '🇹🇭' },
  { code: 'no', flag: '🇳🇴' },
  { code: 'en', flag: '🇬🇧' },
];

const TR: Record<string, Record<string, string>> = {
  no: { subtitle: 'Norsk førerprøve', startQuiz: 'Start Quiz', practice: 'Øving', exam: 'Eksamen', stats: 'Din fremgang', answered: 'Besvart', correct: 'Riktige', accuracy: 'Nøyaktighet', history: 'Historikk', bookmarks: 'Bokmerker', premiumCta: 'Lås opp full tilgang – over 5000 spørsmål', premiumOffer: 'Begrenset tilbud for de første 50', premiumPrice: '199 kr / mnd', getPremium: 'Få Premium', premiumActive: 'Premium Aktiv', streak: 'dagers rekke', freeLeft: 'gratis igjen' },
  th: { subtitle: 'สอบใบขับขี่นอร์เวย์', startQuiz: 'เริ่มทำแบบทดสอบ', practice: 'ฝึกซ้อม', exam: 'สอบ', stats: 'ความก้าวหน้า', answered: 'ตอบแล้ว', correct: 'ถูกต้อง', accuracy: 'ความแม่นยำ', history: 'ประวัติ', bookmarks: 'บุ๊คมาร์ค', premiumCta: 'ปลดล็อคเข้าถึงทั้งหมด – กว่า 5000 ข้อ', premiumOffer: 'ข้อเสนอพิเศษสำหรับ 50 คนแรก', premiumPrice: '199 kr / เดือน', getPremium: 'รับ Premium', premiumActive: 'Premium ใช้งานอยู่', streak: 'วันติดต่อกัน', freeLeft: 'ฟรีที่เหลือ' },
  en: { subtitle: 'Norwegian driving test', startQuiz: 'Start Quiz', practice: 'Practice', exam: 'Exam', stats: 'Your Progress', answered: 'Answered', correct: 'Correct', accuracy: 'Accuracy', history: 'History', bookmarks: 'Bookmarks', premiumCta: 'Unlock full access – over 5,000 questions', premiumOffer: 'Limited offer for first 50 users', premiumPrice: '199 kr / month', getPremium: 'Get Premium', premiumActive: 'Premium Active', streak: 'day streak', freeLeft: 'free left' },
};

export default function HomeScreen() {
  const router = useRouter();
  const { language, setLanguage, deviceId, setProgress, progress, colors, isPremium, freeRemaining, streak, updateStreak } = useAppStore();
  const [loading, setLoading] = useState(true);
  const t = TR[language] || TR.no;
  const c = colors;
  const remaining = freeRemaining();

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      await api.seedDatabase();
      const p = await api.getProgress(deviceId);
      setProgress(p);
      await updateStreak();
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const accuracy = progress.total_questions_answered > 0
    ? Math.round((progress.correct_answers / progress.total_questions_answered) * 100) : 0;

  if (loading) return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <View style={st.center}><ActivityIndicator testID="home-loading" size="large" color={c.accent} /></View>
    </SafeAreaView>
  );

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <ScrollView contentContainerStyle={st.scroll} showsVerticalScrollIndicator={false}>
        {/* Top bar: flag + lang selector + settings */}
        <View style={st.topBar}>
          <Text style={st.thaiFlag}>🇹🇭</Text>
          <View style={st.langRow}>
            {LANGS.map((l) => (
              <TouchableOpacity key={l.code} testID={`lang-btn-${l.code}`}
                style={[st.langBtn, { backgroundColor: language === l.code ? c.accentBg : c.card, borderColor: language === l.code ? c.accent : 'transparent' }]}
                onPress={() => setLanguage(l.code)}>
                <Text style={st.langFlag}>{l.flag}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <TouchableOpacity testID="settings-btn" style={[st.settingsBtn, { backgroundColor: c.card }]} onPress={() => router.push('/settings')}>
            <Ionicons name="settings-outline" size={18} color={c.textSecondary} />
          </TouchableOpacity>
        </View>

        {/* Title */}
        <Text style={[st.title, { color: c.text }]} testID="home-title">Thai2Drive</Text>
        <Text style={[st.subtitle, { color: c.textSecondary }]}>{t.subtitle}</Text>

        {/* Streak */}
        {streak > 0 && (
          <View style={[st.streakRow, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={st.streakFire}>🔥</Text>
            <Text style={[st.streakText, { color: c.accent }]}>{streak} {t.streak}</Text>
          </View>
        )}

        {/* Big Start Quiz Button */}
        <TouchableOpacity testID="start-quiz-btn" style={[st.startBtn, { backgroundColor: c.accent }]}
          onPress={() => router.push({ pathname: '/categories', params: { mode: 'practice' } })} activeOpacity={0.85}>
          <Ionicons name="play" size={24} color="#0F172A" />
          <Text style={st.startText}>{t.startQuiz}</Text>
        </TouchableOpacity>

        {/* Free remaining for non-premium */}
        {!isPremium && (
          <Text style={[st.freeHint, { color: c.textMuted }]}>{remaining} {t.freeLeft}</Text>
        )}

        {/* Exam button */}
        <TouchableOpacity testID="exam-mode-btn" style={[st.examBtn, { backgroundColor: c.card, borderColor: c.accent }]}
          onPress={() => router.push({ pathname: '/quiz', params: { mode: 'exam', category: 'all' } })} activeOpacity={0.85}>
          <Ionicons name="school" size={20} color={c.accent} />
          <Text style={[st.examText, { color: c.accent }]}>{t.exam}</Text>
        </TouchableOpacity>

        {/* Mode shortcuts */}
        <View style={st.modesRow}>
          <TouchableOpacity testID="practice-mode-btn" style={[st.modeChip, { backgroundColor: c.card, borderColor: c.cardBorder }]}
            onPress={() => router.push({ pathname: '/categories', params: { mode: 'practice' } })}>
            <Ionicons name="book-outline" size={18} color={c.correct} />
            <Text style={[st.modeText, { color: c.text }]}>{t.practice}</Text>
          </TouchableOpacity>
          <TouchableOpacity testID="history-btn" style={[st.modeChip, { backgroundColor: c.card, borderColor: c.cardBorder }]}
            onPress={() => router.push('/history')}>
            <Ionicons name="time-outline" size={18} color={c.textSecondary} />
            <Text style={[st.modeText, { color: c.text }]}>{t.history}</Text>
          </TouchableOpacity>
          <TouchableOpacity testID="bookmarks-btn" style={[st.modeChip, { backgroundColor: c.card, borderColor: c.cardBorder }]}
            onPress={() => router.push('/bookmarks')}>
            <Ionicons name="bookmark-outline" size={18} color={c.textSecondary} />
            <Text style={[st.modeText, { color: c.text }]}>{t.bookmarks}</Text>
          </TouchableOpacity>
        </View>

        {/* Progress */}
        <View style={[st.progressCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
          <Text style={[st.sectionTitle, { color: c.textMuted }]}>{t.stats}</Text>
          <View style={st.statsRow}>
            <View style={st.statCol}>
              <Text style={[st.statVal, { color: c.text }]}>{progress.total_questions_answered}</Text>
              <Text style={[st.statLbl, { color: c.textSecondary }]}>{t.answered}</Text>
            </View>
            <View style={[st.divider, { backgroundColor: c.divider }]} />
            <View style={st.statCol}>
              <Text style={[st.statVal, { color: c.text }]}>{progress.correct_answers}</Text>
              <Text style={[st.statLbl, { color: c.textSecondary }]}>{t.correct}</Text>
            </View>
            <View style={[st.divider, { backgroundColor: c.divider }]} />
            <View style={st.statCol}>
              <Text style={[st.statVal, { color: accuracy >= 70 ? c.correct : accuracy > 0 ? c.incorrect : c.text }]}>{accuracy}%</Text>
              <Text style={[st.statLbl, { color: c.textSecondary }]}>{t.accuracy}</Text>
            </View>
          </View>
        </View>

        {/* Premium Banner */}
        {!isPremium ? (
          <TouchableOpacity testID="home-premium-btn" style={[st.premBanner, { borderColor: c.accent }]} onPress={() => router.push('/paywall')} activeOpacity={0.85}>
            <Text style={st.premRocket}>🚀</Text>
            <Text style={[st.premCta, { color: c.text }]}>{t.premiumCta}</Text>
            <Text style={[st.premOffer, { color: c.textSecondary }]}>{t.premiumOffer}</Text>
            <View style={st.premPriceRow}>
              <Text style={[st.premPrice, { color: c.accent }]}>{t.premiumPrice}</Text>
            </View>
            <View style={[st.premBtn, { backgroundColor: c.accent }]}>
              <Ionicons name="diamond" size={16} color="#0F172A" />
              <Text style={st.premBtnText}>{t.getPremium}</Text>
            </View>
          </TouchableOpacity>
        ) : (
          <View style={[st.premActive, { backgroundColor: `${c.correct}10`, borderColor: `${c.correct}30` }]}>
            <Ionicons name="diamond" size={18} color={c.correct} />
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
  scroll: { padding: 20, paddingBottom: 40 },
  topBar: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  thaiFlag: { fontSize: 28, marginRight: 12 },
  langRow: { flex: 1, flexDirection: 'row', gap: 6 },
  langBtn: { width: 38, height: 38, borderRadius: 19, justifyContent: 'center', alignItems: 'center', borderWidth: 2 },
  langFlag: { fontSize: 18 },
  settingsBtn: { width: 38, height: 38, borderRadius: 19, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 36, fontWeight: '800', letterSpacing: -1 },
  subtitle: { fontSize: 15, marginTop: 2, marginBottom: 18 },
  streakRow: { flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, gap: 6, borderWidth: 1, marginBottom: 18 },
  streakFire: { fontSize: 18 },
  streakText: { fontSize: 14, fontWeight: '700' },
  startBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 18, paddingVertical: 20, gap: 10, marginBottom: 8 },
  startText: { fontSize: 20, fontWeight: '800', color: '#0F172A' },
  freeHint: { fontSize: 12, textAlign: 'center', marginBottom: 12 },
  examBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 14, gap: 8, marginBottom: 14, borderWidth: 1.5 },
  examText: { fontSize: 16, fontWeight: '700' },
  modesRow: { flexDirection: 'row', gap: 8, marginBottom: 16 },
  modeChip: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', borderRadius: 12, paddingVertical: 11, gap: 5, borderWidth: 1 },
  modeText: { fontSize: 13, fontWeight: '600' },
  progressCard: { borderRadius: 16, padding: 16, marginBottom: 16, borderWidth: 1 },
  sectionTitle: { fontSize: 11, textTransform: 'uppercase', letterSpacing: 1.5, fontWeight: '700', marginBottom: 12 },
  statsRow: { flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center' },
  statCol: { alignItems: 'center', flex: 1 },
  statVal: { fontSize: 26, fontWeight: '800' },
  statLbl: { fontSize: 11, marginTop: 2 },
  divider: { width: 1, height: 36 },
  premBanner: { borderRadius: 20, padding: 20, borderWidth: 1.5, alignItems: 'center', marginBottom: 12 },
  premRocket: { fontSize: 32, marginBottom: 8 },
  premCta: { fontSize: 16, fontWeight: '700', textAlign: 'center', lineHeight: 22, marginBottom: 4 },
  premOffer: { fontSize: 13, textAlign: 'center', marginBottom: 10 },
  premPriceRow: { marginBottom: 14 },
  premPrice: { fontSize: 22, fontWeight: '800' },
  premBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', borderRadius: 12, paddingVertical: 12, paddingHorizontal: 32, gap: 6 },
  premBtnText: { fontSize: 15, fontWeight: '700', color: '#0F172A' },
  premActive: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', borderRadius: 12, paddingVertical: 12, gap: 6, borderWidth: 1, marginBottom: 12 },
  premActiveText: { fontSize: 14, fontWeight: '700' },
});
