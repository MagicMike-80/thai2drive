import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';

const TR: Record<string, Record<string, string>> = {
  no: {
    done: 'Quiz fullført!', score: 'Din poengsum', correct: 'Riktige', of: 'av',
    ready: 'Du er klar for prøven!', good: 'Bra jobbet!', keep: 'Fortsett å øve – du blir bedre!',
    retry: 'Prøv igjen', home: 'Hjem', practice: 'Øving', exam: 'Eksamen',
    passed: 'BESTÅTT', failed: 'IKKE BESTÅTT', threshold: '85% kreves',
    upgrade: 'Oppgrader til Premium', unlockAll: 'Lås opp alle spørsmål',
  },
  th: {
    done: 'ทำแบบทดสอบเสร็จ!', score: 'คะแนน', correct: 'ถูก', of: 'จาก',
    ready: 'คุณพร้อมสอบแล้ว!', good: 'ทำได้ดี!', keep: 'ฝึกซ้อมต่อ – คุณเก่งขึ้นเรื่อยๆ!',
    retry: 'ลองอีกครั้ง', home: 'หน้าหลัก', practice: 'ฝึกซ้อม', exam: 'สอบ',
    passed: 'ผ่าน', failed: 'ไม่ผ่าน', threshold: 'ต้องได้ 85%',
    upgrade: 'อัพเกรดเป็น Premium', unlockAll: 'ปลดล็อคคำถามทั้งหมด',
  },
  en: {
    done: 'Quiz Complete!', score: 'Your Score', correct: 'Correct', of: 'out of',
    ready: "You're ready for the test!", good: 'Good job!', keep: "Keep practicing – you're improving!",
    retry: 'Try Again', home: 'Home', practice: 'Practice', exam: 'Exam',
    passed: 'PASSED', failed: 'FAILED', threshold: '85% required',
    upgrade: 'Upgrade to Premium', unlockAll: 'Unlock all questions',
  },
};

export default function ResultsScreen() {
  const router = useRouter();
  const { total, correct, mode, passed } = useLocalSearchParams<{ total: string; correct: string; mode: string; passed: string }>();
  const { language, isPremium } = useAppStore();
  const t = TR[language] || TR.en;
  const c = useAppStore((s) => s.colors);

  const tot = parseInt(total || '0', 10);
  const cor = parseInt(correct || '0', 10);
  const pct = tot > 0 ? Math.round((cor / tot) * 100) : 0;
  const isExam = mode === 'exam';
  const examPass = passed === 'true';

  const msg = () => {
    if (isExam) return examPass ? t.passed : t.failed;
    if (pct >= 80) return t.ready;
    if (pct >= 50) return t.good;
    return t.keep;
  };

  const emoji = () => {
    if (isExam) return examPass ? '🏆' : '💪';
    if (pct >= 80) return '🔥';
    if (pct >= 50) return '👍';
    return '📚';
  };

  const col = () => {
    if (isExam) return examPass ? c.correct : c.incorrect;
    if (pct >= 80) return c.correct;
    if (pct >= 50) return c.accent;
    return c.incorrect;
  };

  const color = col();

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <View style={st.content}>
        {/* Emoji */}
        <Text style={st.emoji}>{emoji()}</Text>

        {/* Dynamic message */}
        <Text testID="result-message" style={[st.msg, { color }]}>{msg()}</Text>
        <Text style={[st.sub, { color: c.textSecondary }]}>{t.done}</Text>

        {/* Score card */}
        <View style={[st.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
          <Text style={[st.lbl, { color: c.textMuted }]}>{t.score}</Text>
          <Text testID="result-percentage" style={[st.pct, { color }]}>{pct}%</Text>
          <Text style={[st.det, { color: c.textMuted }]}>{cor} {t.correct} {t.of} {tot}</Text>
          <View style={[st.bar, { backgroundColor: c.progressBg }]}>
            <View style={[st.fill, { width: `${pct}%`, backgroundColor: color }]} />
          </View>
          {isExam && <Text style={[st.thr, { color: c.textMuted }]}>{t.threshold}</Text>}
        </View>

        {/* Mode badge */}
        <View style={[st.badge, { backgroundColor: c.card }]}>
          <Ionicons name={mode === 'practice' ? 'book-outline' : 'school-outline'} size={16} color={c.textSecondary} />
          <Text style={[st.badgeT, { color: c.textSecondary }]}>{mode === 'practice' ? t.practice : t.exam}</Text>
        </View>
      </View>

      {/* Actions */}
      <View style={st.actions}>
        {/* Premium upsell for non-premium users */}
        {!isPremium && (
          <TouchableOpacity testID="result-upgrade-btn" style={[st.upgradeBtn, { borderColor: c.accent }]} onPress={() => router.push('/paywall')} activeOpacity={0.8}>
            <Ionicons name="diamond" size={16} color={c.accent} />
            <Text style={[st.upgradeT, { color: c.accent }]}>{t.upgrade}</Text>
          </TouchableOpacity>
        )}

        <View style={st.btnRow}>
          <TouchableOpacity testID="result-home-btn" style={[st.secBtn, { backgroundColor: c.card, borderColor: c.cardBorder }]} onPress={() => router.replace('/')}>
            <Ionicons name="home-outline" size={18} color={c.textSecondary} />
            <Text style={[st.secT, { color: c.textSecondary }]}>{t.home}</Text>
          </TouchableOpacity>
          <TouchableOpacity testID="result-retry-btn" style={[st.priBtn, { backgroundColor: c.accent }]}
            onPress={() => { isExam ? router.replace({ pathname: '/quiz', params: { mode: 'exam', category: 'all' } }) : router.replace({ pathname: '/categories', params: { mode } }); }}>
            <Ionicons name="refresh" size={18} color="#0F172A" />
            <Text style={st.priT}>{t.retry}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  container: { flex: 1 },
  content: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  emoji: { fontSize: 56, marginBottom: 12 },
  msg: { fontSize: 26, fontWeight: '800', textAlign: 'center', marginBottom: 4 },
  sub: { fontSize: 15, marginBottom: 28 },
  card: { borderRadius: 20, padding: 28, alignItems: 'center', width: '100%', marginBottom: 16, borderWidth: 1 },
  lbl: { fontSize: 12, textTransform: 'uppercase', letterSpacing: 1.5, fontWeight: '700', marginBottom: 6 },
  pct: { fontSize: 64, fontWeight: '800' },
  det: { fontSize: 15, marginTop: 4, marginBottom: 18 },
  bar: { width: '100%', height: 7, borderRadius: 4, overflow: 'hidden' },
  fill: { height: '100%', borderRadius: 4 },
  thr: { fontSize: 12, marginTop: 10 },
  badge: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingVertical: 7, borderRadius: 16, gap: 6 },
  badgeT: { fontSize: 13, fontWeight: '600' },
  actions: { padding: 20 },
  upgradeBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 13, gap: 8, borderWidth: 1.5, marginBottom: 10 },
  upgradeT: { fontSize: 15, fontWeight: '700' },
  btnRow: { flexDirection: 'row', gap: 10 },
  secBtn: { flex: 1, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 14, gap: 6, borderWidth: 1 },
  secT: { fontSize: 14, fontWeight: '600' },
  priBtn: { flex: 1, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 14, gap: 6 },
  priT: { fontSize: 14, fontWeight: '700', color: '#0F172A' },
});
