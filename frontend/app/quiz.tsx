import React, { useEffect, useState, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Animated,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as Speech from 'expo-speech';
import { useAppStore } from '../src/store/appStore';
import { api, Question } from '../src/services/api';

const ANSWER_LETTERS = ['A', 'B', 'C', 'D'];
const EXAM_TIME_SECONDS = 90 * 60; // 90 minutes
const EXAM_PASS_THRESHOLD = 85;

const TRANSLATIONS: Record<string, Record<string, string>> = {
  no: {
    question: 'Spørsmål', of: 'av', checkAnswer: 'Sjekk svar', nextQuestion: 'Neste',
    finish: 'Fullfør', explanation: 'Forklaring', correct: 'Riktig!', incorrect: 'Feil!',
    exit: 'Avslutt', tapTranslate: 'Trykk for oversettelse', timeRemaining: 'Tid igjen',
  },
  th: {
    question: 'คำถาม', of: 'จาก', checkAnswer: 'ตรวจคำตอบ', nextQuestion: 'ถัดไป',
    finish: 'เสร็จสิ้น', explanation: 'คำอธิบาย', correct: 'ถูกต้อง!', incorrect: 'ผิด!',
    exit: 'ออก', tapTranslate: 'แตะเพื่อแปล', timeRemaining: 'เวลาที่เหลือ',
  },
  en: {
    question: 'Question', of: 'of', checkAnswer: 'Check Answer', nextQuestion: 'Next',
    finish: 'Finish', explanation: 'Explanation', correct: 'Correct!', incorrect: 'Incorrect!',
    exit: 'Exit', tapTranslate: 'Tap to translate', timeRemaining: 'Time remaining',
  },
};

export default function QuizScreen() {
  const router = useRouter();
  const { mode, category } = useLocalSearchParams<{ mode: string; category: string }>();
  const { language, deviceId, addBookmark, removeBookmark, isBookmarked, setProgress } = useAppStore();
  const t = TRANSLATIONS[language] || TRANSLATIONS.no;

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [loading, setLoading] = useState(true);
  const [quizStartTime] = useState(new Date());
  const [answeredQuestions, setAnsweredQuestions] = useState<any[]>([]);
  const [showTranslation, setShowTranslation] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(EXAM_TIME_SECONDS);

  const fadeAnim = useRef(new Animated.Value(1)).current;
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const isExam = mode === 'exam';

  useEffect(() => {
    loadQuestions();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      Speech.stop();
    };
  }, []);

  useEffect(() => {
    if (isExam && !loading && questions.length > 0) {
      timerRef.current = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            if (timerRef.current) clearInterval(timerRef.current);
            handleTimeUp();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [loading, questions.length]);

  const loadQuestions = async () => {
    try {
      const count = isExam ? 45 : 10;
      const cat = category === 'all' ? undefined : category;
      const qs = await api.getRandomQuestions(count, cat);
      setQuestions(qs);
    } catch (error) {
      console.error('Error loading questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeUp = useCallback(() => {
    const correctCount = answeredQuestions.filter((a) => a.correct).length;
    const totalAnswered = answeredQuestions.length;
    const scorePercentage = totalAnswered > 0 ? (correctCount / questions.length) * 100 : 0;
    navigateToResults(correctCount, scorePercentage);
  }, [answeredQuestions, questions.length]);

  const currentQuestion = questions[currentIndex];

  const getQuestionText = (q: Question, lang?: string) => {
    const l = lang || language;
    const key = `question_text_${l}` as keyof Question;
    return (q[key] as string) || q.question_text_no;
  };

  const getAnswerText = (q: Question, letter: string, lang?: string) => {
    const l = lang || language;
    const key = `answer_${letter.toLowerCase()}_${l}` as keyof Question;
    return (q[key] as string) || (q as any)[`answer_${letter.toLowerCase()}_no`];
  };

  const getExplanation = (q: Question, lang?: string) => {
    const l = lang || language;
    const key = `explanation_${l}` as keyof Question;
    return (q[key] as string) || q.explanation_no;
  };

  const handleSelectAnswer = (letter: string) => {
    if (isAnswered) return;
    setSelectedAnswer(letter);
  };

  const handleCheckAnswer = async () => {
    if (!selectedAnswer || !currentQuestion) return;
    setIsAnswered(true);
    const isCorrect = selectedAnswer === currentQuestion.correct_answer;

    setAnsweredQuestions((prev) => [
      ...prev,
      { question_id: currentQuestion.id, selected_answer: selectedAnswer, correct: isCorrect },
    ]);

    try {
      await api.updateProgress(deviceId, isCorrect, currentQuestion.category);
      const updatedProgress = await api.getProgress(deviceId);
      setProgress(updatedProgress);
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  const handleNext = () => {
    if (currentIndex >= questions.length - 1) {
      finishQuiz();
      return;
    }

    Animated.sequence([
      Animated.timing(fadeAnim, { toValue: 0, duration: 120, useNativeDriver: true }),
      Animated.timing(fadeAnim, { toValue: 1, duration: 120, useNativeDriver: true }),
    ]).start();

    setTimeout(() => {
      setCurrentIndex((prev) => prev + 1);
      setSelectedAnswer(null);
      setIsAnswered(false);
      setShowTranslation(false);
    }, 120);
  };

  const finishQuiz = async () => {
    if (timerRef.current) clearInterval(timerRef.current);
    const correctCount = answeredQuestions.filter((a) => a.correct).length;
    const scorePercentage = (correctCount / questions.length) * 100;

    try {
      const passed = isExam ? scorePercentage >= EXAM_PASS_THRESHOLD : undefined;
      await api.saveQuizAttempt({
        device_id: deviceId,
        mode: mode || 'practice',
        category: category === 'all' ? undefined : category,
        total_questions: questions.length,
        correct_answers: correctCount,
        score_percentage: scorePercentage,
        passed,
        questions_answered: answeredQuestions,
        started_at: quizStartTime.toISOString(),
      });
    } catch (error) {
      console.error('Error saving quiz attempt:', error);
    }

    navigateToResults(correctCount, scorePercentage);
  };

  const navigateToResults = (correctCount: number, scorePercentage: number) => {
    router.replace({
      pathname: '/results',
      params: {
        total: questions.length.toString(),
        correct: correctCount.toString(),
        mode: mode || 'practice',
        passed: isExam ? (scorePercentage >= EXAM_PASS_THRESHOLD ? 'true' : 'false') : '',
      },
    });
  };

  const handleBookmark = async () => {
    if (!currentQuestion) return;
    if (isBookmarked(currentQuestion.id)) {
      await removeBookmark(currentQuestion.id);
    } else {
      await addBookmark(currentQuestion.id);
    }
  };

  const speakThai = () => {
    if (!currentQuestion) return;
    if (isSpeaking) {
      Speech.stop();
      setIsSpeaking(false);
      return;
    }
    setIsSpeaking(true);
    Speech.speak(getQuestionText(currentQuestion, 'th'), {
      language: 'th-TH',
      rate: 0.85,
      onDone: () => setIsSpeaking(false),
      onError: () => setIsSpeaking(false),
    });
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator testID="quiz-loading" size="large" color="#F59E0B" />
        </View>
      </SafeAreaView>
    );
  }

  if (!currentQuestion) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.errorText}>No questions available</Text>
        </View>
      </SafeAreaView>
    );
  }

  const questionBookmarked = isBookmarked(currentQuestion.id);
  const timerWarning = isExam && timeRemaining < 300;

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity testID="quiz-exit-btn" style={styles.exitButton} onPress={() => router.back()}>
          <Ionicons name="close" size={22} color="#F8FAFC" />
        </TouchableOpacity>

        <View style={styles.progressContainer}>
          <Text style={styles.progressText}>
            {currentIndex + 1} / {questions.length}
          </Text>
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: `${((currentIndex + 1) / questions.length) * 100}%` }]} />
          </View>
        </View>

        <TouchableOpacity testID="quiz-bookmark-btn" style={styles.bookmarkButton} onPress={handleBookmark}>
          <Ionicons
            name={questionBookmarked ? 'bookmark' : 'bookmark-outline'}
            size={22}
            color={questionBookmarked ? '#F59E0B' : '#F8FAFC'}
          />
        </TouchableOpacity>
      </View>

      {/* Timer for exam mode */}
      {isExam && (
        <View style={[styles.timerBar, timerWarning && styles.timerBarWarning]}>
          <Ionicons name="timer-outline" size={16} color={timerWarning ? '#EF4444' : '#F59E0B'} />
          <Text style={[styles.timerText, timerWarning && styles.timerTextWarning]}>
            {formatTime(timeRemaining)}
          </Text>
        </View>
      )}

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        <Animated.View style={{ opacity: fadeAnim }}>
          {/* Question */}
          <TouchableOpacity
            testID="question-card"
            style={styles.questionCard}
            onPress={() => setShowTranslation(!showTranslation)}
            activeOpacity={0.9}
          >
            <Text style={styles.questionText}>{getQuestionText(currentQuestion)}</Text>

            {/* Translate hint */}
            {!showTranslation && language !== 'th' && (
              <View style={styles.translateHint}>
                <Ionicons name="language-outline" size={14} color="#F59E0B" />
                <Text style={styles.translateHintText}>{t.tapTranslate}</Text>
              </View>
            )}

            {/* Thai Translation */}
            {showTranslation && language !== 'th' && (
              <View style={styles.translationContainer}>
                <View style={styles.translationDivider} />
                <Text style={styles.translationText}>
                  {getQuestionText(currentQuestion, 'th')}
                </Text>
                <TouchableOpacity testID="tts-btn" style={styles.ttsButton} onPress={speakThai}>
                  <Ionicons
                    name={isSpeaking ? 'volume-high' : 'volume-medium-outline'}
                    size={18}
                    color="#F59E0B"
                  />
                  <Text style={styles.ttsButtonText}>🇹🇭</Text>
                </TouchableOpacity>
              </View>
            )}
          </TouchableOpacity>

          {/* Answers */}
          <View style={styles.answersContainer}>
            {ANSWER_LETTERS.map((letter) => {
              const answerText = getAnswerText(currentQuestion, letter);
              const isSelected = selectedAnswer === letter;
              const isCorrect = currentQuestion.correct_answer === letter;

              let cardStyle = [styles.answerButton];
              let letterBgStyle = [styles.answerLetterBg];
              let textColor = '#E2E8F0';

              if (isAnswered) {
                if (isCorrect) {
                  cardStyle.push(styles.correctAnswer);
                  letterBgStyle.push(styles.correctLetterBg);
                  textColor = '#10B981';
                } else if (isSelected && !isCorrect) {
                  cardStyle.push(styles.incorrectAnswer);
                  letterBgStyle.push(styles.incorrectLetterBg);
                  textColor = '#EF4444';
                } else {
                  cardStyle.push(styles.dimmedAnswer);
                }
              } else if (isSelected) {
                cardStyle.push(styles.selectedAnswer);
                letterBgStyle.push(styles.selectedLetterBg);
              }

              return (
                <TouchableOpacity
                  key={letter}
                  testID={`answer-btn-${letter}`}
                  style={cardStyle}
                  onPress={() => handleSelectAnswer(letter)}
                  disabled={isAnswered}
                  activeOpacity={0.7}
                >
                  <View style={letterBgStyle}>
                    <Text style={styles.letterText}>{letter}</Text>
                  </View>
                  <Text style={[styles.answerText, { color: textColor }]}>{answerText}</Text>
                  {isAnswered && isCorrect && (
                    <Ionicons name="checkmark-circle" size={22} color="#10B981" />
                  )}
                  {isAnswered && isSelected && !isCorrect && (
                    <Ionicons name="close-circle" size={22} color="#EF4444" />
                  )}
                </TouchableOpacity>
              );
            })}
          </View>

          {/* Explanation */}
          {isAnswered && (
            <View style={styles.explanationCard}>
              <View style={styles.explanationHeader}>
                <Ionicons
                  name={selectedAnswer === currentQuestion.correct_answer ? 'checkmark-circle' : 'close-circle'}
                  size={22}
                  color={selectedAnswer === currentQuestion.correct_answer ? '#10B981' : '#EF4444'}
                />
                <Text style={[styles.explanationStatus, {
                  color: selectedAnswer === currentQuestion.correct_answer ? '#10B981' : '#EF4444',
                }]}>
                  {selectedAnswer === currentQuestion.correct_answer ? t.correct : t.incorrect}
                </Text>
              </View>
              <Text style={styles.explanationLabel}>{t.explanation}:</Text>
              <Text style={styles.explanationText}>{getExplanation(currentQuestion)}</Text>
              {language !== 'th' && (
                <Text style={styles.explanationThai}>{getExplanation(currentQuestion, 'th')}</Text>
              )}
            </View>
          )}
        </Animated.View>
      </ScrollView>

      {/* Action Button */}
      <View style={styles.actionContainer}>
        {!isAnswered ? (
          <TouchableOpacity
            testID="check-answer-btn"
            style={[styles.actionButton, !selectedAnswer && styles.actionButtonDisabled]}
            onPress={handleCheckAnswer}
            disabled={!selectedAnswer}
          >
            <Text style={styles.actionButtonText}>{t.checkAnswer}</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity testID="next-btn" style={styles.actionButton} onPress={handleNext}>
            <Text style={styles.actionButtonText}>
              {currentIndex >= questions.length - 1 ? t.finish : t.nextQuestion}
            </Text>
            <Ionicons name="arrow-forward" size={20} color="#0F172A" />
          </TouchableOpacity>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  errorText: { color: '#EF4444', fontSize: 16 },
  header: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 12, gap: 12 },
  exitButton: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#1E293B', justifyContent: 'center', alignItems: 'center' },
  progressContainer: { flex: 1 },
  progressText: { fontSize: 13, color: '#94A3B8', marginBottom: 6, textAlign: 'center', fontWeight: '600' },
  progressBar: { height: 6, backgroundColor: '#1E293B', borderRadius: 3 },
  progressFill: { height: '100%', backgroundColor: '#F59E0B', borderRadius: 3 },
  bookmarkButton: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#1E293B', justifyContent: 'center', alignItems: 'center' },
  timerBar: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 8, gap: 6, backgroundColor: 'rgba(245, 158, 11, 0.08)', borderBottomWidth: 1, borderBottomColor: 'rgba(245, 158, 11, 0.15)' },
  timerBarWarning: { backgroundColor: 'rgba(239, 68, 68, 0.08)', borderBottomColor: 'rgba(239, 68, 68, 0.15)' },
  timerText: { fontSize: 16, fontWeight: '700', color: '#F59E0B', fontVariant: ['tabular-nums'] },
  timerTextWarning: { color: '#EF4444' },
  scrollContent: { padding: 16, paddingBottom: 24 },
  questionCard: { backgroundColor: '#1E293B', borderRadius: 20, padding: 24, marginBottom: 20, borderWidth: 1, borderColor: 'rgba(51, 65, 85, 0.5)' },
  questionText: { fontSize: 20, fontWeight: '700', color: '#F8FAFC', lineHeight: 28 },
  translateHint: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 12, opacity: 0.7 },
  translateHintText: { fontSize: 12, color: '#F59E0B' },
  translationContainer: { marginTop: 12 },
  translationDivider: { height: 1, backgroundColor: 'rgba(245, 158, 11, 0.2)', marginBottom: 12 },
  translationText: { fontSize: 16, color: '#F59E0B', lineHeight: 24 },
  ttsButton: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 10, alignSelf: 'flex-start', backgroundColor: 'rgba(245, 158, 11, 0.1)', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 },
  ttsButtonText: { fontSize: 14 },
  answersContainer: { gap: 10 },
  answerButton: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1E293B', borderRadius: 16, padding: 16, borderWidth: 2, borderColor: 'rgba(51, 65, 85, 0.5)' },
  selectedAnswer: { borderColor: '#F59E0B', backgroundColor: 'rgba(245, 158, 11, 0.08)' },
  correctAnswer: { borderColor: '#10B981', backgroundColor: 'rgba(16, 185, 129, 0.08)' },
  incorrectAnswer: { borderColor: '#EF4444', backgroundColor: 'rgba(239, 68, 68, 0.08)' },
  dimmedAnswer: { opacity: 0.5 },
  answerLetterBg: { width: 36, height: 36, borderRadius: 12, backgroundColor: '#334155', justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  selectedLetterBg: { backgroundColor: '#F59E0B' },
  correctLetterBg: { backgroundColor: '#10B981' },
  incorrectLetterBg: { backgroundColor: '#EF4444' },
  letterText: { fontSize: 15, fontWeight: '700', color: '#F8FAFC' },
  answerText: { flex: 1, fontSize: 16, color: '#E2E8F0', lineHeight: 22 },
  explanationCard: { backgroundColor: '#1E293B', borderRadius: 20, padding: 20, marginTop: 20, borderWidth: 1, borderColor: 'rgba(51, 65, 85, 0.5)' },
  explanationHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12, gap: 8 },
  explanationStatus: { fontSize: 18, fontWeight: '700' },
  explanationLabel: { fontSize: 13, color: '#64748B', textTransform: 'uppercase', letterSpacing: 1, fontWeight: '600', marginBottom: 8 },
  explanationText: { fontSize: 15, color: '#E2E8F0', lineHeight: 22 },
  explanationThai: { fontSize: 14, color: '#F59E0B', lineHeight: 22, marginTop: 8, opacity: 0.85 },
  actionContainer: { padding: 16, borderTopWidth: 1, borderTopColor: 'rgba(51, 65, 85, 0.5)' },
  actionButton: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', backgroundColor: '#F59E0B', borderRadius: 16, paddingVertical: 16, gap: 8 },
  actionButtonDisabled: { backgroundColor: '#334155' },
  actionButtonText: { fontSize: 16, fontWeight: '700', color: '#0F172A' },
});
