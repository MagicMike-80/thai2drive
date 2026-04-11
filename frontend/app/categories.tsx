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
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { api, Category } from '../src/services/api';

const CATEGORY_ICONS: { [key: string]: keyof typeof Ionicons.glyphMap } = {
  'Traffic Signs': 'warning-outline',
  'Road Rules': 'document-text-outline',
  'Right of Way': 'git-branch-outline',
  'Speed Limits': 'speedometer-outline',
  'Safety': 'shield-checkmark-outline',
};

const CATEGORY_COLORS: { [key: string]: string } = {
  'Traffic Signs': '#F59E0B',
  'Road Rules': '#3B82F6',
  'Right of Way': '#8B5CF6',
  'Speed Limits': '#EF4444',
  'Safety': '#22C55E',
};

const TRANSLATIONS = {
  no: {
    selectCategory: 'Velg kategori',
    allCategories: 'Alle kategorier',
    questions: 'spørsmål',
    back: 'Tilbake',
    practice: 'Øvingsmodus',
    exam: 'Eksamensmodus',
    categories: {
      'Traffic Signs': 'Trafikkskilt',
      'Road Rules': 'Trafikkregler',
      'Right of Way': 'Vikeplikt',
      'Speed Limits': 'Fartsgrenser',
      'Safety': 'Sikkerhet',
    },
  },
  th: {
    selectCategory: 'เลือกหมวดหมู่',
    allCategories: 'ทุกหมวดหมู่',
    questions: 'คำถาม',
    back: 'กลับ',
    practice: 'โหมดฝึกซ้อม',
    exam: 'โหมดสอบ',
    categories: {
      'Traffic Signs': 'ป้ายจราจร',
      'Road Rules': 'กฎจราจร',
      'Right of Way': 'การให้ทาง',
      'Speed Limits': 'ขีดจำกัดความเร็ว',
      'Safety': 'ความปลอดภัย',
    },
  },
  en: {
    selectCategory: 'Select Category',
    allCategories: 'All Categories',
    questions: 'questions',
    back: 'Back',
    practice: 'Practice Mode',
    exam: 'Exam Mode',
    categories: {
      'Traffic Signs': 'Traffic Signs',
      'Road Rules': 'Road Rules',
      'Right of Way': 'Right of Way',
      'Speed Limits': 'Speed Limits',
      'Safety': 'Safety',
    },
  },
};

export default function CategoriesScreen() {
  const router = useRouter();
  const { mode } = useLocalSearchParams<{ mode: string }>();
  const { language } = useAppStore();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const t = TRANSLATIONS[language as keyof typeof TRANSLATIONS];

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const cats = await api.getCategories();
      setCategories(cats);
    } catch (error) {
      console.error('Error loading categories:', error);
    } finally {
      setLoading(false);
    }
  };

  const startQuiz = (category?: string) => {
    router.push({
      pathname: '/quiz',
      params: { mode, category: category || 'all' },
    });
  };

  const totalQuestions = categories.reduce((sum, cat) => sum + cat.count, 0);

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
        <View style={styles.headerText}>
          <Text style={styles.modeLabel}>
            {mode === 'practice' ? t.practice : t.exam}
          </Text>
          <Text style={styles.title}>{t.selectCategory}</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* All Categories Option */}
        <TouchableOpacity
          style={styles.allCard}
          onPress={() => startQuiz()}
          activeOpacity={0.8}
        >
          <View style={styles.allIconContainer}>
            <Ionicons name="grid-outline" size={28} color="#3B82F6" />
          </View>
          <View style={styles.allTextContainer}>
            <Text style={styles.allTitle}>{t.allCategories}</Text>
            <Text style={styles.allCount}>
              {totalQuestions} {t.questions}
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#64748B" />
        </TouchableOpacity>

        {/* Category Grid */}
        <View style={styles.grid}>
          {categories.map((category) => {
            const catName = category.name as keyof typeof t.categories;
            const displayName = t.categories[catName] || category.name;
            const icon = CATEGORY_ICONS[category.name] || 'help-circle-outline';
            const color = CATEGORY_COLORS[category.name] || '#64748B';

            return (
              <TouchableOpacity
                key={category.name}
                style={[styles.categoryCard, { borderColor: `${color}40` }]}
                onPress={() => startQuiz(category.name)}
                activeOpacity={0.8}
              >
                <View style={[styles.categoryIcon, { backgroundColor: `${color}20` }]}>
                  <Ionicons name={icon} size={28} color={color} />
                </View>
                <Text style={styles.categoryName}>{displayName}</Text>
                <Text style={styles.categoryCount}>
                  {category.count} {t.questions}
                </Text>
              </TouchableOpacity>
            );
          })}
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
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
    marginRight: 16,
  },
  headerText: {
    flex: 1,
  },
  modeLabel: {
    fontSize: 12,
    color: '#3B82F6',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginTop: 4,
  },
  scrollContent: {
    padding: 20,
  },
  allCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
  },
  allIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  allTextContainer: {
    flex: 1,
  },
  allTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  allCount: {
    fontSize: 14,
    color: '#94A3B8',
    marginTop: 4,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
  },
  categoryCard: {
    width: '47%',
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
  },
  categoryIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  categoryName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  categoryCount: {
    fontSize: 13,
    color: '#94A3B8',
  },
});
