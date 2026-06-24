import React, { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { api, MyStats, CategoryStat } from '../src/services/api';
import { BottomNavBar } from '../src/components/BottomNavBar';

const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Min statistikk', overall: 'Totalt', correct: 'Riktige', attempts: 'Øvelser',
    weakest: 'Svakeste områder', strongest: 'Sterkeste områder', all: 'Alle kategorier',
    noData: 'Ingen data ennå — gjør noen øvelser først!', questions: 'spørsmål',
  },
  th: {
    title: 'สถิติของฉัน', overall: 'ภาพรวม', correct: 'ถูกต้อง', attempts: 'การฝึก',
    weakest: 'หัวข้อที่อ่อนแอ', strongest: 'หัวข้อที่แข็งแกร่ง', all: 'ทุกหมวดหมู่',
    noData: 'ยังไม่มีข้อมูล — ทำแบบฝึกหัดก่อน!', questions: 'ข้อ',
  },
  en: {
    title: 'My Statistics', overall: 'Overall', correct: 'Correct', attempts: 'Sessions',
    weakest: 'Weakest areas', strongest: 'Strongest areas', all: 'All categories',
    noData: 'No data yet — do some practice first!', questions: 'questions',
  },
};

const CAT_LABELS: Record<string, { no: string; th: string; en: string }> = {
  'Traffic Signs':            { no: 'Trafikkskilt',    th: 'ป้ายจราจร',      en: 'Traffic Signs' },
  'Road Rules':               { no: 'Trafikkregler',   th: 'กฎจราจร',        en: 'Road Rules' },
  'Right of Way':             { no: 'Vikeplikt',       th: 'การให้ทาง',      en: 'Right of Way' },
  'Speed Limits':             { no: 'Fartsgrenser',    th: 'ความเร็ว',       en: 'Speed Limits' },
  'Safety':                   { no: 'Sikkerhet',       th: 'ความปลอดภัย',    en: 'Safety' },
  'Driving Conditions':       { no: 'Kjøreforhold',    th: 'สภาพการขับขี่', en: 'Driving Conditions' },
  'Situations':               { no: 'Situasjoner',     th: 'สถานการณ์',      en: 'Situations' },
  'Pedestrians and Cyclists': { no: 'Gående/Syklister',th: 'คนเดิน/จักรยาน',en: 'Pedestrians & Cyclists' },
  'Vehicle Knowledge':        { no: 'Kjøretøy',        th: 'ความรู้รถ',      en: 'Vehicle Knowledge' },
  'Environment and Economy':  { no: 'Miljø/Økonomi',   th: 'สิ่งแวดล้อม',    en: 'Environment & Economy' },
};

function catLabel(category: string, lang: 'no' | 'th' | 'en') {
  return CAT_LABELS[category]?.[lang] ?? category;
}

function pctColor(pct: number) {
  if (pct >= 75) return '#10B981';
  if (pct >= 50) return '#F59E0B';
  return '#EF4444';
}

function ScoreBar({ pct, color }: { pct: number; color: string }) {
  return (
    <View style={bar.track}>
      <View style={[bar.fill, { width: `${Math.min(pct, 100)}%` as any, backgroundColor: color }]} />
    </View>
  );
}
const bar = StyleSheet.create({
  track: { height: 8, backgroundColor: 'rgba(255,255,255,.1)', borderRadius: 4, overflow: 'hidden', flex: 1 },
  fill:  { height: 8, borderRadius: 4 },
});

export default function StatsScreen() {
  const router = useRouter();
  const { language, colors, deviceId, user } = useAppStore();
  const c = colors;
  const t = TR[language] || {};
  const lang = language as 'no' | 'th' | 'en';

  const [stats, setStats] = useState<MyStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const targetId = user?.id || deviceId;
    if (!targetId) { setLoading(false); return; }
    api.getMyStats(targetId)
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false));
  }, [deviceId, user]);

  const sorted = stats?.by_category ?? [];
  const weakest   = [...sorted].sort((a, b) => a.pct - b.pct).slice(0, 3);
  const strongest = [...sorted].sort((a, b) => b.pct - a.pct).slice(0, 3);

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
      ) : !stats || stats.overall.total_q === 0 ? (
        <View style={st.center}>
          <Text style={{ fontSize: 48 }}>📊</Text>
          <Text style={[st.emptyText, { color: c.textMuted }]}>{t.noData}</Text>
        </View>
      ) : (
        <ScrollView contentContainerStyle={st.scroll}>

          {/* Overall card */}
          <View style={[st.overallCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={[st.overallLabel, { color: c.textMuted }]}>{t.overall}</Text>
            <Text style={[st.overallPct, { color: pctColor(stats.overall.pct) }]}>
              {Math.round(stats.overall.pct)}%
            </Text>
            <ScoreBar pct={stats.overall.pct} color={pctColor(stats.overall.pct)} />
            <View style={st.overallRow}>
              <View style={st.overallStat}>
                <Text style={[st.overallStatVal, { color: c.text }]}>{stats.overall.total_correct}</Text>
                <Text style={[st.overallStatLbl, { color: c.textMuted }]}>{t.correct}</Text>
              </View>
              <View style={st.overallStat}>
                <Text style={[st.overallStatVal, { color: c.text }]}>{stats.overall.total_q}</Text>
                <Text style={[st.overallStatLbl, { color: c.textMuted }]}>{t.questions}</Text>
              </View>
              <View style={st.overallStat}>
                <Text style={[st.overallStatVal, { color: c.text }]}>{stats.overall.attempts}</Text>
                <Text style={[st.overallStatLbl, { color: c.textMuted }]}>{t.attempts}</Text>
              </View>
            </View>
          </View>

          {/* Weakest */}
          {weakest.length > 0 && (
            <>
              <Text style={[st.sectionHead, { color: c.textMuted }]}>🔴 {t.weakest}</Text>
              {weakest.map(s => <CategoryRow key={s.category} s={s} lang={lang} c={c} />)}
            </>
          )}

          {/* Strongest */}
          {strongest.length > 0 && (
            <>
              <Text style={[st.sectionHead, { color: c.textMuted }]}>🟢 {t.strongest}</Text>
              {strongest.map(s => <CategoryRow key={s.category} s={s} lang={lang} c={c} />)}
            </>
          )}

          {/* All categories */}
          <Text style={[st.sectionHead, { color: c.textMuted }]}>📋 {t.all}</Text>
          {[...sorted].sort((a, b) => b.total_q - a.total_q).map(s => (
            <CategoryRow key={s.category} s={s} lang={lang} c={c} />
          ))}

        </ScrollView>
      )}
      <BottomNavBar activeTab="stats" />
    </SafeAreaView>
  );
}

function CategoryRow({ s, lang, c }: { s: CategoryStat; lang: 'no' | 'th' | 'en'; c: any }) {
  const pct = Math.round(s.pct);
  const color = pctColor(pct);
  return (
    <View style={[st.catRow, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
      <View style={st.catTop}>
        <Text style={[st.catName, { color: c.text }]} numberOfLines={1}>
          {catLabel(s.category, lang)}
        </Text>
        <Text style={[st.catPct, { color }]}>{pct}%</Text>
      </View>
      <View style={st.catBarRow}>
        <ScoreBar pct={pct} color={color} />
        <Text style={[st.catMeta, { color: c.textMuted }]}>
          {s.total_correct}/{s.total_q}
        </Text>
      </View>
    </View>
  );
}

const st = StyleSheet.create({
  container:      { flex: 1 },
  center:         { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12, padding: 24 },
  header:         { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1 },
  backBtn:        { width: 40, height: 40, justifyContent: 'center' },
  headerTitle:    { flex: 1, fontSize: 17, fontWeight: '700', textAlign: 'center' },
  scroll:         { padding: 16, gap: 8, paddingBottom: 110 },
  overallCard:    { borderRadius: 16, borderWidth: 1, padding: 20, marginBottom: 8, gap: 8 },
  overallLabel:   { fontSize: 12, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 1 },
  overallPct:     { fontSize: 48, fontWeight: '900' },
  overallRow:     { flexDirection: 'row', justifyContent: 'space-around', marginTop: 8 },
  overallStat:    { alignItems: 'center', gap: 2 },
  overallStatVal: { fontSize: 20, fontWeight: '800' },
  overallStatLbl: { fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.5 },
  sectionHead:    { fontSize: 11, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 1, marginTop: 12, marginBottom: 4, marginLeft: 4 },
  catRow:         { borderRadius: 12, borderWidth: 1, padding: 14, gap: 8 },
  catTop:         { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  catName:        { fontSize: 14, fontWeight: '600', flex: 1, marginRight: 8 },
  catPct:         { fontSize: 16, fontWeight: '800' },
  catBarRow:      { flexDirection: 'row', alignItems: 'center', gap: 10 },
  catMeta:        { fontSize: 11, minWidth: 40, textAlign: 'right' },
  emptyText:      { fontSize: 15, textAlign: 'center', marginTop: 12 },
});
