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
    questions: 'spørsmål',
    correct: 'riktige',
  },
  th: {
    title: 'ประวัติแบบทดสอบ',
    noHistory: 'ยังไม่มีประวัติแบบทดสอบ',
    startQuiz: 'เริ่มแบบทดสอบแรกของคุณ!',
    back: 'กลับ',
    practice: 'ฝึกซ้อม',
    exam: 'สอบ',
    questions: 'คำถาม',
    correct: 'ถูกต้อง',
  },
  en: {
    title: 'Quiz History',
    noHistory: 'No quiz history yet',
    startQuiz: 'Start your first quiz!',
    back: 'Back',
    practice: 'Practice',
    exam: 'Exam',
    questions: 'questions',
    correct: 'correct',
  },
};

export default function HistoryScreen() {
  const router = useRouter();
  const { language, deviceId } = useAppStore();
  const [attempts, setAttempts] = useState<QuizAttempt[]>([]);
  const [loading, setLoading] = useState(true);
  const t = TRANSLATIONS[language as keyof typeof TRANSLATIONS];

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

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#3B82F6" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={24} color="#FFFFFF" />
        </TouchableOpacity>
        <Text style={styles.title}>{t.title}</Text>
        <View style={styles.placeholder} />
      </View>

      {attempts.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="time-outline" size={64} color="#334155" />
          <Text style={styles.emptyText}>{t.noHistory}</Text>
          <Text style={styles.emptySubtext}>{t.startQuiz}</Text>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.scrollContent}>
          {attempts.map((attempt) => (
            <View key={attempt.id} style={styles.attemptCard}>
              <View style={styles.attemptHeader}>
                <View style={styles.modeBadge}>
                  <Ionicons
                    name={attempt.mode === 'practice' ? 'book-outline' : 'school-outline'}
                    size={14}
                    color="#94A3B8"
                  />
                  <Text style={styles.modeText}>
                    {attempt.mode === 'practice' ? t.practice : t.exam}
                  </Text>
                </View>
                <Text style={styles.dateText}>{formatDate(attempt.completed_at)}</Text>
              </View>

              <View style={styles.attemptBody}>
                <View style={styles.scoreContainer}>
                  <Text
                    style={[
                      styles.scoreText,
                      { color: getScoreColor(attempt.score_percentage) },
                    ]}
                  >
                    {Math.round(attempt.score_percentage)}%
                  </Text>
                </View>

                <View style={styles.detailsContainer}>
                  <Text style={styles.detailText}>
                    {attempt.correct_answers} {t.correct} / {attempt.total_questions} {t.questions}
                  </Text>
                  {attempt.category && (
                    <Text style={styles.categoryText}>{attempt.category}</Text>
                  )}
                </View>
              </View>

              <View style={styles.progressBar}>
                <View
                  style={[
                    styles.progressFill,
                    {
                      width: `${attempt.score_percentage}%`,
                      backgroundColor: getScoreColor(attempt.score_percentage),
                    },
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
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1E293B',
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1E293B',
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  placeholder: {
    width: 40,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyText: {
    fontSize: 18,
    color: '#64748B',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#475569',
    marginTop: 8,
  },
  scrollContent: {
    padding: 20,
  },
  attemptCard: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  attemptHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  modeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#334155',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    gap: 4,
  },
  modeText: {
    fontSize: 12,
    color: '#94A3B8',
  },
  dateText: {
    fontSize: 12,
    color: '#64748B',
  },
  attemptBody: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  scoreContainer: {
    marginRight: 16,
  },
  scoreText: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  detailsContainer: {
    flex: 1,
  },
  detailText: {
    fontSize: 14,
    color: '#94A3B8',
  },
  categoryText: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 4,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#334155',
    borderRadius: 2,
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
  },
});
