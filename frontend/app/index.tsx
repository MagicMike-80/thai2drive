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
  { code: 'no', label: 'Norsk', flag: '🇳🇴' },
  { code: 'th', label: 'ไทย', flag: '🇹🇭' },
  { code: 'en', label: 'English', flag: '🇬🇧' },
];

const TRANSLATIONS = {
  no: {
    title: 'Thai2Drive',
    subtitle: 'Norsk førerprøve quiz',
    practice: 'Øvingsmodus',
    exam: 'Eksamensmodus',
    practiceDesc: 'Øv deg uten press',
    examDesc: 'Test deg selv',
    history: 'Historikk',
    bookmarks: 'Bokmerker',
    stats: 'Din statistikk',
    answered: 'Besvart',
    correct: 'Riktige',
    accuracy: 'Nøyaktighet',
  },
  th: {
    title: 'Thai2Drive',
    subtitle: 'แบบทดสอบใบขับขี่นอร์เวย์',
    practice: 'โหมดฝึกซ้อม',
    exam: 'โหมดสอบ',
    practiceDesc: 'ฝึกซ้อมไม่มีเวลา',
    examDesc: 'ทดสอบตัวเอง',
    history: 'ประวัติ',
    bookmarks: 'บุ๊คมาร์ค',
    stats: 'สถิติของคุณ',
    answered: 'ตอบแล้ว',
    correct: 'ถูกต้อง',
    accuracy: 'ความแม่นยำ',
  },
  en: {
    title: 'Thai2Drive',
    subtitle: 'Norwegian Driving Theory Quiz',
    practice: 'Practice Mode',
    exam: 'Exam Mode',
    practiceDesc: 'Practice without pressure',
    examDesc: 'Test yourself',
    history: 'History',
    bookmarks: 'Bookmarks',
    stats: 'Your Statistics',
    answered: 'Answered',
    correct: 'Correct',
    accuracy: 'Accuracy',
  },
};

export default function HomeScreen() {
  const router = useRouter();
  const { language, setLanguage, deviceId, setProgress, progress } = useAppStore();
  const [loading, setLoading] = useState(true);
  const t = TRANSLATIONS[language as keyof typeof TRANSLATIONS];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Seed database if needed
      await api.seedDatabase();
      // Load user progress
      const userProgress = await api.getProgress(deviceId);
      setProgress(userProgress);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const navigateToQuiz = (mode: 'practice' | 'exam') => {
    router.push({
      pathname: '/categories',
      params: { mode },
    });
  };

  const accuracy = progress.total_questions_answered > 0
    ? Math.round((progress.correct_answers / progress.total_questions_answered) * 100)
    : 0;

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
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>{t.title}</Text>
            <Text style={styles.subtitle}>{t.subtitle}</Text>
          </View>
          {/* Language Selector */}
          <View style={styles.languageSelector}>
            {LANGUAGES.map((lang) => (
              <TouchableOpacity
                key={lang.code}
                style={[
                  styles.langButton,
                  language === lang.code && styles.langButtonActive,
                ]}
                onPress={() => setLanguage(lang.code)}
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
              <Text style={[styles.statValue, { color: accuracy >= 70 ? '#22C55E' : '#EF4444' }]}>
                {accuracy}%
              </Text>
              <Text style={styles.statLabel}>{t.accuracy}</Text>
            </View>
          </View>
        </View>

        {/* Mode Selection */}
        <View style={styles.modesContainer}>
          <TouchableOpacity
            style={[styles.modeCard, styles.practiceCard]}
            onPress={() => navigateToQuiz('practice')}
            activeOpacity={0.8}
          >
            <View style={styles.modeIconContainer}>
              <Ionicons name="book-outline" size={32} color="#22C55E" />
            </View>
            <Text style={styles.modeTitle}>{t.practice}</Text>
            <Text style={styles.modeDesc}>{t.practiceDesc}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.modeCard, styles.examCard]}
            onPress={() => navigateToQuiz('exam')}
            activeOpacity={0.8}
          >
            <View style={styles.modeIconContainer}>
              <Ionicons name="school-outline" size={32} color="#3B82F6" />
            </View>
            <Text style={styles.modeTitle}>{t.exam}</Text>
            <Text style={styles.modeDesc}>{t.examDesc}</Text>
          </TouchableOpacity>
        </View>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => router.push('/history')}
          >
            <Ionicons name="time-outline" size={24} color="#94A3B8" />
            <Text style={styles.actionText}>{t.history}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => router.push('/bookmarks')}
          >
            <Ionicons name="bookmark-outline" size={24} color="#94A3B8" />
            <Text style={styles.actionText}>{t.bookmarks}</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
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
  scrollContent: {
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 24,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  subtitle: {
    fontSize: 14,
    color: '#94A3B8',
    marginTop: 4,
  },
  languageSelector: {
    flexDirection: 'row',
    gap: 8,
  },
  langButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1E293B',
    justifyContent: 'center',
    alignItems: 'center',
  },
  langButtonActive: {
    backgroundColor: '#3B82F6',
  },
  langFlag: {
    fontSize: 20,
  },
  statsCard: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
  },
  statsTitle: {
    fontSize: 16,
    color: '#94A3B8',
    marginBottom: 16,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  statLabel: {
    fontSize: 12,
    color: '#94A3B8',
    marginTop: 4,
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#334155',
  },
  modesContainer: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 24,
  },
  modeCard: {
    flex: 1,
    borderRadius: 16,
    padding: 20,
    minHeight: 160,
  },
  practiceCard: {
    backgroundColor: 'rgba(34, 197, 94, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(34, 197, 94, 0.3)',
  },
  examCard: {
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(59, 130, 246, 0.3)',
  },
  modeIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#1E293B',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  modeTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  modeDesc: {
    fontSize: 13,
    color: '#94A3B8',
  },
  quickActions: {
    flexDirection: 'row',
    gap: 16,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#1E293B',
    borderRadius: 12,
    padding: 16,
    gap: 8,
  },
  actionText: {
    fontSize: 14,
    color: '#94A3B8',
  },
});
