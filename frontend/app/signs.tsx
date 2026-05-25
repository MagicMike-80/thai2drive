import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, Modal, FlatList, Image, Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { api, TrafficSign, TrafficSignGroup, LearningVideo } from '../src/services/api';

// ── Group metadata: colors match production web SIGN_GROUP_META ──────────────
const GROUP_COLORS: Record<number, string> = {
  1: '#EF4444', // Vikepliktskilt
  2: '#F59E0B', // Fareskilt
  3: '#DC2626', // Forbudtskilt
  4: '#3B82F6', // Påbudsskilt
  5: '#10B981', // Opplysningsskilt
  6: '#8B5CF6', // Serviceskilt
  7: '#06B6D4', // Veivisningsskilt
  8: '#94A3B8', // Underskilt
  9: '#F97316', // Markeringsskilt
};

// Norwegian group name → sign group number (for video lookup)
function groupNameFromNum(num: number): string {
  const map: Record<number, string> = {
    1: 'Vikepliktskilt',
    2: 'Fareskilt',
    3: 'Forbudtskilt',
    4: 'Påbudsskilt',
    5: 'Opplysningsskilt',
    6: 'Serviceskilt',
    7: 'Veivisningsskilt',
    8: 'Underskilt',
    9: 'Markeringsskilt',
  };
  return map[num] || '';
}

const TR: Record<string, Record<string, string>> = {
  no: {
    title:    'Trafikkskilt',
    all:      'Alle',
    close:    'Lukk',
    noData:   'Kunne ikke laste skilt.',
    noExpl:   'Ingen forklaring tilgjengelig',
    watchVid: '▶ Se video',
    signs:    'skilt',
  },
  th: {
    title:    'ป้ายจราจร',
    all:      'ทั้งหมด',
    close:    'ปิด',
    noData:   'โหลดข้อมูลไม่ได้',
    noExpl:   'ไม่มีคำอธิบาย',
    watchVid: '▶ ดูวิดีโอ',
    signs:    'ป้าย',
  },
  en: {
    title:    'Traffic Signs',
    all:      'All',
    close:    'Close',
    noData:   'Could not load signs.',
    noExpl:   'No explanation available',
    watchVid: '▶ Watch video',
    signs:    'signs',
  },
};

// Fetch video for a sign (cached per session in module scope)
const _videoCache: Record<string, LearningVideo | null> = {};
async function fetchVideoForSign(signId: string, groupNum: number): Promise<LearningVideo | null> {
  const key = `sign:${signId}`;
  if (Object.prototype.hasOwnProperty.call(_videoCache, key)) return _videoCache[key];
  const groupName = groupNameFromNum(groupNum);
  const v = await api.getVideoForSign(signId, groupName);
  _videoCache[key] = v;
  return v;
}

// ── Sign detail modal ──────────────────────────────────────────────────────────
interface SignDetailProps {
  sign: TrafficSign | null;
  group: TrafficSignGroup | null;
  lang: string;
  colors: any;
  tr: Record<string, string>;
  onClose: () => void;
}

function SignDetailModal({ sign, group, lang, colors: c, tr, onClose }: SignDetailProps) {
  const [panelLang, setPanelLang] = useState<'no' | 'th' | 'en'>(lang as 'no' | 'th' | 'en');
  const [video, setVideo] = useState<LearningVideo | null | undefined>(undefined);
  const groupColor = group ? (GROUP_COLORS[group.group] || c.accent) : c.accent;

  useEffect(() => {
    setPanelLang(lang as 'no' | 'th' | 'en');
  }, [lang]);

  useEffect(() => {
    setVideo(undefined);
    if (!sign || !group) return;
    fetchVideoForSign(sign.id, group.group).then(setVideo);
  }, [sign?.id]);

  if (!sign || !group) return null;

  const name = sign.name[panelLang] || sign.name.no || '';
  const expl = sign.explanation[panelLang] || sign.explanation.no || '';
  const groupName = group.group_name[panelLang] || group.group_name.no || '';

  const vidTitle = panelLang === 'th'
    ? (video?.title_th || video?.title_no || '')
    : panelLang === 'en'
    ? (video?.title_en || video?.title_no || '')
    : (video?.title_no || '');

  return (
    <Modal visible animationType="slide" transparent onRequestClose={onClose}>
      <View style={md.overlay}>
        <View style={[md.sheet, { backgroundColor: c.card }]}>
          {/* Handle */}
          <View style={[md.handle, { backgroundColor: c.divider }]} />

          {/* Group label + image */}
          <View style={[md.groupBadge, { backgroundColor: `${groupColor}20`, borderColor: `${groupColor}40` }]}>
            <Text style={[md.groupBadgeText, { color: groupColor }]}>{groupName}</Text>
          </View>

          <Image
            source={{ uri: sign.image_url }}
            style={md.signImage}
            resizeMode="contain"
          />

          <Text style={[md.signName, { color: c.text }]}>{name}</Text>

          {/* Language tabs */}
          <View style={md.langTabs}>
            {(['no', 'th', 'en'] as const).map(l => (
              <TouchableOpacity
                key={l}
                style={[md.langTab, panelLang === l && { backgroundColor: c.accent }]}
                onPress={() => setPanelLang(l)}>
                <Text style={[md.langTabText, { color: panelLang === l ? '#0F172A' : c.textMuted }]}>
                  {l === 'no' ? '🇳🇴' : l === 'th' ? '🇹🇭' : '🇬🇧'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Explanation */}
          <ScrollView style={md.explScroll} showsVerticalScrollIndicator={false}>
            {expl ? (
              <View style={[md.explCard, { backgroundColor: c.bg, borderColor: c.cardBorder }]}>
                <Text style={[md.explLabel, { color: c.accent }]}>📖 {panelLang === 'th' ? 'คำอธิบาย' : panelLang === 'en' ? 'Explanation' : 'Forklaring'}</Text>
                <Text style={[md.explText, { color: c.text }]}>{expl}</Text>
              </View>
            ) : (
              <View style={[md.explCard, { backgroundColor: c.bg, borderColor: c.cardBorder }]}>
                <Text style={[md.explText, { color: c.textMuted }]}>{tr.noExpl}</Text>
              </View>
            )}

            {/* Video button */}
            {video && video.youtube_url ? (
              <TouchableOpacity
                style={[md.vidBtn, { backgroundColor: `${groupColor}15`, borderColor: `${groupColor}40` }]}
                onPress={() => Linking.openURL(video.youtube_url)}
                activeOpacity={0.8}>
                <Ionicons name="play-circle" size={22} color={groupColor} />
                <View style={{ flex: 1 }}>
                  <Text style={[md.vidBtnLabel, { color: c.textMuted }]}>📹 {panelLang === 'th' ? 'วิดีโออธิบาย' : panelLang === 'en' ? 'Explanation video' : 'Forklaringsvideo'}</Text>
                  <Text style={[md.vidBtnTitle, { color: c.text }]} numberOfLines={2}>{vidTitle}</Text>
                </View>
                <Ionicons name="chevron-forward" size={18} color={c.textMuted} />
              </TouchableOpacity>
            ) : null}
          </ScrollView>

          <TouchableOpacity
            style={[md.closeBtn, { backgroundColor: c.accent }]}
            onPress={onClose}>
            <Text style={md.closeBtnText}>{tr.close}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

// ── Main signs screen ──────────────────────────────────────────────────────────
export default function SignsScreen() {
  const router = useRouter();
  const { language, colors } = useAppStore();
  const c = colors;
  const tr = TR[language] || TR.no;
  const lang = language as 'no' | 'th' | 'en';

  const [groups, setGroups] = useState<TrafficSignGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [activeGroup, setActiveGroup] = useState<number>(0); // 0 = all
  const [selected, setSelected] = useState<TrafficSign | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<TrafficSignGroup | null>(null);

  useEffect(() => {
    api.getTrafficSigns()
      .then(data => { setGroups(data || []); setError(false); })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  const allSigns: TrafficSign[] = activeGroup === 0
    ? groups.flatMap(g => g.signs)
    : (groups.find(g => g.group === activeGroup)?.signs ?? []);

  const openSign = useCallback((sign: TrafficSign) => {
    const g = groups.find(gr => gr.group === sign.group) ?? null;
    setSelected(sign);
    setSelectedGroup(g);
  }, [groups]);

  const totalCount = groups.reduce((n, g) => n + g.signs.length, 0);

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      {/* Header */}
      <View style={[st.header, { borderBottomColor: c.divider }]}>
        <TouchableOpacity onPress={() => router.back()} style={st.backBtn}>
          <Ionicons name="arrow-back" size={24} color={c.text} />
        </TouchableOpacity>
        <View style={{ flex: 1 }}>
          <Text style={[st.headerTitle, { color: c.text }]}>{tr.title}</Text>
          {!loading && !error && totalCount > 0 && (
            <Text style={[st.headerCount, { color: c.textMuted }]}>{totalCount} {tr.signs}</Text>
          )}
        </View>
        <View style={{ width: 40 }} />
      </View>

      {loading ? (
        <View style={st.center}>
          <ActivityIndicator size="large" color={c.accent} />
        </View>
      ) : error ? (
        <View style={st.center}>
          <Ionicons name="warning-outline" size={40} color={c.textMuted} />
          <Text style={[st.errText, { color: c.textMuted }]}>{tr.noData}</Text>
        </View>
      ) : (
        <>
          {/* Group filter tabs */}
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={st.filterScroll}
            contentContainerStyle={st.filterRow}>
            <TouchableOpacity
              style={[st.chip, activeGroup === 0 && { backgroundColor: c.accent }]}
              onPress={() => setActiveGroup(0)}>
              <Text style={[st.chipText, { color: activeGroup === 0 ? '#0F172A' : c.textMuted }]}>
                {tr.all}
              </Text>
            </TouchableOpacity>
            {groups.map(g => {
              const gColor = GROUP_COLORS[g.group] || c.accent;
              const active = activeGroup === g.group;
              return (
                <TouchableOpacity
                  key={g.group}
                  style={[st.chip, active && { backgroundColor: gColor }]}
                  onPress={() => setActiveGroup(g.group)}>
                  <Text style={[st.chipText, { color: active ? '#fff' : c.textMuted }]}>
                    {g.group_name[lang] || g.group_name.no}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>

          {/* Sign grid */}
          <FlatList
            data={allSigns}
            keyExtractor={item => item.id}
            numColumns={3}
            contentContainerStyle={st.grid}
            columnWrapperStyle={st.row}
            renderItem={({ item }) => {
              const groupColor = GROUP_COLORS[item.group] || c.accent;
              const nameText = item.name[lang] || item.name.no || item.id;
              return (
                <TouchableOpacity
                  style={[st.signCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}
                  onPress={() => openSign(item)}
                  activeOpacity={0.75}>
                  <View style={[st.imgWrap, { borderColor: `${groupColor}30` }]}>
                    <Image
                      source={{ uri: item.image_url }}
                      style={st.signImg}
                      resizeMode="contain"
                    />
                  </View>
                  <Text style={[st.signName, { color: c.text }]} numberOfLines={2}>
                    {nameText}
                  </Text>
                </TouchableOpacity>
              );
            }}
          />
        </>
      )}

      {/* Sign detail modal */}
      {selected && (
        <SignDetailModal
          sign={selected}
          group={selectedGroup}
          lang={lang}
          colors={c}
          tr={tr}
          onClose={() => { setSelected(null); setSelectedGroup(null); }}
        />
      )}
    </SafeAreaView>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const st = StyleSheet.create({
  container:    { flex: 1 },
  center:       { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12 },
  header:       { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 1 },
  backBtn:      { width: 40, height: 40, justifyContent: 'center' },
  headerTitle:  { fontSize: 17, fontWeight: '700' },
  headerCount:  { fontSize: 12, marginTop: 1 },
  errText:      { fontSize: 15 },
  filterScroll: { maxHeight: 50, flexGrow: 0 },
  filterRow:    { paddingHorizontal: 12, paddingVertical: 7, gap: 8, flexDirection: 'row' },
  chip:         { paddingHorizontal: 13, paddingVertical: 6, borderRadius: 999, backgroundColor: 'rgba(255,255,255,.08)' },
  chipText:     { fontSize: 12, fontWeight: '600' },
  grid:         { padding: 10, paddingBottom: 30 },
  row:          { gap: 8, marginBottom: 8 },
  signCard:     { flex: 1, borderRadius: 12, borderWidth: 1, padding: 10, alignItems: 'center', gap: 6, minHeight: 115 },
  imgWrap:      { width: 64, height: 64, borderRadius: 10, borderWidth: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(255,255,255,.04)' },
  signImg:      { width: 56, height: 56 },
  signName:     { fontSize: 10, fontWeight: '600', textAlign: 'center', lineHeight: 14 },
});

const md = StyleSheet.create({
  overlay:        { flex: 1, backgroundColor: 'rgba(0,0,0,.65)', justifyContent: 'flex-end' },
  sheet:          { borderTopLeftRadius: 24, borderTopRightRadius: 24, paddingTop: 12, paddingHorizontal: 20, paddingBottom: 36 },
  handle:         { width: 40, height: 4, borderRadius: 2, alignSelf: 'center', marginBottom: 16 },
  groupBadge:     { alignSelf: 'center', paddingHorizontal: 12, paddingVertical: 4, borderRadius: 20, borderWidth: 1, marginBottom: 12 },
  groupBadgeText: { fontSize: 11, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 0.8 },
  signImage:      { width: 120, height: 120, alignSelf: 'center', marginBottom: 10 },
  signName:       { fontSize: 22, fontWeight: '800', textAlign: 'center', marginBottom: 14 },
  langTabs:       { flexDirection: 'row', justifyContent: 'center', gap: 8, marginBottom: 14 },
  langTab:        { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 20, backgroundColor: 'rgba(255,255,255,.07)' },
  langTabText:    { fontSize: 18 },
  explScroll:     { maxHeight: 260, marginBottom: 14 },
  explCard:       { borderRadius: 14, padding: 16, borderWidth: 1, marginBottom: 10 },
  explLabel:      { fontSize: 11, fontWeight: '700', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.5 },
  explText:       { fontSize: 14, lineHeight: 21 },
  vidBtn:         { flexDirection: 'row', alignItems: 'center', gap: 10, borderRadius: 14, padding: 14, borderWidth: 1, marginBottom: 8 },
  vidBtnLabel:    { fontSize: 10, fontWeight: '600', marginBottom: 2 },
  vidBtnTitle:    { fontSize: 13, fontWeight: '600', lineHeight: 18 },
  closeBtn:       { borderRadius: 14, paddingVertical: 14, alignItems: 'center' },
  closeBtnText:   { color: '#0F172A', fontWeight: '800', fontSize: 16 },
});
