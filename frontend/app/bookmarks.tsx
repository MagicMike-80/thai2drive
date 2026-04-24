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
import { api, Question } from '../src/services/api';
import { useScreenProtection } from '../src/hooks/useScreenProtection';
import { AppBrand } from '../src/components/AppBrand';

const TRANSLATIONS = {
  no: {
    title: 'Bokmerker',
    noBookmarks: 'Ingen bokmerker ennå',
    bookmarkHint: 'Bokmerk spørsmål under quiz for å se dem her',
    back: 'Tilbake',
    remove: 'Fjern',
    answer: 'Svar',
  },
  th: {
    title: 'บุ๊คมาร์ค',
    noBookmarks: 'ยังไม่มีบุ๊คมาร์ค',
    bookmarkHint: 'บันทึกคำถามระหว่างทำแบบทดสอบเพื่อดูที่นี่',
    back: 'กลับ',
    remove: 'ลบ',
    answer: 'คำตอบ',
  },
  en: {
    title: 'Bookmarks',
    noBookmarks: 'No bookmarks yet',
    bookmarkHint: 'Bookmark questions during quiz to see them here',
    back: 'Back',
    remove: 'Remove',
    answer: 'Answer',
  },
};

export default function BookmarksScreen() {
  const router = useRouter();
  const { language, deviceId, removeBookmark } = useAppStore();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const t = TRANSLATIONS[language as keyof typeof TRANSLATIONS] || TRANSLATIONS.en;

  // Screen capture protection
  useScreenProtection(language);

  useEffect(() => {
    loadBookmarks();
  }, []);

  const loadBookmarks = async () => {
    try {
      const data = await api.getBookmarkedQuestions(deviceId);
      setQuestions(data);
    } catch (error) {
      console.error('Error loading bookmarks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (questionId: string) => {
    await removeBookmark(questionId);
    setQuestions((prev) => prev.filter((q) => q.id !== questionId));
  };

  const getQuestionText = (q: Question) => {
    return q.question?.[language] || q.question?.no || '';
  };

  const getAnswerText = (q: Question, optId: string) => {
    const opt = q.options?.find(o => o.id === optId);
    return opt?.text?.[language] || opt?.text?.no || '';
  };

  const getExplanation = (q: Question) => {
    return q.explanation?.[language] || q.explanation?.no || '';
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
        <View style={styles.brandWrap}>
          <AppBrand size="md" />
        </View>
        <Text style={styles.title}>{t.title}</Text>
        <View style={{ width: 40 }} />
      </View>

      {questions.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="bookmark-outline" size={64} color="#334155" />
          <Text style={styles.emptyText}>{t.noBookmarks}</Text>
          <Text style={styles.emptySubtext}>{t.bookmarkHint}</Text>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.scrollContent}>
          {questions.map((question) => {
            const isExpanded = expandedId === question.id;

            return (
              <View key={question.id} style={styles.questionCard}>
                <TouchableOpacity
                  style={styles.questionHeader}
                  onPress={() => setExpandedId(isExpanded ? null : question.id)}
                  activeOpacity={0.7}
                >
                  <Text style={styles.questionText} numberOfLines={isExpanded ? undefined : 2}>
                    {getQuestionText(question)}
                  </Text>
                  <Ionicons
                    name={isExpanded ? 'chevron-up' : 'chevron-down'}
                    size={20}
                    color="#64748B"
                  />
                </TouchableOpacity>

                {isExpanded && (
                  <View style={styles.expandedContent}>
                    {/* Answer */}
                    <View style={styles.answerSection}>
                      <Text style={styles.answerLabel}>{t.answer}:</Text>
                      <View style={styles.correctAnswer}>
                        <Text style={styles.correctLetter}>{question.correctOptionId}</Text>
                        <Text style={styles.correctText}>
                          {getAnswerText(question, question.correctOptionId)}
                        </Text>
                      </View>
                    </View>

                    {/* Explanation */}
                    <View style={styles.explanationSection}>
                      <Text style={styles.explanationText}>
                        {getExplanation(question)}
                      </Text>
                    </View>

                    {/* Category & Remove */}
                    <View style={styles.cardFooter}>
                      <View style={styles.categoryBadge}>
                        <Text style={styles.categoryText}>{question.category}</Text>
                      </View>
                      <TouchableOpacity
                        style={styles.removeButton}
                        onPress={() => handleRemove(question.id)}
                      >
                        <Ionicons name="trash-outline" size={16} color="#EF4444" />
                        <Text style={styles.removeText}>{t.remove}</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                )}
              </View>
            );
          })}
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
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1E293B',
  },
  brandWrap: { marginRight: 12 },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1E293B',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  title: {
    flex: 1,
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  countBadge: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  countText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
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
    textAlign: 'center',
  },
  scrollContent: {
    padding: 20,
  },
  questionCard: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    marginBottom: 12,
    overflow: 'hidden',
  },
  questionHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 16,
  },
  questionText: {
    flex: 1,
    fontSize: 16,
    color: '#FFFFFF',
    lineHeight: 22,
    marginRight: 12,
  },
  expandedContent: {
    borderTopWidth: 1,
    borderTopColor: '#334155',
    padding: 16,
  },
  answerSection: {
    marginBottom: 16,
  },
  answerLabel: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 8,
  },
  correctAnswer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(34, 197, 94, 0.1)',
    borderRadius: 8,
    padding: 12,
  },
  correctLetter: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#22C55E',
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
    lineHeight: 28,
    marginRight: 12,
  },
  correctText: {
    flex: 1,
    fontSize: 14,
    color: '#22C55E',
  },
  explanationSection: {
    backgroundColor: '#0F172A',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  explanationText: {
    fontSize: 14,
    color: '#94A3B8',
    lineHeight: 20,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  categoryBadge: {
    backgroundColor: '#334155',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  categoryText: {
    fontSize: 12,
    color: '#94A3B8',
  },
  removeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  removeText: {
    fontSize: 14,
    color: '#EF4444',
  },
});
