import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { api } from '../src/services/api';

const LANGUAGES = [
  { code: 'no', label: 'NO', flag: '🇳🇴' },
  { code: 'th', label: 'TH', flag: '🇹🇭' },
  { code: 'en', label: 'EN', flag: '🇬🇧' },
];

const TRANSLATIONS: Record<string, Record<string, string>> = {
  no: {
    title: 'Thai2Drive',
    subtitle: 'Norsk førerprøve quiz',
    practice: 'Øvingsmodus',
    exam: 'Eksamensmodus',
    practiceDesc: 'Øv deg uten press, velg kategori',
    examDesc: '45 spørsmål · 90 min · 85% for å bestå',
    history: 'Historikk',
    bookmarks: 'Bokmerker',
    stats: 'Din statistikk',
    answered: 'Besvart',
    correct: 'Riktige',
    accuracy: 'Nøyaktighet',
    questionsAvailable: 'spørsmål tilgjengelig',
  },
  th: {
    title: 'Thai2Drive',
    subtitle: 'แบบทดสอบใบขับขี่นอร์เวย์',
    practice: 'โหมดฝึกซ้อม',
    exam: 'โหมดสอบ',
    practiceDesc: 'ฝึกซ้อมไม่มีเวลา เลือกหมวดหมู่',
    examDesc: '45 ข้อ · 90 นาที · 85% ผ่าน',
    history: 'ประวัติ',
    bookmarks: 'บุ๊คมาร์ค',
    stats: 'สถิติของคุณ',
    answered: 'ตอบแล้ว',
    correct: 'ถูกต้อง',
    accuracy: 'ความแม่นยำ',
    questionsAvailable: 'คำถามพร้อมใช้',
  },
  en: {
    title: 'Thai2Drive',
    subtitle: 'Norwegian Driving Theory Quiz',
    practice: 'Practice Mode',
    exam: 'Exam Mode',
    practiceDesc: 'Practice without pressure, pick category',
    examDesc: '45 questions · 90 min · 85% to pass',
    history: 'History',
    bookmarks: 'Bookmarks',
    stats: 'Your Statistics',
    answered: 'Answered',
    correct: 'Correct',
    accuracy: 'Accuracy',
    questionsAvailable: 'questions available',
  },
};

export default function HomeScreen() {
  const router = useRouter();
  const { language, setLanguage, deviceId, setProgress, progress, colors, isPremium, freeRemaining } = useAppStore();
  const [loading, setLoading] = useState(true);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const t = TRANSLATIONS[language] || TRANSLATIONS.no;
  const c = colors;
  const remaining = freeRemaining();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      await api.seedDatabase();
      const userProgress = await api.getProgress(deviceId);
      setProgress(userProgress);
      const cats = await api.getCategories();
      setTotalQuestions(cats.reduce((s: number, c: { count: number }) => s + c.count, 0));
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const navigateToQuiz = (mode: 'practice' | 'exam') => {
    if (mode === 'exam') {
      router.push({ pathname: '/quiz', params: { mode: 'exam', category: 'all' } });
    } else {
      router.push({ pathname: '/categories', params: { mode } });
    }
  };

  const accuracy = progress.total_questions_answered > 0
    ? Math.round((progress.correct_answers / progress.total_questions_answered) * 100)
    : 0;

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: c.bg }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator testID="home-loading" size="large" color={c.accent} />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: c.bg }]}>
      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={[styles.title, { color: c.text }]} testID="home-title">{t.title}</Text>
            <Text style={[styles.subtitle, { color: c.textSecondary }]}>{t.subtitle}</Text>
          </View>
          <View style={styles.headerRight}>
            <TouchableOpacity
              testID="settings-btn"
              style={[styles.settingsBtn, { backgroundColor: c.card }]}
              onPress={() => router.push('/settings')}
              activeOpacity={0.7}
            >
              <Ionicons name="settings-outline" size={20} color={c.textSecondary} />
            </TouchableOpacity>
          </View>
        </View>

        {/* Language selector */}
        <View style={styles.languageSelector}>
          {LANGUAGES.map((lang) => (
            <TouchableOpacity
              key={lang.code}
              testID={`lang-btn-${lang.code}`}
              style={[styles.langButton, { backgroundColor: c.card, borderColor: language === lang.code ? c.accent : 'transparent' }]}
              onPress={() => setLanguage(lang.code)}
              activeOpacity={0.7}
            >
              <Text style={styles.langFlag}>{lang.flag}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Stats Card */}
        <View style={[styles.statsCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
          <Text style={[styles.statsTitle, { color: c.textMuted }]}>{t.stats}</Text>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={[styles.statValue, { color: c.text }]}>{progress.total_questions_answered}</Text>
              <Text style={[styles.statLabel, { color: c.textSecondary }]}>{t.answered}</Text>
            </View>
            <View style={[styles.statDivider, { backgroundColor: c.divider }]} />
            <View style={styles.statItem}>
              <Text style={[styles.statValue, { color: c.text }]}>{progress.correct_answers}</Text>
              <Text style={[styles.statLabel, { color: c.textSecondary }]}>{t.correct}</Text>
            </View>
            <View style={[styles.statDivider, { backgroundColor: c.divider }]} />
            <View style={styles.statItem}>
              <Text style={[styles.statValue, { color: accuracy >= 70 ? c.correct : accuracy > 0 ? c.incorrect : c.text }]}>
                {accuracy}%
              </Text>
              <Text style={[styles.statLabel, { color: c.textSecondary }]}>{t.accuracy}</Text>
            </View>
          </View>
        </View>

        {/* Mode Cards */}
        <TouchableOpacity
          testID="practice-mode-btn"
          style={[styles.practiceCard, { backgroundColor: c.card, borderColor: `${c.correct}40` }]}
          onPress={() => navigateToQuiz('practice')}
          activeOpacity={0.8}
        >
          <View style={styles.modeHeader}>
            <View style={[styles.modeIconBg, { backgroundColor: `${c.correct}18` }]}>
              <Ionicons name="book-outline" size={28} color={c.correct} />
            </View>
            <Ionicons name="chevron-forward" size={22} color={c.textMuted} />
          </View>
          <Text style={[styles.modeTitle, { color: c.text }]}>{t.practice}</Text>
          <Text style={[styles.modeDesc, { color: c.textSecondary }]}>{t.practiceDesc}</Text>
        </TouchableOpacity>

        <TouchableOpacity
          testID="exam-mode-btn"
          style={[styles.examCard, { backgroundColor: c.card, borderColor: `${c.accent}40` }]}
          onPress={() => navigateToQuiz('exam')}
          activeOpacity={0.8}
        >
          <View style={styles.modeHeader}>
            <View style={[styles.modeIconBg, { backgroundColor: c.accentBg }]}>
              <Ionicons name="school-outline" size={28} color={c.accent} />
            </View>
            <Ionicons name="chevron-forward" size={22} color={c.textMuted} />
          </View>
          <Text style={[styles.modeTitle, { color: c.text }]}>{t.exam}</Text>
          <Text style={[styles.modeDesc, { color: c.textSecondary }]}>{t.examDesc}</Text>
        </TouchableOpacity>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <TouchableOpacity testID="history-btn" style={[styles.actionButton, { backgroundColor: c.card, borderColor: c.cardBorder }]} onPress={() => router.push('/history')} activeOpacity={0.7}>
            <Ionicons name="time-outline" size={22} color={c.textSecondary} />
            <Text style={[styles.actionText, { color: c.textSecondary }]}>{t.history}</Text>
          </TouchableOpacity>
          <TouchableOpacity testID="bookmarks-btn" style={[styles.actionButton, { backgroundColor: c.card, borderColor: c.cardBorder }]} onPress={() => router.push('/bookmarks')} activeOpacity={0.7}>
            <Ionicons name="bookmark-outline" size={22} color={c.textSecondary} />
            <Text style={[styles.actionText, { color: c.textSecondary }]}>{t.bookmarks}</Text>
          </TouchableOpacity>
        </View>

        {/* Premium Banner */}
        {!isPremium ? (
          <TouchableOpacity
            testID="home-premium-btn"
            style={[styles.premiumBanner, { backgroundColor: c.card, borderColor: `${c.accent}40` }]}
            onPress={() => router.push('/paywall')}
            activeOpacity={0.8}
          >
            <View style={[styles.premiumIconBg, { backgroundColor: c.accentBg }]}>
              <Ionicons name="diamond" size={20} color={c.accent} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={[styles.premiumTitle, { color: c.text }]}>Unlock Premium</Text>
              <Text style={[styles.premiumSub, { color: c.textSecondary }]}>
                {remaining > 0 ? `${remaining} free questions left` : 'Free limit reached'}
              </Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={c.accent} />
          </TouchableOpacity>
        ) : (
          <View style={[styles.premiumBadge, { backgroundColor: `${c.correct}12`, borderColor: `${c.correct}30` }]}>
            <Ionicons name="diamond" size={16} color={c.correct} />
            <Text style={[styles.premiumBadgeText, { color: c.correct }]}>Premium Active</Text>
          </View>
        )}

        <View style={styles.footerInfo}>
          <Ionicons name="library-outline" size={16} color={c.textMuted} />
          <Text style={[styles.footerText, { color: c.textMuted }]}>{totalQuestions} {t.questionsAvailable}</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  scrollContent: { padding: 20, paddingBottom: 40 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 },
  title: { fontSize: 34, fontWeight: '800', letterSpacing: -1 },
  subtitle: { fontSize: 14, marginTop: 4 },
  headerRight: { flexDirection: 'row', gap: 8 },
  settingsBtn: { width: 42, height: 42, borderRadius: 21, justifyContent: 'center', alignItems: 'center' },
  languageSelector: { flexDirection: 'row', gap: 8, marginBottom: 20 },
  langButton: { width: 42, height: 42, borderRadius: 21, justifyContent: 'center', alignItems: 'center', borderWidth: 2 },
  langFlag: { fontSize: 20 },
  statsCard: { borderRadius: 20, padding: 20, marginBottom: 20, borderWidth: 1 },
  statsTitle: { fontSize: 13, textTransform: 'uppercase', letterSpacing: 1.5, fontWeight: '700', marginBottom: 16 },
  statsRow: { flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center' },
  statItem: { alignItems: 'center', flex: 1 },
  statValue: { fontSize: 30, fontWeight: '800' },
  statLabel: { fontSize: 12, marginTop: 4 },
  statDivider: { width: 1, height: 44 },
  practiceCard: { borderRadius: 20, padding: 20, marginBottom: 12, borderWidth: 1 },
  examCard: { borderRadius: 20, padding: 20, marginBottom: 20, borderWidth: 1 },
  modeHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  modeIconBg: { width: 52, height: 52, borderRadius: 16, justifyContent: 'center', alignItems: 'center' },
  modeTitle: { fontSize: 20, fontWeight: '700', marginBottom: 4 },
  modeDesc: { fontSize: 14, lineHeight: 20 },
  quickActions: { flexDirection: 'row', gap: 12 },
  actionButton: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', borderRadius: 16, paddingVertical: 16, gap: 8, borderWidth: 1 },
  actionText: { fontSize: 14, fontWeight: '600' },
  footerInfo: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginTop: 24, gap: 6 },
  footerText: { fontSize: 13 },
  premiumBanner: { flexDirection: 'row', alignItems: 'center', borderRadius: 16, padding: 14, marginTop: 16, borderWidth: 1, gap: 12 },
  premiumIconBg: { width: 40, height: 40, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  premiumTitle: { fontSize: 15, fontWeight: '700' },
  premiumSub: { fontSize: 12, marginTop: 2 },
  premiumBadge: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', borderRadius: 12, paddingVertical: 10, marginTop: 16, gap: 6, borderWidth: 1 },
  premiumBadgeText: { fontSize: 13, fontWeight: '700' },
});
