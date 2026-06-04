import React, { useEffect, useState, useRef } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, ScrollView,
  ActivityIndicator, Animated, Image, Dimensions
} from 'react-native';

const SCREEN_W = Dimensions.get('window').width;
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as Speech from 'expo-speech';
import { useAppStore } from '../src/store/appStore';
import { api, BookChapter, BookSection } from '../src/services/api';
import { BookHtml } from '../src/components/BookHtml';

const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Læringsbok',
    chapters: 'Kapitler',
    back: 'Tilbake',
    loading: 'Laster...',
    noContent: 'Innhold kommer snart',
    listen: 'Lytt',
    stop: 'Stopp',
    sections: 'seksjoner',
    next: 'Neste',
    prev: 'Forrige',
  },
  th: {
    title: 'หนังสือเรียน',
    chapters: 'บทเรียน',
    back: 'กลับ',
    loading: 'กำลังโหลด...',
    noContent: 'เนื้อหาจะมาเร็วๆ นี้',
    listen: 'ฟัง',
    stop: 'หยุด',
    sections: 'หัวข้อ',
    next: 'ถัดไป',
    prev: 'ก่อนหน้า',
  },
  en: {
    title: 'Study Book',
    chapters: 'Chapters',
    back: 'Back',
    loading: 'Loading...',
    noContent: 'Content coming soon',
    listen: 'Listen',
    stop: 'Stop',
    sections: 'sections',
    next: 'Next',
    prev: 'Previous',
  },
};

const LANG_CODES: Record<string, string> = {
  no: 'nb-NO',
  th: 'th-TH',
  en: 'en-US',
};

export default function BookScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ chapter?: string; section?: string }>();
  const { language, colors } = useAppStore();
  const c = colors;
  const t = TR[language] || TR.no;
  const lang = language as 'no' | 'th' | 'en';
  const isDark = c.bg === '#0F172A';

  const [chapters, setChapters] = useState<BookChapter[]>([]);
  const [sections, setSections] = useState<BookSection[]>([]);
  const [selectedChapter, setSelectedChapter] = useState<number | null>(
    params.chapter ? parseInt(params.chapter) : null
  );
  const [selectedSection, setSelectedSection] = useState<number>(
    params.section ? parseInt(params.section) : 0
  );
  const [loading, setLoading] = useState(true);
  const [speaking, setSpeaking] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    loadChapters();
    return () => { Speech.stop(); };
  }, []);

  useEffect(() => {
    if (selectedChapter !== null) {
      loadSections(selectedChapter);
    }
  }, [selectedChapter]);

  useEffect(() => {
    fadeAnim.setValue(0);
    Animated.timing(fadeAnim, { toValue: 1, duration: 300, useNativeDriver: true }).start();
  }, [selectedSection]);

  const loadChapters = async () => {
    try {
      const data = await api.getChapters();
      setChapters(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const loadSections = async (chapterNum: number) => {
    setLoading(true);
    Speech.stop();
    setSpeaking(false);
    try {
      const data = await api.getChapterSections(chapterNum);
      setSections(data);
      setSelectedSection(0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const currentSection = sections[selectedSection] || null;

  const toggleSpeech = () => {
    if (speaking) {
      Speech.stop();
      setSpeaking(false);
      return;
    }
    if (!currentSection) return;
    const text = currentSection.content[lang] || currentSection.content.no;
    const title = currentSection.section_title[lang] || currentSection.section_title.no;
    Speech.speak(`${title}. ${text}`, {
      language: LANG_CODES[lang] || 'nb-NO',
      rate: 0.85,
      onDone: () => setSpeaking(false),
      onError: () => setSpeaking(false),
    });
    setSpeaking(true);
  };

  const goNext = () => {
    Speech.stop();
    setSpeaking(false);
    if (selectedSection < sections.length - 1) {
      setSelectedSection(s => s + 1);
    }
  };

  const goPrev = () => {
    Speech.stop();
    setSpeaking(false);
    if (selectedSection > 0) {
      setSelectedSection(s => s - 1);
    }
  };

  // CHAPTER LIST VIEW
  if (selectedChapter === null) {
    return (
      <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
        {/* Header */}
        <View style={[st.header, { borderBottomColor: c.divider }]}>
          <TouchableOpacity onPress={() => router.back()} style={st.backBtn}>
            <Ionicons name="arrow-back" size={24} color={c.text} />
          </TouchableOpacity>
          <Text style={[st.headerTitle, { color: c.text }]}>{t.title}</Text>
          <View style={{ width: 40 }} />
        </View>

        {loading ? (
          <View style={st.center}>
            <ActivityIndicator size="large" color={c.accent} />
          </View>
        ) : chapters.length === 0 ? (
          <View style={st.center}>
            <Ionicons name="book-outline" size={48} color={c.textMuted} />
            <Text style={[st.emptyText, { color: c.textMuted }]}>{t.noContent}</Text>
          </View>
        ) : (
          <ScrollView contentContainerStyle={st.chapterList}>
            <Text style={[st.sectionHeader, { color: c.textMuted }]}>{t.chapters}</Text>
            {chapters.map((ch, idx) => (
              <TouchableOpacity
                key={ch.chapter_num}
                style={[st.chapterCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}
                onPress={() => setSelectedChapter(ch.chapter_num)}
                activeOpacity={0.75}
              >
                <View style={[st.chapterNum, { backgroundColor: c.accentBg }]}>
                  <Text style={[st.chapterNumText, { color: c.accent }]}>{ch.chapter_num}</Text>
                </View>
                <View style={st.chapterInfo}>
                  <Text style={[st.chapterTitle, { color: c.text }]}>{ch.title[lang] || ch.title.no}</Text>
                  <Text style={[st.chapterSub, { color: c.textMuted }]}>{ch.section_count} {t.sections}</Text>
                </View>
                <Ionicons name="chevron-forward" size={20} color={c.textMuted} />
              </TouchableOpacity>
            ))}
          </ScrollView>
        )}
      </SafeAreaView>
    );
  }

  // READING VIEW
  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      {/* Header */}
      <View style={[st.header, { borderBottomColor: c.divider }]}>
        <TouchableOpacity onPress={() => { Speech.stop(); setSpeaking(false); setSelectedChapter(null); setSections([]); }} style={st.backBtn}>
          <Ionicons name="arrow-back" size={24} color={c.text} />
        </TouchableOpacity>
        <Text style={[st.headerTitle, { color: c.text }]} numberOfLines={1}>
          {chapters.find(c => c.chapter_num === selectedChapter)?.title[lang] || ''}
        </Text>
        {/* Listen button */}
        <TouchableOpacity
          style={[st.listenBtn, { backgroundColor: speaking ? c.accent : c.accentBg }]}
          onPress={toggleSpeech}
          disabled={!currentSection}
        >
          <Ionicons name={speaking ? 'stop' : 'volume-high-outline'} size={20} color={speaking ? '#0F172A' : c.accent} />
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={st.center}><ActivityIndicator size="large" color={c.accent} /></View>
      ) : sections.length === 0 ? (
        <View style={st.center}>
          <Text style={[st.emptyText, { color: c.textMuted }]}>{t.noContent}</Text>
        </View>
      ) : currentSection ? (
        <>
          {/* Progress bar */}
          <View style={[st.progressBar, { backgroundColor: c.divider }]}>
            <View style={[st.progressFill, { backgroundColor: c.accent, width: `${((selectedSection + 1) / sections.length) * 100}%` }]} />
          </View>

          {/* Section counter */}
          <Text style={[st.counter, { color: c.textMuted }]}>
            {selectedSection + 1} / {sections.length}
          </Text>

          {/* Content */}
          <Animated.ScrollView style={{ opacity: fadeAnim }} contentContainerStyle={st.content}>
            <Text style={[st.sectionTitle, { color: c.accent }]}>
              {currentSection.section_title[lang] || currentSection.section_title.no}
            </Text>
            {currentSection.image ? (
              <View style={st.imageWrapper}>
                <Image
                  source={{ uri: currentSection.image }}
                  style={st.sectionImage}
                  resizeMode="contain"
                />
              </View>
            ) : null}
            <BookHtml
              html={currentSection.content[lang] || currentSection.content.no || ''}
              textColor={c.text}
              accentColor={c.accent}
              isDark={isDark}
            />
          </Animated.ScrollView>

          {/* Navigation */}
          <View style={[st.navRow, { borderTopColor: c.divider }]}>
            <TouchableOpacity
              style={[st.navBtn, { opacity: selectedSection === 0 ? 0.3 : 1 }]}
              onPress={goPrev}
              disabled={selectedSection === 0}
            >
              <Ionicons name="chevron-back" size={22} color={c.text} />
              <Text style={[st.navText, { color: c.text }]}>{t.prev}</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[st.navBtn, { opacity: selectedSection === sections.length - 1 ? 0.3 : 1 }]}
              onPress={goNext}
              disabled={selectedSection === sections.length - 1}
            >
              <Text style={[st.navText, { color: c.text }]}>{t.next}</Text>
              <Ionicons name="chevron-forward" size={22} color={c.text} />
            </TouchableOpacity>
          </View>
        </>
      ) : null}
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1 },
  backBtn: { width: 40, height: 40, justifyContent: 'center' },
  headerTitle: { flex: 1, fontSize: 17, fontWeight: '700', textAlign: 'center', marginHorizontal: 8 },
  listenBtn: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center' },
  chapterList: { padding: 20, gap: 12 },
  sectionHeader: { fontSize: 11, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4 },
  chapterCard: { flexDirection: 'row', alignItems: 'center', borderRadius: 14, borderWidth: 1, padding: 16, gap: 14 },
  chapterNum: { width: 42, height: 42, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  chapterNumText: { fontSize: 18, fontWeight: '800' },
  chapterInfo: { flex: 1 },
  chapterTitle: { fontSize: 15, fontWeight: '700' },
  chapterSub: { fontSize: 12, marginTop: 3 },
  progressBar: { height: 3 },
  progressFill: { height: 3 },
  counter: { fontSize: 12, textAlign: 'center', marginTop: 10, marginBottom: 4 },
  content: { padding: 24, paddingBottom: 40 },
  sectionTitle: { fontSize: 20, fontWeight: '800', marginBottom: 16, lineHeight: 26 },
  imageWrapper: { borderRadius: 12, overflow: 'hidden', marginBottom: 20, backgroundColor: '#fff' },
  sectionImage: { width: SCREEN_W - 48, height: (SCREEN_W - 48) * 0.6 },
  bodyText: { fontSize: 16, lineHeight: 26, letterSpacing: 0.1 },
  emptyText: { fontSize: 15, marginTop: 12, textAlign: 'center' },
  navRow: { flexDirection: 'row', justifyContent: 'space-between', paddingHorizontal: 24, paddingVertical: 16, borderTopWidth: 1 },
  navBtn: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  navText: { fontSize: 15, fontWeight: '600' },
});
