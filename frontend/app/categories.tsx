import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { api, Category } from '../src/services/api';

const CATEGORY_ICONS: Record<string, keyof typeof Ionicons.glyphMap> = {
  'Traffic Signs': 'warning-outline', 'Road Rules': 'document-text-outline',
  'Right of Way': 'git-branch-outline', 'Speed Limits': 'speedometer-outline', 'Safety': 'shield-checkmark-outline',
  'Driving Conditions': 'rainy-outline',
  'Situations': 'bulb-outline',
};
const CATEGORY_COLORS: Record<string, string> = {
  'Traffic Signs': '#F59E0B', 'Road Rules': '#3B82F6', 'Right of Way': '#8B5CF6', 'Speed Limits': '#EF4444', 'Safety': '#22C55E',
  'Driving Conditions': '#06B6D4',
  'Situations': '#EC4899',
};
const TR: Record<string, Record<string, any>> = {
  no: { selectCategory: 'Velg kategori', allCategories: 'Alle kategorier', questions: 'spørsmål', practice: 'Øvingsmodus', exam: 'Eksamensmodus',
    categories: { 'Traffic Signs': 'Trafikkskilt', 'Road Rules': 'Trafikkregler', 'Right of Way': 'Vikeplikt', 'Speed Limits': 'Fartsgrenser', 'Safety': 'Sikkerhet', 'Driving Conditions': 'Kjøreforhold', 'Situations': 'Situasjoner' } },
  th: { selectCategory: 'เลือกหมวดหมู่', allCategories: 'ทุกหมวดหมู่', questions: 'คำถาม', practice: 'โหมดฝึกซ้อม', exam: 'โหมดสอบ',
    categories: { 'Traffic Signs': 'ป้ายจราจร', 'Road Rules': 'กฎจราจร', 'Right of Way': 'การให้ทาง', 'Speed Limits': 'ขีดจำกัดความเร็ว', 'Safety': 'ความปลอดภัย', 'Driving Conditions': 'สภาพการขับขี่', 'Situations': 'สถานการณ์จริง' } },
  en: { selectCategory: 'Select Category', allCategories: 'All Categories', questions: 'questions', practice: 'Practice Mode', exam: 'Exam Mode',
    categories: { 'Traffic Signs': 'Traffic Signs', 'Road Rules': 'Road Rules', 'Right of Way': 'Right of Way', 'Speed Limits': 'Speed Limits', 'Safety': 'Safety', 'Driving Conditions': 'Driving Conditions', 'Situations': 'Situations' } },
};

export default function CategoriesScreen() {
  const router = useRouter();
  const { mode } = useLocalSearchParams<{ mode: string }>();
  const { language, colors } = useAppStore();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const t = TR[language] || TR.no;
  const c = colors;

  useEffect(() => { api.getCategories().then(setCategories).catch(console.error).finally(() => setLoading(false)); }, []);

  const startQuiz = (cat?: string) => router.push({ pathname: '/quiz', params: { mode, category: cat || 'all' } });
  const total = categories.reduce((s, cat) => s + cat.count, 0);

  if (loading) return <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}><View style={st.center}><ActivityIndicator size="large" color={c.accent} /></View></SafeAreaView>;

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <View style={[st.header, { borderBottomColor: c.divider }]}>
        <TouchableOpacity style={[st.backBtn, { backgroundColor: c.card }]} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={22} color={c.text} />
        </TouchableOpacity>
        <View style={{ flex: 1 }}>
          <Text style={[st.modeLabel, { color: c.accent }]}>{mode === 'practice' ? t.practice : t.exam}</Text>
          <Text style={[st.title, { color: c.text }]}>{t.selectCategory}</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={st.scroll}>
        <TouchableOpacity testID="all-categories-btn" style={[st.allCard, { backgroundColor: c.card, borderColor: c.cardBorder }]} onPress={() => startQuiz()} activeOpacity={0.8}>
          <View style={[st.allIcon, { backgroundColor: c.accentBg }]}><Ionicons name="grid-outline" size={24} color={c.accent} /></View>
          <View style={{ flex: 1 }}><Text style={[st.allTitle, { color: c.text }]}>{t.allCategories}</Text><Text style={[st.allCount, { color: c.textSecondary }]}>{total} {t.questions}</Text></View>
          <Ionicons name="chevron-forward" size={22} color={c.textMuted} />
        </TouchableOpacity>

        <View style={st.grid}>
          {categories.map((cat) => {
            const name = (t.categories as any)[cat.name] || cat.name;
            const icon = CATEGORY_ICONS[cat.name] || 'help-circle-outline';
            const color = CATEGORY_COLORS[cat.name] || c.textMuted;
            return (
              <TouchableOpacity key={cat.name} testID={`category-${cat.name}`} style={[st.catCard, { backgroundColor: c.card, borderColor: `${color}30` }]} onPress={() => startQuiz(cat.name)} activeOpacity={0.8}>
                <View style={[st.catIcon, { backgroundColor: `${color}18` }]}><Ionicons name={icon} size={24} color={color} /></View>
                <Text style={[st.catName, { color: c.text }]}>{name}</Text>
                <Text style={[st.catCount, { color: c.textSecondary }]}>{cat.count} {t.questions}</Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1 },
  backBtn: { width: 40, height: 40, borderRadius: 12, justifyContent: 'center', alignItems: 'center', marginRight: 14 },
  modeLabel: { fontSize: 11, textTransform: 'uppercase', letterSpacing: 1, fontWeight: '700' },
  title: { fontSize: 22, fontWeight: '800', marginTop: 2 },
  scroll: { padding: 16 },
  allCard: { flexDirection: 'row', alignItems: 'center', borderRadius: 16, padding: 16, marginBottom: 20, borderWidth: 1 },
  allIcon: { width: 48, height: 48, borderRadius: 14, justifyContent: 'center', alignItems: 'center', marginRight: 14 },
  allTitle: { fontSize: 17, fontWeight: '700' },
  allCount: { fontSize: 13, marginTop: 2 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  catCard: { width: '47%', borderRadius: 16, padding: 16, borderWidth: 1 },
  catIcon: { width: 48, height: 48, borderRadius: 14, justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  catName: { fontSize: 15, fontWeight: '700', marginBottom: 2 },
  catCount: { fontSize: 12 },
});
