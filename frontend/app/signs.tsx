import React, { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, Modal, FlatList
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { api, Sign, SignGroup } from '../src/services/api';

const TR: Record<string, Record<string, string>> = {
  no: { title: 'Trafikkskilt', close: 'Lukk', noData: 'Kunne ikke laste skilt.' },
  th: { title: 'ป้ายจราจร',   close: 'ปิด',  noData: 'โหลดข้อมูลไม่ได้'      },
  en: { title: 'Traffic Signs', close: 'Close', noData: 'Could not load signs.' },
};

// Renders a recognizable sign shape using only RN Views
function SignShape({ type, color, num }: { type: string; color: string; num: string }) {
  if (type === 'triangle' || type === 'fare') {
    // Approximate triangle with a rotated square
    return (
      <View style={[ss.triOuter, { borderBottomColor: color }]}>
        <View style={ss.triInner}>
          <Text style={ss.shapeNum}>{num}</Text>
        </View>
      </View>
    );
  }
  if (type === 'rect' || type === 'opplysning') {
    return (
      <View style={[ss.rect, { backgroundColor: color }]}>
        <Text style={ss.shapeNumWhite}>{num}</Text>
      </View>
    );
  }
  // Default: circle (forbud / pabud / vikeplikt)
  const bg   = type === 'forbud' ? '#fff' : color;
  const border = type === 'forbud' ? color : 'transparent';
  const textColor = type === 'forbud' ? color : '#fff';
  return (
    <View style={[ss.circle, { backgroundColor: bg, borderColor: border, borderWidth: type === 'forbud' ? 3 : 0 }]}>
      {type === 'forbud' && <View style={ss.diagonal} />}
      <Text style={[ss.shapeNum, { color: textColor, fontSize: 10 }]}>{num}</Text>
    </View>
  );
}

const ss = StyleSheet.create({
  triOuter:      { width: 0, height: 0, borderLeftWidth: 30, borderRightWidth: 30, borderBottomWidth: 52, borderLeftColor: 'transparent', borderRightColor: 'transparent', alignItems: 'center' },
  triInner:      { position: 'absolute', top: 18, alignItems: 'center' },
  circle:        { width: 56, height: 56, borderRadius: 28, alignItems: 'center', justifyContent: 'center', overflow: 'hidden' },
  diagonal:      { position: 'absolute', width: 3, height: 60, backgroundColor: '#EF4444', transform: [{ rotate: '-45deg' }] },
  rect:          { width: 56, height: 40, borderRadius: 6, alignItems: 'center', justifyContent: 'center' },
  shapeNum:      { fontSize: 10, fontWeight: '900', color: '#1a1a1a' },
  shapeNumWhite: { fontSize: 10, fontWeight: '900', color: '#fff' },
});

export default function SignsScreen() {
  const router = useRouter();
  const { language, colors } = useAppStore();
  const c = colors;
  const t = TR[language] || TR.no;
  const lang = language as 'no' | 'th' | 'en';

  const [groups, setGroups] = useState<Record<string, SignGroup>>({});
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Sign | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<SignGroup | null>(null);
  const [activeType, setActiveType] = useState<string>('all');

  useEffect(() => {
    api.getSigns()
      .then(setGroups)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const typeKeys = Object.keys(groups);
  const allSigns: Sign[] = typeKeys.flatMap(k => groups[k].signs);
  const displayed = activeType === 'all'
    ? allSigns
    : (groups[activeType]?.signs ?? []);

  const openSign = (sign: Sign, type: string) => {
    setSelected(sign);
    setSelectedGroup(groups[type] ?? null);
  };

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
        <View style={st.center}><ActivityIndicator size="large" color={c.accent} /></View>
      ) : (
        <>
          {/* Filter tabs */}
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={st.filterScroll} contentContainerStyle={st.filterRow}>
            <TouchableOpacity
              style={[st.chip, activeType === 'all' && { backgroundColor: c.accent }]}
              onPress={() => setActiveType('all')}>
              <Text style={[st.chipText, { color: activeType === 'all' ? '#0F172A' : c.textMuted }]}>Alle</Text>
            </TouchableOpacity>
            {typeKeys.map(key => {
              const meta = groups[key].meta;
              const active = activeType === key;
              return (
                <TouchableOpacity
                  key={key}
                  style={[st.chip, active && { backgroundColor: meta.color }]}
                  onPress={() => setActiveType(key)}>
                  <Text style={[st.chipText, { color: active ? '#fff' : c.textMuted }]}>
                    {meta[lang] ?? meta.no}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>

          {/* Grid */}
          <FlatList
            data={displayed}
            keyExtractor={(item, i) => item.num + i}
            numColumns={3}
            contentContainerStyle={st.grid}
            renderItem={({ item }) => {
              const type = typeKeys.find(k => groups[k].signs.includes(item)) ?? 'forbud';
              const meta = groups[type]?.meta;
              return (
                <TouchableOpacity
                  style={[st.signCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}
                  onPress={() => openSign(item, type)}
                  activeOpacity={0.75}>
                  <View style={st.shapeWrapper}>
                    <SignShape type={meta?.shape ?? 'circle'} color={meta?.color ?? '#EF4444'} num={item.num} />
                  </View>
                  <Text style={[st.signName, { color: c.text }]} numberOfLines={2}>
                    {item.name[lang] ?? item.name.no}
                  </Text>
                </TouchableOpacity>
              );
            }}
          />
        </>
      )}

      {/* Detail modal */}
      <Modal visible={!!selected} transparent animationType="slide" onRequestClose={() => setSelected(null)}>
        <View style={st.modalOverlay}>
          <View style={[st.modalBox, { backgroundColor: c.card }]}>
            {selected && selectedGroup && (
              <>
                <View style={st.modalShape}>
                  <SignShape type={selectedGroup.meta.shape} color={selectedGroup.meta.color} num={selected.num} />
                </View>
                <Text style={[st.modalType, { color: selectedGroup.meta.color }]}>
                  {selectedGroup.meta[lang] ?? selectedGroup.meta.no}
                </Text>
                <Text style={[st.modalTitle, { color: c.text }]}>
                  {selected.name[lang] ?? selected.name.no}
                </Text>
                <View style={[st.modalDivider, { backgroundColor: c.divider }]} />

                {(['no', 'th', 'en'] as const).map(l => (
                  <View key={l} style={[st.modalLang, { borderColor: c.divider }]}>
                    <Text style={[st.modalLangLabel, { color: c.textMuted }]}>
                      {l === 'no' ? '🇳🇴' : l === 'th' ? '🇹🇭' : '🇬🇧'}
                      {'  '}{selected.name[l]}
                    </Text>
                    <Text style={[st.modalDesc, { color: c.text }]}>{selected.desc[l]}</Text>
                  </View>
                ))}

                <TouchableOpacity
                  style={[st.closeBtn, { backgroundColor: c.accent }]}
                  onPress={() => setSelected(null)}>
                  <Text style={st.closeBtnText}>{t.close}</Text>
                </TouchableOpacity>
              </>
            )}
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  container:    { flex: 1 },
  center:       { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header:       { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1 },
  backBtn:      { width: 40, height: 40, justifyContent: 'center' },
  headerTitle:  { flex: 1, fontSize: 17, fontWeight: '700', textAlign: 'center' },
  filterScroll: { maxHeight: 52, flexGrow: 0 },
  filterRow:    { paddingHorizontal: 12, paddingVertical: 8, gap: 8, flexDirection: 'row' },
  chip:         { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 999, backgroundColor: 'rgba(255,255,255,.08)' },
  chipText:     { fontSize: 13, fontWeight: '600' },
  grid:         { padding: 12, gap: 10 },
  signCard:     { flex: 1, margin: 4, borderRadius: 12, borderWidth: 1, padding: 12, alignItems: 'center', gap: 8, minHeight: 110 },
  shapeWrapper: { height: 60, justifyContent: 'center', alignItems: 'center' },
  signName:     { fontSize: 11, fontWeight: '600', textAlign: 'center', lineHeight: 15 },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,.6)', justifyContent: 'flex-end' },
  modalBox:     { borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 28, paddingBottom: 40, gap: 8 },
  modalShape:   { alignItems: 'center', marginBottom: 8 },
  modalType:    { fontSize: 11, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 1 },
  modalTitle:   { fontSize: 22, fontWeight: '800', color: '#fff' },
  modalDivider: { height: 1, marginVertical: 8 },
  modalLang:    { paddingVertical: 10, borderBottomWidth: 1, gap: 4 },
  modalLangLabel:{ fontSize: 13, fontWeight: '700' },
  modalDesc:    { fontSize: 14, lineHeight: 21 },
  closeBtn:     { marginTop: 16, padding: 14, borderRadius: 12, alignItems: 'center' },
  closeBtnText: { color: '#0F172A', fontWeight: '800', fontSize: 16 },
});
