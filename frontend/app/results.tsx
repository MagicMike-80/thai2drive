import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';

const TRANSLATIONS = {
  no: {
    quizComplete: 'Quiz fullført!',
    yourScore: 'Din poengsum',
    correct: 'Riktige',
    outOf: 'av',
    excellent: 'Utmerket!',
    good: 'Bra jobbet!',
    keepPracticing: 'Fortsett å øve!',
    tryAgain: 'Prøv igjen',
    backHome: 'Tilbake til hjem',
    practice: 'Øvingsmodus',
    exam: 'Eksamensmodus',
  },
  th: {
    quizComplete: 'ทำแบบทดสอบเสร็จสิ้น!',
    yourScore: 'คะแนนของคุณ',
    correct: 'ถูกต้อง',
    outOf: 'จาก',
    excellent: 'ยอดเยี่ยม!',
    good: 'ทำได้ดี!',
    keepPracticing: 'ฝึกซ้อมต่อไป!',
    tryAgain: 'ลองอีกครั้ง',
    backHome: 'กลับหน้าหลัก',
    practice: 'โหมดฝึกซ้อม',
    exam: 'โหมดสอบ',
  },
  en: {
    quizComplete: 'Quiz Complete!',
    yourScore: 'Your Score',
    correct: 'Correct',
    outOf: 'out of',
    excellent: 'Excellent!',
    good: 'Good job!',
    keepPracticing: 'Keep practicing!',
    tryAgain: 'Try Again',
    backHome: 'Back to Home',
    practice: 'Practice Mode',
    exam: 'Exam Mode',
  },
};

export default function ResultsScreen() {
  const router = useRouter();
  const { total, correct, mode } = useLocalSearchParams<{
    total: string;
    correct: string;
    mode: string;
  }>();
  const { language } = useAppStore();
  const t = TRANSLATIONS[language as keyof typeof TRANSLATIONS];

  const totalNum = parseInt(total || '0', 10);
  const correctNum = parseInt(correct || '0', 10);
  const percentage = totalNum > 0 ? Math.round((correctNum / totalNum) * 100) : 0;

  const getMessage = () => {
    if (percentage >= 80) return t.excellent;
    if (percentage >= 60) return t.good;
    return t.keepPracticing;
  };

  const getColor = () => {
    if (percentage >= 80) return '#22C55E';
    if (percentage >= 60) return '#F59E0B';
    return '#EF4444';
  };

  const getIcon = (): keyof typeof Ionicons.glyphMap => {
    if (percentage >= 80) return 'trophy';
    if (percentage >= 60) return 'thumbs-up';
    return 'refresh';
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {/* Result Icon */}
        <View style={[styles.iconContainer, { backgroundColor: `${getColor()}20` }]}>
          <Ionicons name={getIcon()} size={64} color={getColor()} />
        </View>

        {/* Message */}
        <Text style={[styles.message, { color: getColor() }]}>{getMessage()}</Text>
        <Text style={styles.subtitle}>{t.quizComplete}</Text>

        {/* Score Display */}
        <View style={styles.scoreCard}>
          <Text style={styles.scoreLabel}>{t.yourScore}</Text>
          <View style={styles.scoreRow}>
            <Text style={[styles.scorePercentage, { color: getColor() }]}>
              {percentage}%
            </Text>
          </View>
          <Text style={styles.scoreDetail}>
            {correctNum} {t.correct} {t.outOf} {totalNum}
          </Text>

          {/* Progress Ring */}
          <View style={styles.progressRing}>
            <View
              style={[
                styles.progressFill,
                {
                  width: `${percentage}%`,
                  backgroundColor: getColor(),
                },
              ]}
            />
          </View>
        </View>

        {/* Mode Badge */}
        <View style={styles.modeBadge}>
          <Ionicons
            name={mode === 'practice' ? 'book-outline' : 'school-outline'}
            size={16}
            color="#94A3B8"
          />
          <Text style={styles.modeText}>
            {mode === 'practice' ? t.practice : t.exam}
          </Text>
        </View>
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={() => router.replace('/')}
        >
          <Ionicons name="home-outline" size={20} color="#94A3B8" />
          <Text style={styles.secondaryButtonText}>{t.backHome}</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.primaryButton}
          onPress={() =>
            router.replace({
              pathname: '/categories',
              params: { mode },
            })
          }
        >
          <Ionicons name="refresh" size={20} color="#FFFFFF" />
          <Text style={styles.primaryButtonText}>{t.tryAgain}</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  iconContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  message: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#94A3B8',
    marginBottom: 32,
  },
  scoreCard: {
    backgroundColor: '#1E293B',
    borderRadius: 20,
    padding: 32,
    alignItems: 'center',
    width: '100%',
    marginBottom: 24,
  },
  scoreLabel: {
    fontSize: 14,
    color: '#94A3B8',
    marginBottom: 8,
  },
  scoreRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  scorePercentage: {
    fontSize: 64,
    fontWeight: 'bold',
  },
  scoreDetail: {
    fontSize: 16,
    color: '#64748B',
    marginTop: 8,
    marginBottom: 24,
  },
  progressRing: {
    width: '100%',
    height: 8,
    backgroundColor: '#334155',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  modeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1E293B',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 8,
  },
  modeText: {
    fontSize: 14,
    color: '#94A3B8',
  },
  actions: {
    flexDirection: 'row',
    padding: 20,
    gap: 16,
  },
  secondaryButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1E293B',
    borderRadius: 12,
    paddingVertical: 16,
    gap: 8,
  },
  secondaryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#94A3B8',
  },
  primaryButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#3B82F6',
    borderRadius: 12,
    paddingVertical: 16,
    gap: 8,
  },
  primaryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});
