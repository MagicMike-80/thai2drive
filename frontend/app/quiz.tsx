import React, { useEffect, useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Animated,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { api, Question } from '../src/services/api';

const ANSWER_LETTERS = ['A', 'B', 'C', 'D'];

const TRANSLATIONS = {
  no: {
    question: 'Spørsmål',
    of: 'av',
    checkAnswer: 'Sjekk svar',
    nextQuestion: 'Neste spørsmål',
    finish: 'Fullfør',
    explanation: 'Forklaring',
    correct: 'Riktig!',
    incorrect: 'Feil!',
    exit: 'Avslutt',
    bookmark: 'Bokmerk',
    bookmarked: 'Bokmerket',
  },
  th: {
    question: 'คำถาม',
    of: 'จาก',
    checkAnswer: 'ตรวจคำตอบ',
    nextQuestion: 'คำถามถัดไป',
    finish: 'เสร็จสิ้น',
    explanation: 'คำอธิบาย',
    correct: 'ถูกต้อง!',
    incorrect: 'ผิด!',
    exit: 'ออก',
    bookmark: 'บุ๊คมาร์ค',
    bookmarked: 'บันทึกแล้ว',
  },
  en: {
    question: 'Question',
    of: 'of',
    checkAnswer: 'Check Answer',
    nextQuestion: 'Next Question',
    finish: 'Finish',
    explanation: 'Explanation',
    correct: 'Correct!',
    incorrect: 'Incorrect!',
    exit: 'Exit',
    bookmark: 'Bookmark',
    bookmarked: 'Bookmarked',
  },
};

export default function QuizScreen() {
  const router = useRouter();
  const { mode, category } = useLocalSearchParams<{ mode: string; category: string }>();
  const { language, deviceId, addBookmark, removeBookmark, isBookmarked, setProgress } = useAppStore();
  const t = TRANSLATIONS[language as keyof typeof TRANSLATIONS];

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [loading, setLoading] = useState(true);
  const [quizStartTime] = useState(new Date());
  const [answeredQuestions, setAnsweredQuestions] = useState<any[]>([]);

  const fadeAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      const count = mode === 'exam' ? 20 : 10;
      const cat = category === 'all' ? undefined : category;
      const qs = await api.getRandomQuestions(count, cat);
      setQuestions(qs);
    } catch (error) {
      console.error('Error loading questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const currentQuestion = questions[currentIndex];

  const getQuestionText = (q: Question) => {
    const key = `question_text_${language}` as keyof Question;
    return q[key] as string || q.question_text_no;
  };

  const getAnswerText = (q: Question, letter: string) => {
    const key = `answer_${letter.toLowerCase()}_${language}` as keyof Question;
    return q[key] as string || (q as any)[`answer_${letter.toLowerCase()}_no`];
  };

  const getExplanation = (q: Question) => {
    const key = `explanation_${language}` as keyof Question;
    return q[key] as string || q.explanation_no;
  };

  const handleSelectAnswer = (letter: string) => {
    if (isAnswered) return;
    setSelectedAnswer(letter);
  };

  const handleCheckAnswer = async () => {
    if (!selectedAnswer || !currentQuestion) return;

    setIsAnswered(true);
    const isCorrect = selectedAnswer === currentQuestion.correct_answer;

    // Save answer record
    setAnsweredQuestions((prev) => [
      ...prev,
      {
        question_id: currentQuestion.id,
        selected_answer: selectedAnswer,
        correct: isCorrect,
      },
    ]);

    // Update progress
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
      // Quiz complete
      finishQuiz();
      return;
    }

    // Animate transition
    Animated.sequence([
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 150,
        useNativeDriver: true,
      }),
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 150,
        useNativeDriver: true,
      }),
    ]).start();

    setTimeout(() => {
      setCurrentIndex((prev) => prev + 1);
      setSelectedAnswer(null);
      setIsAnswered(false);
    }, 150);
  };

  const finishQuiz = async () => {
    const correctCount = answeredQuestions.filter((a) => a.correct).length;
    const scorePercentage = (correctCount / questions.length) * 100;

    try {
      await api.saveQuizAttempt({
        device_id: deviceId,
        mode: mode || 'practice',
        category: category === 'all' ? undefined : category,
        total_questions: questions.length,
        correct_answers: correctCount,
        score_percentage: scorePercentage,
        questions_answered: answeredQuestions,
        started_at: quizStartTime.toISOString(),
      });
    } catch (error) {
      console.error('Error saving quiz attempt:', error);
    }

    router.replace({
      pathname: '/results',
      params: {
        total: questions.length.toString(),
        correct: correctCount.toString(),
        mode: mode || 'practice',
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

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#3B82F6" />
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

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.exitButton}
          onPress={() => router.back()}
        >
          <Ionicons name="close" size={24} color="#FFFFFF" />
        </TouchableOpacity>

        <View style={styles.progressContainer}>
          <Text style={styles.progressText}>
            {t.question} {currentIndex + 1} {t.of} {questions.length}
          </Text>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                { width: `${((currentIndex + 1) / questions.length) * 100}%` },
              ]}
            />
          </View>
        </View>

        <TouchableOpacity
          style={styles.bookmarkButton}
          onPress={handleBookmark}
        >
          <Ionicons
            name={questionBookmarked ? 'bookmark' : 'bookmark-outline'}
            size={24}
            color={questionBookmarked ? '#F59E0B' : '#FFFFFF'}
          />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Animated.View style={{ opacity: fadeAnim }}>
          {/* Question */}
          <View style={styles.questionCard}>
            <Text style={styles.questionText}>
              {getQuestionText(currentQuestion)}
            </Text>
          </View>

          {/* Answers */}
          <View style={styles.answersContainer}>
            {ANSWER_LETTERS.map((letter) => {
              const answerText = getAnswerText(currentQuestion, letter);
              const isSelected = selectedAnswer === letter;
              const isCorrect = currentQuestion.correct_answer === letter;

              let buttonStyle = styles.answerButton;
              let textStyle = styles.answerText;
              let letterStyle = styles.answerLetter;

              if (isAnswered) {
                if (isCorrect) {
                  buttonStyle = { ...buttonStyle, ...styles.correctAnswer };
                  textStyle = { ...textStyle, color: '#22C55E' };
                  letterStyle = { ...letterStyle, ...styles.correctLetter };
                } else if (isSelected && !isCorrect) {
                  buttonStyle = { ...buttonStyle, ...styles.incorrectAnswer };
                  textStyle = { ...textStyle, color: '#EF4444' };
                  letterStyle = { ...letterStyle, ...styles.incorrectLetter };
                }
              } else if (isSelected) {
                buttonStyle = { ...buttonStyle, ...styles.selectedAnswer };
                letterStyle = { ...letterStyle, ...styles.selectedLetter };
              }

              return (
                <TouchableOpacity
                  key={letter}
                  style={buttonStyle}
                  onPress={() => handleSelectAnswer(letter)}
                  disabled={isAnswered}
                  activeOpacity={0.7}
                >
                  <View style={letterStyle}>
                    <Text style={styles.letterText}>{letter}</Text>
                  </View>
                  <Text style={textStyle}>{answerText}</Text>
                </TouchableOpacity>
              );
            })}
          </View>

          {/* Explanation (shown after answering) */}
          {isAnswered && (
            <View style={styles.explanationCard}>
              <View style={styles.explanationHeader}>
                <Ionicons
                  name={
                    selectedAnswer === currentQuestion.correct_answer
                      ? 'checkmark-circle'
                      : 'close-circle'
                  }
                  size={24}
                  color={
                    selectedAnswer === currentQuestion.correct_answer
                      ? '#22C55E'
                      : '#EF4444'
                  }
                />
                <Text
                  style={[
                    styles.explanationStatus,
                    {
                      color:
                        selectedAnswer === currentQuestion.correct_answer
                          ? '#22C55E'
                          : '#EF4444',
                    },
                  ]}
                >
                  {selectedAnswer === currentQuestion.correct_answer
                    ? t.correct
                    : t.incorrect}
                </Text>
              </View>
              <Text style={styles.explanationLabel}>{t.explanation}:</Text>
              <Text style={styles.explanationText}>
                {getExplanation(currentQuestion)}
              </Text>
            </View>
          )}
        </Animated.View>
      </ScrollView>

      {/* Action Button */}
      <View style={styles.actionContainer}>
        {!isAnswered ? (
          <TouchableOpacity
            style={[
              styles.actionButton,
              !selectedAnswer && styles.actionButtonDisabled,
            ]}
            onPress={handleCheckAnswer}
            disabled={!selectedAnswer}
          >
            <Text style={styles.actionButtonText}>{t.checkAnswer}</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity style={styles.actionButton} onPress={handleNext}>
            <Text style={styles.actionButtonText}>
              {currentIndex >= questions.length - 1 ? t.finish : t.nextQuestion}
            </Text>
            <Ionicons name="arrow-forward" size={20} color="#FFFFFF" />
          </TouchableOpacity>
        )}
      </View>
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
  errorText: {
    color: '#EF4444',
    fontSize: 16,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1E293B',
  },
  exitButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1E293B',
    justifyContent: 'center',
    alignItems: 'center',
  },
  progressContainer: {
    flex: 1,
    marginHorizontal: 16,
  },
  progressText: {
    fontSize: 12,
    color: '#94A3B8',
    marginBottom: 8,
    textAlign: 'center',
  },
  progressBar: {
    height: 4,
    backgroundColor: '#1E293B',
    borderRadius: 2,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3B82F6',
    borderRadius: 2,
  },
  bookmarkButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1E293B',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollContent: {
    padding: 20,
  },
  questionCard: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 24,
    marginBottom: 24,
  },
  questionText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#FFFFFF',
    lineHeight: 28,
  },
  answersContainer: {
    gap: 12,
  },
  answerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1E293B',
    borderRadius: 12,
    padding: 16,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedAnswer: {
    borderColor: '#3B82F6',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
  },
  correctAnswer: {
    borderColor: '#22C55E',
    backgroundColor: 'rgba(34, 197, 94, 0.1)',
  },
  incorrectAnswer: {
    borderColor: '#EF4444',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
  },
  answerLetter: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#334155',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  selectedLetter: {
    backgroundColor: '#3B82F6',
  },
  correctLetter: {
    backgroundColor: '#22C55E',
  },
  incorrectLetter: {
    backgroundColor: '#EF4444',
  },
  letterText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  answerText: {
    flex: 1,
    fontSize: 16,
    color: '#E2E8F0',
    lineHeight: 22,
  },
  explanationCard: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 20,
    marginTop: 24,
  },
  explanationHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  explanationStatus: {
    fontSize: 18,
    fontWeight: '600',
    marginLeft: 8,
  },
  explanationLabel: {
    fontSize: 14,
    color: '#94A3B8',
    marginBottom: 8,
  },
  explanationText: {
    fontSize: 15,
    color: '#E2E8F0',
    lineHeight: 22,
  },
  actionContainer: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#1E293B',
  },
  actionButton: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#3B82F6',
    borderRadius: 12,
    paddingVertical: 16,
    gap: 8,
  },
  actionButtonDisabled: {
    backgroundColor: '#334155',
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});
