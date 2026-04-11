import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';

const TRANSLATIONS: Record<string, Record<string, string>> = {
  no: {
    quizComplete: 'Quiz fullført!', yourScore: 'Din poengsum', correct: 'Riktige', outOf: 'av',
    excellent: 'Utmerket!', good: 'Bra jobbet!', keepPracticing: 'Fortsett å øve!',
    tryAgain: 'Prøv igjen', backHome: 'Hjem', practice: 'Øving', exam: 'Eksamen',
    passed: 'BESTÅTT', failed: 'IKKE BESTÅTT', passThreshold: '85% kreves for å bestå',
  },
  th: {
    quizComplete: 'ทำแบบทดสอบเสร็จสิ้น!', yourScore: 'คะแนนของคุณ', correct: 'ถูกต้อง', outOf: 'จาก',
    excellent: 'ยอดเยี่ยม!', good: 'ทำได้ดี!', keepPracticing: 'ฝึกซ้อมต่อไป!',
    tryAgain: 'ลองอีกครั้ง', backHome: 'หน้าหลัก', practice: 'ฝึกซ้อม', exam: 'สอบ',
    passed: 'ผ่าน', failed: 'ไม่ผ่าน', passThreshold: 'ต้องได้ 85% ขึ้นไปจึงจะผ่าน',
  },
  en: {
    quizComplete: 'Quiz Complete!', yourScore: 'Your Score', correct: 'Correct', outOf: 'out of',
    excellent: 'Excellent!', good: 'Good job!', keepPracticing: 'Keep practicing!',
    tryAgain: 'Try Again', backHome: 'Home', practice: 'Practice', exam: 'Exam',
    passed: 'PASSED', failed: 'FAILED', passThreshold: '85% required to pass',
  },
};

export default function ResultsScreen() {
  const router = useRouter();
  const { total, correct, mode, passed } = useLocalSearchParams<{
    total: string; correct: string; mode: string; passed: string;
  }>();
  const { language } = useAppStore();
  const t = TRANSLATIONS[language] || TRANSLATIONS.no;

  const totalNum = parseInt(total || '0', 10);
  const correctNum = parseInt(correct || '0', 10);
  const percentage = totalNum > 0 ? Math.round((correctNum / totalNum) * 100) : 0;
  const isExam = mode === 'exam';
  const examPassed = passed === 'true';

  const getMessage = () => {
    if (isExam) return examPassed ? t.passed : t.failed;
    if (percentage >= 80) return t.excellent;
    if (percentage >= 60) return t.good;
    return t.keepPracticing;
  };

  const getColor = () => {
    if (isExam) return examPassed ? '#10B981' : '#EF4444';
    if (percentage >= 80) return '#10B981';
    if (percentage >= 60) return '#F59E0B';
    return '#EF4444';
  };

  const getIcon = (): keyof typeof Ionicons.glyphMap => {
    if (isExam) return examPassed ? 'trophy' : 'refresh';
    if (percentage >= 80) return 'trophy';
    if (percentage >= 60) return 'thumbs-up';
    return 'refresh';
  };

  const color = getColor();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={[styles.iconContainer, { backgroundColor: `${color}15` }]}>
          <Ionicons name={getIcon()} size={56} color={color} />
        </View>

        <Text testID="result-message" style={[styles.message, { color }]}>{getMessage()}</Text>
        <Text style={styles.subtitle}>{t.quizComplete}</Text>

        <View style={styles.scoreCard}>
          <Text style={styles.scoreLabel}>{t.yourScore}</Text>
          <Text testID="result-percentage" style={[styles.scorePercentage, { color }]}>{percentage}%</Text>
          <Text style={styles.scoreDetail}>
            {correctNum} {t.correct} {t.outOf} {totalNum}
          </Text>
          <View style={styles.progressRing}>
            <View style={[styles.progressFill, { width: `${percentage}%`, backgroundColor: color }]} />
          </View>
          {isExam && (
            <Text style={styles.passThreshold}>{t.passThreshold}</Text>
          )}
        </View>

        <View style={styles.modeBadge}>
          <Ionicons
            name={mode === 'practice' ? 'book-outline' : 'school-outline'}
            size={16} color="#94A3B8"
          />
          <Text style={styles.modeText}>
            {mode === 'practice' ? t.practice : t.exam}
          </Text>
        </View>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity testID="result-home-btn" style={styles.secondaryButton} onPress={() => router.replace('/')}>
          <Ionicons name="home-outline" size={20} color="#94A3B8" />
          <Text style={styles.secondaryButtonText}>{t.backHome}</Text>
        </TouchableOpacity>
        <TouchableOpacity
          testID="result-retry-btn"
          style={styles.primaryButton}
          onPress={() => {
            if (isExam) {
              router.replace({ pathname: '/quiz', params: { mode: 'exam', category: 'all' } });
            } else {
              router.replace({ pathname: '/categories', params: { mode } });
            }
          }}
        >
          <Ionicons name="refresh" size={20} color="#0F172A" />
          <Text style={styles.primaryButtonText}>{t.tryAgain}</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  content: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  iconContainer: { width: 112, height: 112, borderRadius: 56, justifyContent: 'center', alignItems: 'center', marginBottom: 20 },
  message: { fontSize: 30, fontWeight: '800', marginBottom: 4 },
  subtitle: { fontSize: 16, color: '#94A3B8', marginBottom: 32 },
  scoreCard: { backgroundColor: '#1E293B', borderRadius: 24, padding: 32, alignItems: 'center', width: '100%', marginBottom: 20, borderWidth: 1, borderColor: 'rgba(51, 65, 85, 0.5)' },
  scoreLabel: { fontSize: 13, color: '#64748B', textTransform: 'uppercase', letterSpacing: 1.5, fontWeight: '700', marginBottom: 8 },
  scorePercentage: { fontSize: 72, fontWeight: '800' },
  scoreDetail: { fontSize: 16, color: '#64748B', marginTop: 4, marginBottom: 20 },
  progressRing: { width: '100%', height: 8, backgroundColor: '#334155', borderRadius: 4, overflow: 'hidden' },
  progressFill: { height: '100%', borderRadius: 4 },
  passThreshold: { fontSize: 13, color: '#64748B', marginTop: 12 },
  modeBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1E293B', paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, gap: 6 },
  modeText: { fontSize: 14, color: '#94A3B8', fontWeight: '600' },
  actions: { flexDirection: 'row', padding: 20, gap: 12 },
  secondaryButton: { flex: 1, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', backgroundColor: '#1E293B', borderRadius: 16, paddingVertical: 16, gap: 8, borderWidth: 1, borderColor: 'rgba(51, 65, 85, 0.5)' },
  secondaryButtonText: { fontSize: 16, fontWeight: '600', color: '#94A3B8' },
  primaryButton: { flex: 1, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', backgroundColor: '#F59E0B', borderRadius: 16, paddingVertical: 16, gap: 8 },
  primaryButtonText: { fontSize: 16, fontWeight: '700', color: '#0F172A' },
});
