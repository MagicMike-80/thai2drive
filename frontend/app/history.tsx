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
import { api, QuizAttempt } from '../src/services/api';

const TRANSLATIONS = {
  no: {
    title: 'Quiz Historikk',
    noHistory: 'Ingen quiz historikk ennå',
    startQuiz: 'Start din første quiz!',
    back: 'Tilbake',
    practice: 'Øving',
    exam: 'Eksamen',
    daily: 'Dagstest',
    smart: 'Smart øving',
    questions: 'spørsmål',
    correct: 'riktige',
    passed: 'Bestått',
    failed: 'Ikke bestått',
  },
  th: {
    title: 'ประวัติแบบทดสอบ',
    noHistory: 'ยังไม่มีประวัติแบบทดสอบ',
    startQuiz: 'เริ่มแบบทดสอบแรกของคุณ!',
    back: 'กลับ',
    practice: 'ฝึกซ้อม',
    exam: 'สอบ',
    daily: 'ทดสอบประจำวัน',
    smart: 'ฝึกอัจฉริยะ',
    questions: 'คำถาม',
    correct: 'ถูกต้อง',
    passed: 'ผ่าน',
    failed: 'ไม่ผ่าน',
  },
  en: {
    title: 'Quiz History',
    noHistory: 'No quiz history yet',
    startQuiz: 'Start your first quiz!',
    back: 'Back',
    practice: 'Practice',
    exam: 'Exam',
    daily: 'Daily test',
    smart: 'Smart practice',
    questions: 'questions',
    correct: 'correct',
    passed: 'Passed',
    failed: 'Failed',
  },
};

export default function HistoryScreen() {
  const router = useRouter();
  const { language, deviceId, colors } = useAppStore();
  const c = colors;
  const [attempts, setAttempts] = useState<QuizAttempt[]>([]);
  const [loading, setLoading] = useState(true);
  const t = TRANSLATIONS[language as keyof typeof TRANSLATIONS] || TRANSLATIONS.en;

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await api.getQuizAttempts(deviceId);
      setAttempts(data);
    } catch (error) {
      console.error('Error loading history:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(language === 'th' ? 'th-TH' : language === 'no' ? 'nb-NO' : 'en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return '#22C55E';
    if (percentage >= 60) return '#F59E0B';
    return '#EF4444';
  };

  const modeLabel = (mode: string) => {
    if (mode === 'exam') return t.exam;
    if (mode === 'daily') return t.daily;
    if (mode === 'smart') return t.smart;
    return t.practice;
  };

  const modeIcon = (mode: string) => {
    if (mode === 'exam') return 'school-outline';
    if (mode === 'daily') return 'calendar-outline';
    if (mode === 'smart') return 'bulb-outline';
    return 'book-outline';
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: c.bg }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={c.accent} />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: c.bg }]}>
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: c.divider }]}>
        <TouchableOpacity
          style={[styles.backButton, { backgroundColor: c.card }]}
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={22} color={c.text} />
        </TouchableOpacity>
        <Text style={[styles.title, { color: c.text }]}>{t.title}</Text>
        <View style={styles.placeholder} />
      </View>

      {attempts.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="time-outline" size={64} color={c.textMuted} />
          <Text style={[styles.emptyText, { color: c.textSecondary }]}>{t.noHistory}</Text>
          <Text style={[styles.emptySubtext, { color: c.textMuted }]}>{t.startQuiz}</Text>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.scrollContent}>
          {attempts.map((attempt) => (
            <View key={attempt.id} style={[styles.attemptCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
              <View style={styles.attemptHeader}>
                <View style={[styles.modeBadge, { backgroundColor: c.bg }]}>
                  <Ionicons
                    name={modeIcon(attempt.mode) as any}
                    size={14}
                    color={c.textSecondary}
                  />
                  <Text style={[styles.modeText, { color: c.textSecondary }]}>
                    {modeLabel(attempt.mode)}
                  </Text>
                </View>
                <Text style={[styles.dateText, { color: c.textMuted }]}>{formatDate(attempt.completed_at)}</Text>
              </View>

              <View style={styles.attemptBody}>
                <View style={styles.scoreContainer}>
                  <Text style={[styles.scoreText, { color: getScoreColor(attempt.score_percentage) }]}>
                    {Math.round(attempt.score_percentage)}%
                  </Text>
                  {attempt.passed !== undefined && (
                    <Text style={{ fontSize: 10, color: attempt.passed ? '#22C55E' : '#EF4444', fontWeight: '700', textAlign: 'center' }}>
                      {attempt.passed ? t.passed : t.failed}
                    </Text>
                  )}
                </View>

                <View style={styles.detailsContainer}>
                  <Text style={[styles.detailText, { color: c.textSecondary }]}>
                    {attempt.correct_answers} {t.correct} / {attempt.total_questions} {t.questions}
                  </Text>
                  {attempt.category && (
                    <Text style={[styles.categoryText, { color: c.textMuted }]}>{attempt.category}</Text>
                  )}
                </View>
              </View>

              <View style={[styles.progressBar, { backgroundColor: c.progressBg || c.divider }]}>
                <View
                  style={[
                    styles.progressFill,
                    { width: `${Math.min(100, attempt.score_percentage)}%`, backgroundColor: getScoreColor(attempt.score_percentage) },
                  ]}
                />
              </View>
            </View>
          ))}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container:        { flex: 1 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header:           { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1 },
  backButton:       { width: 38, height: 38, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  title:            { fontSize: 18, fontWeight: '700' },
  placeholder:      { width: 38 },
  emptyContainer:   { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  emptyText:        { fontSize: 17, marginTop: 16 },
  emptySubtext:     { fontSize: 14, marginTop: 8 },
  scrollContent:    { padding: 16, paddingBottom: 32 },
  attemptCard:      { borderRadius: 16, padding: 16, marginBottom: 10, borderWidth: 1 },
  attemptHeader:    { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  modeBadge:        { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, gap: 4 },
  modeText:         { fontSize: 12, fontWeight: '600' },
  dateText:         { fontSize: 12 },
  attemptBody:      { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  scoreContainer:   { marginRight: 16, alignItems: 'center' },
  scoreText:        { fontSize: 32, fontWeight: '800' },
  detailsContainer: { flex: 1 },
  detailText:       { fontSize: 14 },
  categoryText:     { fontSize: 12, marginTop: 4 },
  progressBar:      { height: 4, borderRadius: 2 },
  progressFill:     { height: '100%', borderRadius: 2 },
});
