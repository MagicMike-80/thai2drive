import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { api } from '../src/services/api';

const { width } = Dimensions.get('window');

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
  const { language, setLanguage, deviceId, setProgress, progress } = useAppStore();
  const [loading, setLoading] = useState(true);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const t = TRANSLATIONS[language] || TRANSLATIONS.no;

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
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator testID="home-loading" size="large" color="#F59E0B" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.title} testID="home-title">{t.title}</Text>
            <Text style={styles.subtitle}>{t.subtitle}</Text>
          </View>
          <View style={styles.languageSelector}>
            {LANGUAGES.map((lang) => (
              <TouchableOpacity
                key={lang.code}
                testID={`lang-btn-${lang.code}`}
                style={[styles.langButton, language === lang.code && styles.langButtonActive]}
                onPress={() => setLanguage(lang.code)}
                activeOpacity={0.7}
              >
                <Text style={styles.langFlag}>{lang.flag}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Stats Card */}
        <View style={styles.statsCard}>
          <Text style={styles.statsTitle}>{t.stats}</Text>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{progress.total_questions_answered}</Text>
              <Text style={styles.statLabel}>{t.answered}</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{progress.correct_answers}</Text>
              <Text style={styles.statLabel}>{t.correct}</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={[styles.statValue, { color: accuracy >= 70 ? '#10B981' : accuracy > 0 ? '#EF4444' : '#F8FAFC' }]}>
                {accuracy}%
              </Text>
              <Text style={styles.statLabel}>{t.accuracy}</Text>
            </View>
          </View>
        </View>

        {/* Mode Cards */}
        <TouchableOpacity
          testID="practice-mode-btn"
          style={styles.practiceCard}
          onPress={() => navigateToQuiz('practice')}
          activeOpacity={0.8}
        >
          <View style={styles.modeHeader}>
            <View style={[styles.modeIconBg, { backgroundColor: 'rgba(16, 185, 129, 0.15)' }]}>
              <Ionicons name="book-outline" size={28} color="#10B981" />
            </View>
            <Ionicons name="chevron-forward" size={22} color="#64748B" />
          </View>
          <Text style={styles.modeTitle}>{t.practice}</Text>
          <Text style={styles.modeDesc}>{t.practiceDesc}</Text>
        </TouchableOpacity>

        <TouchableOpacity
          testID="exam-mode-btn"
          style={styles.examCard}
          onPress={() => navigateToQuiz('exam')}
          activeOpacity={0.8}
        >
          <View style={styles.modeHeader}>
            <View style={[styles.modeIconBg, { backgroundColor: 'rgba(245, 158, 11, 0.15)' }]}>
              <Ionicons name="school-outline" size={28} color="#F59E0B" />
            </View>
            <Ionicons name="chevron-forward" size={22} color="#64748B" />
          </View>
          <Text style={styles.modeTitle}>{t.exam}</Text>
          <Text style={styles.modeDesc}>{t.examDesc}</Text>
        </TouchableOpacity>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <TouchableOpacity
            testID="history-btn"
            style={styles.actionButton}
            onPress={() => router.push('/history')}
            activeOpacity={0.7}
          >
            <Ionicons name="time-outline" size={22} color="#94A3B8" />
            <Text style={styles.actionText}>{t.history}</Text>
          </TouchableOpacity>
          <TouchableOpacity
            testID="bookmarks-btn"
            style={styles.actionButton}
            onPress={() => router.push('/bookmarks')}
            activeOpacity={0.7}
          >
            <Ionicons name="bookmark-outline" size={22} color="#94A3B8" />
            <Text style={styles.actionText}>{t.bookmarks}</Text>
          </TouchableOpacity>
        </View>

        {/* Questions count */}
        <View style={styles.footerInfo}>
          <Ionicons name="library-outline" size={16} color="#64748B" />
          <Text style={styles.footerText}>{totalQuestions} {t.questionsAvailable}</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  scrollContent: { padding: 20, paddingBottom: 40 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28 },
  title: { fontSize: 34, fontWeight: '800', color: '#F8FAFC', letterSpacing: -1 },
  subtitle: { fontSize: 14, color: '#94A3B8', marginTop: 4 },
  languageSelector: { flexDirection: 'row', gap: 8 },
  langButton: { width: 42, height: 42, borderRadius: 21, backgroundColor: '#1E293B', justifyContent: 'center', alignItems: 'center', borderWidth: 2, borderColor: 'transparent' },
  langButtonActive: { borderColor: '#F59E0B', backgroundColor: 'rgba(245, 158, 11, 0.1)' },
  langFlag: { fontSize: 20 },
  statsCard: { backgroundColor: '#1E293B', borderRadius: 20, padding: 20, marginBottom: 20, borderWidth: 1, borderColor: 'rgba(51, 65, 85, 0.5)' },
  statsTitle: { fontSize: 13, color: '#64748B', textTransform: 'uppercase', letterSpacing: 1.5, fontWeight: '700', marginBottom: 16 },
  statsRow: { flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center' },
  statItem: { alignItems: 'center', flex: 1 },
  statValue: { fontSize: 30, fontWeight: '800', color: '#F8FAFC' },
  statLabel: { fontSize: 12, color: '#94A3B8', marginTop: 4 },
  statDivider: { width: 1, height: 44, backgroundColor: 'rgba(51, 65, 85, 0.5)' },
  practiceCard: { backgroundColor: '#1E293B', borderRadius: 20, padding: 20, marginBottom: 12, borderWidth: 1, borderColor: 'rgba(16, 185, 129, 0.25)' },
  examCard: { backgroundColor: '#1E293B', borderRadius: 20, padding: 20, marginBottom: 20, borderWidth: 1, borderColor: 'rgba(245, 158, 11, 0.25)' },
  modeHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  modeIconBg: { width: 52, height: 52, borderRadius: 16, justifyContent: 'center', alignItems: 'center' },
  modeTitle: { fontSize: 20, fontWeight: '700', color: '#F8FAFC', marginBottom: 4 },
  modeDesc: { fontSize: 14, color: '#94A3B8', lineHeight: 20 },
  quickActions: { flexDirection: 'row', gap: 12 },
  actionButton: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#1E293B', borderRadius: 16, paddingVertical: 16, gap: 8, borderWidth: 1, borderColor: 'rgba(51, 65, 85, 0.5)' },
  actionText: { fontSize: 14, fontWeight: '600', color: '#94A3B8' },
  footerInfo: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginTop: 24, gap: 6 },
  footerText: { fontSize: 13, color: '#64748B' },
});
