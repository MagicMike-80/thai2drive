import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Image,
  Linking,
  Modal,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { api, LearningVideo, TrafficSign, TrafficSignGroup } from '../src/services/api';

type Lang = 'no' | 'th' | 'en';

const TR: Record<Lang, Record<string, string>> = {
  no: {
    title: 'Trafikkskilt',
    all: 'Alle',
    close: 'Lukk',
    loading: 'Laster skilt',
    noData: 'Kunne ikke laste skilt.',
    meaning: 'Hva betyr skiltet?',
    driver: 'Hva må føreren gjøre?',
    mistake: 'Vanlig feil',
    exam: 'Eksamentips',
    memory: 'Huskeregel',
    scenario: 'I trafikken',
    related: 'Relaterte skilt',
    confused: 'Ofte forvekslet med',
    practice: 'Øv på dette skiltet',
    askAi: 'Spør AI',
    audio: 'Les høyt',
    save: 'Lagre',
    saved: 'Lagret',
    aiTeacher: 'AI-kjørelærer',
    video: 'Se kort forklaring',
    fallbackMeaning: 'Les form, farge og symbol, og koble skiltet til situasjonen på veien.',
    fallbackDriver: 'Tilpass fart, plassering og oppmerksomhet etter det skiltet forteller.',
    fallbackMistake: 'Ikke les skiltet isolert. Se også underskilt og trafikksituasjonen rundt.',
    fallbackExam: 'Spør: hva endrer dette skiltet for handlingen min akkurat her?',
    fallbackMemory: 'Form → farge → symbol → handling.',
  },
  th: {
    title: 'ป้ายจราจร',
    all: 'ทั้งหมด',
    close: 'ปิด',
    loading: 'กำลังโหลดป้าย',
    noData: 'โหลดข้อมูลป้ายไม่ได้',
    meaning: 'ป้ายนี้หมายความว่าอะไร?',
    driver: 'ผู้ขับขี่ต้องทำอะไร?',
    mistake: 'ข้อผิดพลาดที่พบบ่อย',
    exam: 'เคล็ดลับสอบ',
    memory: 'วิธีจำ',
    scenario: 'สถานการณ์จริง',
    related: 'ป้ายที่เกี่ยวข้อง',
    confused: 'มักสับสนกับ',
    practice: 'ฝึกป้ายนี้',
    askAi: 'ถามครู AI',
    audio: 'อ่านออกเสียง',
    save: 'บันทึก',
    saved: 'บันทึกแล้ว',
    aiTeacher: 'ครู AI',
    video: 'ดูคำอธิบายสั้น',
    fallbackMeaning: 'ดูรูปทรง สี และสัญลักษณ์ แล้วเชื่อมกับสถานการณ์บนถนนจริง',
    fallbackDriver: 'ปรับความเร็ว ตำแหน่งรถ และความระวังตามสิ่งที่ป้ายบอก',
    fallbackMistake: 'อย่าดูป้ายแยกจากถนน ให้ดูป้ายเสริมและบริบทรอบ ๆ ด้วย',
    fallbackExam: 'ถามตัวเองว่า: ป้ายนี้เปลี่ยนการกระทำของฉันตรงนี้อย่างไร?',
    fallbackMemory: 'รูปทรง → สี → สัญลักษณ์ → สิ่งที่ต้องทำ',
  },
  en: {
    title: 'Traffic signs',
    all: 'All',
    close: 'Close',
    loading: 'Loading signs',
    noData: 'Could not load signs.',
    meaning: 'What does this sign mean?',
    driver: 'What must the driver do?',
    mistake: 'Common mistake',
    exam: 'Exam tip',
    memory: 'Memory rule',
    scenario: 'Real traffic situation',
    related: 'Related signs',
    confused: 'Often confused with',
    practice: 'Practice this sign',
    askAi: 'Ask AI Teacher',
    audio: 'Read aloud',
    save: 'Save',
    saved: 'Saved',
    aiTeacher: 'AI teacher',
    video: 'Watch short explanation',
    fallbackMeaning: 'Read the shape, colour, and symbol, and connect the sign to the road situation.',
    fallbackDriver: 'Adapt speed, position, and attention to what the sign tells you.',
    fallbackMistake: 'Do not read the sign alone. Look at supplementary signs and the traffic context.',
    fallbackExam: 'Ask: what does this sign change about my action right here?',
    fallbackMemory: 'Shape → colour → symbol → action.',
  },
};

function pick(text: any, lang: Lang): string {
  if (!text) return '';
  if (typeof text === 'string') return text;
  return text[lang] || text.no || text.en || text.th || '';
}

function signCode(sign: TrafficSign): string {
  return String(sign.order || sign.id || '').match(/\d{3}(?:\.\d+)?/)?.[0] || String(sign.order || sign.id || '');
}

function videoTitle(video: LearningVideo, lang: Lang) {
  return lang === 'th' ? (video.title_th || video.title_no || video.title_en || '') :
    lang === 'en' ? (video.title_en || video.title_no || video.title_th || '') :
    (video.title_no || video.title_en || video.title_th || '');
}

function videoSummary(video: LearningVideo, lang: Lang) {
  return lang === 'th' ? (video.instructor_summary_th || video.instructor_summary_no || video.instructor_summary_en || '') :
    lang === 'en' ? (video.instructor_summary_en || video.instructor_summary_no || video.instructor_summary_th || '') :
    (video.instructor_summary_no || video.instructor_summary_en || video.instructor_summary_th || '');
}

export default function SignsScreen() {
  const router = useRouter();
  const { language, colors } = useAppStore();
  const lang = (['no', 'th', 'en'].includes(language) ? language : 'th') as Lang;
  const t = TR[lang];

  const [groups, setGroups] = useState<TrafficSignGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeGroup, setActiveGroup] = useState<number | 'all'>('all');
  const [selected, setSelected] = useState<TrafficSign | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<TrafficSignGroup | null>(null);
  const [lessonLang, setLessonLang] = useState<Lang>(lang);
  const [favoriteIds, setFavoriteIds] = useState<string[]>([]);
  const [aiOpen, setAiOpen] = useState(false);
  const [video, setVideo] = useState<LearningVideo | null>(null);

  useEffect(() => {
    let alive = true;
    api.getTrafficSigns()
      .then(data => { if (alive) setGroups(data); })
      .catch(() => { if (alive) setGroups([]); })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, []);

  useEffect(() => setLessonLang(lang), [lang]);

  const allSigns = useMemo(() => groups.flatMap(g => g.signs.map(s => ({ sign: s, group: g }))), [groups]);
  const displayed = activeGroup === 'all'
    ? allSigns
    : allSigns.filter(item => item.group.group === activeGroup);

  const related = useMemo(() => {
    if (!selected || !selectedGroup) return [];
    return selectedGroup.signs
      .filter(s => s.id !== selected.id)
      .sort((a, b) => Math.abs((a.order || 9999) - (selected.order || 9999)) - Math.abs((b.order || 9999) - (selected.order || 9999)))
      .slice(0, 8);
  }, [selected, selectedGroup]);

  const openSign = (sign: TrafficSign, group: TrafficSignGroup) => {
    setSelected(sign);
    setSelectedGroup(group);
    setLessonLang(lang);
    setAiOpen(false);
    setVideo(null);
    const groupNo = pick(group.group_name, 'no');
    api.getVideosForSign(sign.id, groupNo, 1).then(v => setVideo(v[0] || null)).catch(() => setVideo(null));
  };

  const toggleFavorite = () => {
    if (!selected) return;
    setFavoriteIds(ids => ids.includes(selected.id) ? ids.filter(id => id !== selected.id) : [...ids, selected.id]);
  };

  const lessonName = selected ? pick(selected.name, lessonLang) || signCode(selected) : '';
  const isFav = selected ? favoriteIds.includes(selected.id) : false;

  const renderLessonCard = (icon: string, label: string, text?: string) => {
    if (!text) return null;
    return (
      <View style={[styles.lessonCard, { borderColor: colors.cardBorder, backgroundColor: colors.card }]}>
        <Text style={styles.lessonIcon}>{icon}</Text>
        <View style={{ flex: 1 }}>
          <Text style={[styles.lessonLabel, { color: colors.accent }]}>{label}</Text>
          <Text style={[styles.lessonText, { color: colors.text }]}>{text}</Text>
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.bg }]}>
      <View style={[styles.header, { borderBottomColor: colors.divider }]}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: colors.text }]}>{t.title}</Text>
        <View style={{ width: 40 }} />
      </View>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.accent} />
          <Text style={[styles.loadingText, { color: colors.textMuted }]}>{t.loading}</Text>
        </View>
      ) : groups.length === 0 ? (
        <View style={styles.center}><Text style={{ color: colors.textMuted }}>{t.noData}</Text></View>
      ) : (
        <>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll} contentContainerStyle={styles.filterRow}>
            <TouchableOpacity style={[styles.chip, activeGroup === 'all' && { backgroundColor: colors.accent }]} onPress={() => setActiveGroup('all')}>
              <Text style={[styles.chipText, { color: activeGroup === 'all' ? '#0F172A' : colors.textMuted }]}>{t.all}</Text>
            </TouchableOpacity>
            {groups.map(group => {
              const active = activeGroup === group.group;
              return (
                <TouchableOpacity key={group.group} style={[styles.chip, active && { backgroundColor: colors.accent }]} onPress={() => setActiveGroup(group.group)}>
                  <Text style={[styles.chipText, { color: active ? '#0F172A' : colors.textMuted }]}>
                    {pick(group.group_name, lang)} ({group.signs.length})
                  </Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>

          <FlatList
            data={displayed}
            keyExtractor={item => item.sign.id}
            numColumns={3}
            contentContainerStyle={styles.grid}
            renderItem={({ item }) => (
              <TouchableOpacity style={[styles.signCard, { backgroundColor: colors.card, borderColor: colors.cardBorder }]} onPress={() => openSign(item.sign, item.group)} activeOpacity={0.8}>
                <View style={styles.signImageWrap}>
                  {!!item.sign.image_url && <Image source={{ uri: item.sign.image_url }} style={styles.signImage} resizeMode="contain" />}
                </View>
                <Text style={[styles.signCode, { color: colors.accent }]}>{signCode(item.sign)}</Text>
                <Text style={[styles.signName, { color: colors.text }]} numberOfLines={2}>{pick(item.sign.name, lang) || pick(item.sign.name, 'no') || signCode(item.sign)}</Text>
              </TouchableOpacity>
            )}
          />
        </>
      )}

      <Modal visible={!!selected} transparent animationType="slide" onRequestClose={() => setSelected(null)}>
        <View style={styles.modalOverlay}>
          <View style={[styles.sheet, { backgroundColor: colors.bg }]}>
            {selected && selectedGroup && (
              <>
                <View style={styles.sheetHandle} />
                <View style={styles.sheetHeader}>
                  <View style={styles.panelImageWrap}>
                    {!!selected.image_url && <Image source={{ uri: selected.image_url }} style={styles.panelImage} resizeMode="contain" />}
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={[styles.groupLabel, { color: colors.accent }]}>{pick(selectedGroup.group_name, lang)}</Text>
                    <Text style={[styles.panelTitle, { color: colors.text }]}>{lessonName}</Text>
                    <Text style={[styles.panelSubtitle, { color: colors.textMuted }]}>{pick(selected.name, 'no')} · {pick(selected.name, 'th')} · {pick(selected.name, 'en')}</Text>
                  </View>
                  <TouchableOpacity onPress={() => setSelected(null)} style={styles.iconBtn}>
                    <Ionicons name="close" size={22} color={colors.text} />
                  </TouchableOpacity>
                </View>

                <View style={styles.langTabs}>
                  {(['no', 'th', 'en'] as Lang[]).map(l => (
                    <TouchableOpacity key={l} onPress={() => setLessonLang(l)} style={[styles.langTab, lessonLang === l && { backgroundColor: colors.accent }]}>
                      <Text style={[styles.langTabText, { color: lessonLang === l ? '#0F172A' : colors.textMuted }]}>{l === 'no' ? 'Norsk' : l === 'th' ? 'ไทย' : 'English'}</Text>
                    </TouchableOpacity>
                  ))}
                </View>

                <ScrollView style={styles.sheetScroll} contentContainerStyle={styles.sheetContent}>
                  {renderLessonCard('📖', t.meaning, pick(selected.explanation, lessonLang) || t.fallbackMeaning)}
                  {renderLessonCard('⚠️', t.driver, pick(selected.whyDangerous || selected.why_dangerous, lessonLang) || t.fallbackDriver)}
                  {renderLessonCard('🔴', t.mistake, pick(selected.typicalMistake || selected.typical_mistake, lessonLang) || t.fallbackMistake)}
                  {renderLessonCard('📝', t.exam, pick(selected.examTip || selected.exam_tip, lessonLang) || t.fallbackExam)}
                  {renderLessonCard('💡', t.memory, pick(selected.memoryRule || selected.memory_rule, lessonLang) || t.fallbackMemory)}
                  {renderLessonCard('🚗', t.scenario, pick(selected.realScenario || selected.real_scenario, lessonLang))}

                  <View style={[styles.relatedBox, { borderColor: colors.cardBorder, backgroundColor: colors.card }]}>
                    <Text style={[styles.relatedTitle, { color: colors.text }]}>{t.confused}</Text>
                    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.relatedRow}>
                      {related.slice(0, 6).map(sign => (
                        <TouchableOpacity key={sign.id} style={[styles.relatedCard, { borderColor: colors.cardBorder }]} onPress={() => openSign(sign, selectedGroup)}>
                          {!!sign.image_url && <Image source={{ uri: sign.image_url }} style={styles.relatedImage} resizeMode="contain" />}
                          <Text style={[styles.relatedCode, { color: colors.accent }]}>{signCode(sign)}</Text>
                          <Text style={[styles.relatedName, { color: colors.text }]} numberOfLines={2}>{pick(sign.name, lessonLang) || signCode(sign)}</Text>
                        </TouchableOpacity>
                      ))}
                    </ScrollView>
                  </View>

                  {video && (
                    <TouchableOpacity style={[styles.videoCard, { borderColor: colors.cardBorder, backgroundColor: colors.card }]} onPress={() => Linking.openURL(video.youtube_url)}>
                      {!!video.thumbnail_url && <Image source={{ uri: video.thumbnail_url }} style={styles.videoThumb} />}
                      <View style={{ flex: 1 }}>
                        <Text style={[styles.videoLabel, { color: colors.accent }]}>📹 {t.video}</Text>
                        <Text style={[styles.videoTitle, { color: colors.text }]}>{videoTitle(video, lessonLang)}</Text>
                        {!!videoSummary(video, lessonLang) && <Text style={[styles.videoSummary, { color: colors.textMuted }]} numberOfLines={2}>{videoSummary(video, lessonLang)}</Text>}
                      </View>
                    </TouchableOpacity>
                  )}

                  {aiOpen && renderLessonCard('🤖', t.aiTeacher, [
                    `${t.meaning} ${pick(selected.explanation, lessonLang) || t.fallbackMeaning}`,
                    `${t.driver} ${pick(selected.whyDangerous || selected.why_dangerous, lessonLang) || t.fallbackDriver}`,
                    `${t.memory} ${pick(selected.memoryRule || selected.memory_rule, lessonLang) || t.fallbackMemory}`,
                  ].join('\n\n'))}
                </ScrollView>

                <View style={[styles.actions, { borderTopColor: colors.divider }]}>
                  <TouchableOpacity style={[styles.primaryBtn, { backgroundColor: colors.accent }]} onPress={() => router.push('/categories')}>
                    <Text style={styles.primaryBtnText}>📚 {t.practice}</Text>
                  </TouchableOpacity>
                  <View style={styles.actionRow}>
                    <TouchableOpacity style={[styles.secondaryBtn, { borderColor: colors.cardBorder }]}><Text style={[styles.secondaryText, { color: colors.text }]}>🔊 {t.audio}</Text></TouchableOpacity>
                    <TouchableOpacity style={[styles.secondaryBtn, { borderColor: colors.cardBorder }]} onPress={() => setAiOpen(true)}><Text style={[styles.secondaryText, { color: colors.text }]}>🤖 {t.askAi}</Text></TouchableOpacity>
                    <TouchableOpacity style={[styles.secondaryBtn, { borderColor: colors.cardBorder }]} onPress={toggleFavorite}><Text style={[styles.secondaryText, { color: colors.text }]}>🔖 {isFav ? t.saved : t.save}</Text></TouchableOpacity>
                  </View>
                </View>
              </>
            )}
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 10 },
  loadingText: { fontSize: 13, fontWeight: '700' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1 },
  backBtn: { width: 40, height: 40, justifyContent: 'center' },
  headerTitle: { flex: 1, fontSize: 17, fontWeight: '800', textAlign: 'center' },
  filterScroll: { maxHeight: 54, flexGrow: 0 },
  filterRow: { paddingHorizontal: 12, paddingVertical: 8, gap: 8, flexDirection: 'row' },
  chip: { paddingHorizontal: 14, paddingVertical: 7, borderRadius: 999, backgroundColor: 'rgba(255,255,255,.08)' },
  chipText: { fontSize: 13, fontWeight: '800' },
  grid: { padding: 12, paddingBottom: 28 },
  signCard: { flex: 1, margin: 4, borderRadius: 12, borderWidth: 1, padding: 10, alignItems: 'center', gap: 6, minHeight: 126 },
  signImageWrap: { height: 58, width: '100%', justifyContent: 'center', alignItems: 'center' },
  signImage: { width: 70, height: 58 },
  signCode: { fontSize: 11, fontWeight: '900' },
  signName: { fontSize: 11, fontWeight: '700', textAlign: 'center', lineHeight: 15 },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,.62)', justifyContent: 'flex-end' },
  sheet: { maxHeight: '92%', borderTopLeftRadius: 24, borderTopRightRadius: 24, overflow: 'hidden' },
  sheetHandle: { alignSelf: 'center', width: 44, height: 4, borderRadius: 999, backgroundColor: 'rgba(255,255,255,.28)', marginTop: 10 },
  sheetHeader: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingHorizontal: 16, paddingTop: 14, paddingBottom: 10 },
  panelImageWrap: { width: 76, height: 76, borderRadius: 14, backgroundColor: 'rgba(0,0,0,.18)', alignItems: 'center', justifyContent: 'center' },
  panelImage: { width: 68, height: 68 },
  groupLabel: { fontSize: 11, fontWeight: '900', textTransform: 'uppercase', letterSpacing: .6 },
  panelTitle: { fontSize: 20, fontWeight: '900', marginTop: 3 },
  panelSubtitle: { fontSize: 11, lineHeight: 15, marginTop: 3 },
  iconBtn: { width: 36, height: 36, borderRadius: 18, alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(255,255,255,.06)' },
  langTabs: { flexDirection: 'row', gap: 8, paddingHorizontal: 16, paddingBottom: 10 },
  langTab: { flex: 1, alignItems: 'center', paddingVertical: 8, borderRadius: 999, backgroundColor: 'rgba(255,255,255,.07)' },
  langTabText: { fontSize: 12, fontWeight: '900' },
  sheetScroll: { flexGrow: 0 },
  sheetContent: { padding: 16, gap: 10, paddingBottom: 16 },
  lessonCard: { flexDirection: 'row', gap: 10, borderWidth: 1, borderRadius: 14, padding: 13 },
  lessonIcon: { fontSize: 20, width: 28, textAlign: 'center' },
  lessonLabel: { fontSize: 11, fontWeight: '900', textTransform: 'uppercase', letterSpacing: .7, marginBottom: 5 },
  lessonText: { fontSize: 14, lineHeight: 21, fontWeight: '600' },
  relatedBox: { borderWidth: 1, borderRadius: 14, padding: 12, gap: 10 },
  relatedTitle: { fontSize: 13, fontWeight: '900' },
  relatedRow: { gap: 8 },
  relatedCard: { width: 112, borderWidth: 1, borderRadius: 12, padding: 8, gap: 5, backgroundColor: 'rgba(255,255,255,.035)' },
  relatedImage: { width: '100%', height: 48 },
  relatedCode: { fontSize: 10, fontWeight: '900' },
  relatedName: { fontSize: 11, fontWeight: '700', lineHeight: 14 },
  videoCard: { flexDirection: 'row', gap: 10, borderWidth: 1, borderRadius: 14, padding: 10 },
  videoThumb: { width: 92, height: 58, borderRadius: 10, backgroundColor: 'rgba(0,0,0,.2)' },
  videoLabel: { fontSize: 11, fontWeight: '900', marginBottom: 3 },
  videoTitle: { fontSize: 13, fontWeight: '900' },
  videoSummary: { fontSize: 12, lineHeight: 17, marginTop: 3 },
  actions: { borderTopWidth: 1, padding: 12, gap: 9 },
  primaryBtn: { borderRadius: 14, paddingVertical: 13, alignItems: 'center' },
  primaryBtnText: { color: '#0F172A', fontSize: 15, fontWeight: '900' },
  actionRow: { flexDirection: 'row', gap: 8 },
  secondaryBtn: { flex: 1, borderWidth: 1, borderRadius: 12, paddingVertical: 10, alignItems: 'center', backgroundColor: 'rgba(255,255,255,.045)' },
  secondaryText: { fontSize: 11, fontWeight: '900' },
});
