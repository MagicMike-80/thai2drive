import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, ScrollView,
  TextInput, ActivityIndicator, SafeAreaView, Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';

const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'https://thai2drive-production.up.railway.app';

const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Trafikkordbok',
    subtitle: 'Norske trafikk­uttrykk forklart',
    search: 'Søk etter ord ...',
    term: 'Begrep',
    definition: 'Definisjon',
    example: 'Eksempel',
    noResults: 'Ingen treff — prøv et annet søk',
    loading: 'Laster ordbok ...',
    allTopics: 'Alle emner',
  },
  th: {
    title: 'พจนานุกรมจราจร',
    subtitle: 'คำศัพท์จราจรนอร์เวย์อธิบายเป็นภาษาไทย',
    search: 'ค้นหาคำ ...',
    term: 'คำศัพท์',
    definition: 'คำนิยาม',
    example: 'ตัวอย่าง',
    noResults: 'ไม่พบผลลัพธ์ — ลองค้นหาใหม่',
    loading: 'กำลังโหลดพจนานุกรม ...',
    allTopics: 'ทุกหัวข้อ',
  },
  en: {
    title: 'Traffic Glossary',
    subtitle: 'Norwegian traffic terms explained',
    search: 'Search terms ...',
    term: 'Term',
    definition: 'Definition',
    example: 'Example',
    noResults: 'No results — try a different search',
    loading: 'Loading glossary ...',
    allTopics: 'All topics',
  },
};

const TOPIC_FILTERS = [
  'Vikeplikt', 'Fart', 'Skilt', 'Sikkerhet', 'Kryss',
  'Kjøreregeler', 'Parkering', 'Gangfelt', 'Førerprøve',
];

interface GlossaryTerm {
  id: string;
  term_no: string;
  term_th: string;
  term_en: string;
  definition_no: string;
  definition_th: string;
  definition_en: string;
  example_no?: string;
  example_th?: string;
  example_en?: string;
  topic_tags: string[];
  active: boolean;
}

export default function GlossaryScreen() {
  const router = useRouter();
  const { language, colors } = useAppStore();
  const c = colors;
  const isDark = c.bg === '#0F172A' || c.bg === '#0B1222';
  const t = TR[language] || {};

  const [terms, setTerms] = useState<GlossaryTerm[]>([]);
  const [filtered, setFiltered] = useState<GlossaryTerm[]>([]);
  const [search, setSearch] = useState('');
  const [activeTopic, setActiveTopic] = useState('');
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    fetchTerms();
  }, []);

  const fetchTerms = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/glossary`);
      if (!res.ok) throw new Error('fetch failed');
      const data: GlossaryTerm[] = await res.json();
      setTerms(data);
      setFiltered(data);
    } catch (e) {
      console.error('Glossary fetch error:', e);
    } finally {
      setLoading(false);
    }
  };

  const applyFilter = useCallback((q: string, topic: string, data: GlossaryTerm[]) => {
    let out = data;
    if (topic) {
      out = out.filter(item => item.topic_tags?.includes(topic));
    }
    if (q.trim()) {
      const lq = q.toLowerCase();
      out = out.filter(item =>
        item.term_no.toLowerCase().includes(lq) ||
        item.term_th.toLowerCase().includes(lq) ||
        item.term_en.toLowerCase().includes(lq) ||
        item.definition_no.toLowerCase().includes(lq) ||
        item.definition_th.toLowerCase().includes(lq)
      );
    }
    setFiltered(out);
  }, []);

  const onSearch = (q: string) => {
    setSearch(q);
    applyFilter(q, activeTopic, terms);
  };

  const onTopic = (topic: string) => {
    const next = activeTopic === topic ? '' : topic;
    setActiveTopic(next);
    applyFilter(search, next, terms);
  };

  const getTermLabel = (item: GlossaryTerm) => {
    if (language === 'th') return item.term_th;
    if (language === 'en') return item.term_en;
    return item.term_no;
  };

  const getDefinition = (item: GlossaryTerm) => {
    if (language === 'th') return item.definition_th;
    if (language === 'en') return item.definition_en;
    return item.definition_no;
  };

  const getExample = (item: GlossaryTerm) => {
    if (language === 'th') return item.example_th;
    if (language === 'en') return item.example_en;
    return item.example_no;
  };

  return (
    <SafeAreaView style={[st.safe, { backgroundColor: c.bg }]}>
      {/* Header */}
      <View style={[st.header, { borderBottomColor: c.divider }]}>
        <TouchableOpacity onPress={() => router.back()} style={st.backBtn} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
          <Ionicons name="arrow-back" size={24} color={c.text} />
        </TouchableOpacity>
        <View style={{ flex: 1, marginLeft: 12 }}>
          <Text style={[st.headerTitle, { color: c.text }]}>{t.title}</Text>
          <Text style={[st.headerSub, { color: c.textMuted }]}>{t.subtitle}</Text>
        </View>
        <View style={[st.countBadge, { backgroundColor: c.accentBg }]}>
          <Text style={[st.countText, { color: c.accent }]}>{terms.length}</Text>
        </View>
      </View>

      {/* Search bar */}
      <View style={[st.searchWrap, { backgroundColor: isDark ? '#1E293B' : '#F1F5F9', borderColor: c.divider }]}>
        <Ionicons name="search-outline" size={18} color={c.textMuted} />
        <TextInput
          style={[st.searchInput, { color: c.text }]}
          placeholder={t.search}
          placeholderTextColor={c.textMuted}
          value={search}
          onChangeText={onSearch}
          clearButtonMode="while-editing"
          autoCapitalize="none"
          autoCorrect={false}
        />
        {search.length > 0 && (
          <TouchableOpacity onPress={() => onSearch('')}>
            <Ionicons name="close-circle" size={18} color={c.textMuted} />
          </TouchableOpacity>
        )}
      </View>

      {/* Topic chips */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={st.chipScroll}
        contentContainerStyle={st.chipRow}
      >
        <TouchableOpacity
          style={[st.chip, !activeTopic && { backgroundColor: c.accent }]}
          onPress={() => onTopic('')}
        >
          <Text style={[st.chipText, !activeTopic && { color: '#0F172A', fontWeight: '700' }]}>
            {t.allTopics}
          </Text>
        </TouchableOpacity>
        {TOPIC_FILTERS.map(topic => (
          <TouchableOpacity
            key={topic}
            style={[st.chip, { borderColor: c.divider }, activeTopic === topic && { backgroundColor: c.accent, borderColor: c.accent }]}
            onPress={() => onTopic(topic)}
          >
            <Text style={[st.chipText, { color: c.textMuted }, activeTopic === topic && { color: '#0F172A', fontWeight: '700' }]}>
              {topic}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Terms list */}
      {loading ? (
        <View style={st.center}>
          <ActivityIndicator size="large" color={c.accent} />
          <Text style={[st.loadingText, { color: c.textMuted }]}>{t.loading}</Text>
        </View>
      ) : filtered.length === 0 ? (
        <View style={st.center}>
          <Ionicons name="search-outline" size={40} color={c.textMuted} />
          <Text style={[st.emptyText, { color: c.textMuted }]}>{t.noResults}</Text>
        </View>
      ) : (
        <ScrollView
          contentContainerStyle={st.listContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {filtered.map(item => {
            const isExpanded = expandedId === item.id;
            const label = getTermLabel(item);
            const definition = getDefinition(item);
            const example = getExample(item);
            const norwegianAlt = language !== 'no' ? item.term_no : null;

            return (
              <TouchableOpacity
                key={item.id}
                style={[
                  st.card,
                  { backgroundColor: c.card, borderColor: isExpanded ? c.accent : c.cardBorder },
                  isExpanded && { borderColor: c.accent },
                ]}
                onPress={() => setExpandedId(isExpanded ? null : item.id)}
                activeOpacity={0.75}
              >
                {/* Card header */}
                <View style={st.cardHeader}>
                  <View style={{ flex: 1 }}>
                    <Text style={[st.termText, { color: c.text }]}>{label}</Text>
                    {norwegianAlt && (
                      <Text style={[st.termAlt, { color: c.textMuted }]}>{norwegianAlt}</Text>
                    )}
                  </View>
                  <View style={st.cardRight}>
                    {item.topic_tags?.[0] && (
                      <View style={[st.tag, { backgroundColor: isDark ? 'rgba(59,130,246,0.15)' : '#EFF6FF' }]}>
                        <Text style={[st.tagText, { color: c.accent }]}>{item.topic_tags[0]}</Text>
                      </View>
                    )}
                    <Ionicons
                      name={isExpanded ? 'chevron-up' : 'chevron-down'}
                      size={16}
                      color={c.textMuted}
                    />
                  </View>
                </View>

                {/* Definition always visible */}
                <Text style={[st.definition, { color: c.textSecondary || c.textMuted }]}>
                  {definition}
                </Text>

                {/* Example — only when expanded */}
                {isExpanded && example && (
                  <View style={[st.exampleBox, { backgroundColor: isDark ? 'rgba(16,185,129,0.08)' : 'rgba(16,185,129,0.06)', borderColor: 'rgba(16,185,129,0.25)' }]}>
                    <Ionicons name="chatbubble-outline" size={14} color="#10B981" style={{ marginRight: 6 }} />
                    <Text style={[st.exampleText, { color: c.text }]}>{example}</Text>
                  </View>
                )}

                {/* Extra topic tags when expanded */}
                {isExpanded && item.topic_tags?.length > 1 && (
                  <View style={st.tagRow}>
                    {item.topic_tags.slice(1).map(tag => (
                      <TouchableOpacity
                        key={tag}
                        style={[st.tag, { backgroundColor: isDark ? 'rgba(59,130,246,0.10)' : '#F0F7FF' }]}
                        onPress={() => onTopic(tag)}
                      >
                        <Text style={[st.tagText, { color: c.accent }]}>{tag}</Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                )}
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  safe: { flex: 1 },
  header: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 20, paddingVertical: 16,
    borderBottomWidth: 1,
  },
  backBtn: { padding: 4 },
  headerTitle: { fontSize: 20, fontWeight: '800' },
  headerSub: { fontSize: 12, marginTop: 2 },
  countBadge: { borderRadius: 12, paddingHorizontal: 10, paddingVertical: 4 },
  countText: { fontSize: 14, fontWeight: '800' },
  searchWrap: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    marginHorizontal: 16, marginTop: 14, marginBottom: 8,
    paddingHorizontal: 14, paddingVertical: Platform.OS === 'ios' ? 12 : 8,
    borderRadius: 14, borderWidth: 1,
  },
  searchInput: { flex: 1, fontSize: 15 },
  chipScroll: { maxHeight: 50 },
  chipRow: { paddingHorizontal: 16, gap: 8, alignItems: 'center', flexDirection: 'row' },
  chip: {
    paddingHorizontal: 14, paddingVertical: 6, borderRadius: 20,
    borderWidth: 1, borderColor: 'transparent',
  },
  chipText: { fontSize: 13, fontWeight: '600' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12 },
  loadingText: { fontSize: 14, marginTop: 8 },
  emptyText: { fontSize: 15, textAlign: 'center', marginTop: 8, maxWidth: 220 },
  listContent: { padding: 16, gap: 10, paddingBottom: 100 },
  card: {
    borderRadius: 16, borderWidth: 1.5,
    padding: 16,
  },
  cardHeader: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 6 },
  termText: { fontSize: 18, fontWeight: '800' },
  termAlt: { fontSize: 13, marginTop: 2 },
  cardRight: { flexDirection: 'row', alignItems: 'center', gap: 8, marginLeft: 8 },
  tag: { borderRadius: 8, paddingHorizontal: 8, paddingVertical: 3 },
  tagText: { fontSize: 11, fontWeight: '600' },
  definition: { fontSize: 14, lineHeight: 21 },
  exampleBox: {
    flexDirection: 'row', alignItems: 'flex-start',
    marginTop: 12, padding: 12, borderRadius: 10, borderWidth: 1,
  },
  exampleText: { flex: 1, fontSize: 13, lineHeight: 20 },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginTop: 10 },
});
