import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';

const LETTERS = ['A', 'B', 'C', 'D'];

const TR: Record<string, Record<string, string>> = {
  no: {
    done: 'Quiz fullført!', score: 'Din poengsum', correct: 'Riktige', of: 'av',
    ready: 'Du er klar for prøven!', good: 'Bra jobbet!', keep: 'Fortsett å øve – du blir bedre!',
    retry: 'Prøv igjen', home: 'Hjem', practice: 'Øving', exam: 'Eksamen',
    passed: 'BESTÅTT', failed: 'IKKE BESTÅTT', threshold: '85% kreves',
    upgrade: 'Oppgrader til Premium', unlockAll: 'Lås opp alle spørsmål',
    review: 'Gjennomgå feil svar', reviewAll: 'Vis alle spørsmål', reviewWrong: 'Vis bare feil',
    reviewTitle: 'Gjennomgang', noMistakes: 'Ingen feil – perfekt!',
    yourAnswer: 'Ditt svar', correctAnswer: 'Riktig svar', explanation: 'Forklaring',
    notAnswered: 'Ikke besvart',
  },
  th: {
    done: 'ทำแบบทดสอบเสร็จ!', score: 'คะแนน', correct: 'ถูก', of: 'จาก',
    ready: 'คุณพร้อมสอบแล้ว!', good: 'ทำได้ดี!', keep: 'ฝึกซ้อมต่อ – คุณเก่งขึ้นเรื่อยๆ!',
    retry: 'ลองอีกครั้ง', home: 'หน้าหลัก', practice: 'ฝึกซ้อม', exam: 'สอบ',
    passed: 'ผ่าน', failed: 'ไม่ผ่าน', threshold: 'ต้องได้ 85%',
    upgrade: 'อัพเกรดเป็น Premium', unlockAll: 'ปลดล็อคคำถามทั้งหมด',
    review: 'ดูข้อที่ผิด', reviewAll: 'ดูทั้งหมด', reviewWrong: 'เฉพาะข้อผิด',
    reviewTitle: 'ทบทวน', noMistakes: 'ไม่มีข้อผิด – ยอดเยี่ยม!',
    yourAnswer: 'คำตอบของคุณ', correctAnswer: 'คำตอบที่ถูก', explanation: 'คำอธิบาย',
    notAnswered: 'ยังไม่ได้ตอบ',
  },
  en: {
    done: 'Quiz Complete!', score: 'Your Score', correct: 'Correct', of: 'out of',
    ready: "You're ready for the test!", good: 'Good job!', keep: "Keep practicing – you're improving!",
    retry: 'Try Again', home: 'Home', practice: 'Practice', exam: 'Exam',
    passed: 'PASSED', failed: 'FAILED', threshold: '85% required',
    upgrade: 'Upgrade to Premium', unlockAll: 'Unlock all questions',
    review: 'Review mistakes', reviewAll: 'Show all', reviewWrong: 'Wrong only',
    reviewTitle: 'Review', noMistakes: 'No mistakes – perfect!',
    yourAnswer: 'Your answer', correctAnswer: 'Correct answer', explanation: 'Explanation',
    notAnswered: 'Not answered',
  },
};

export default function ResultsScreen() {
  const router = useRouter();
  const { total, correct, mode, passed } = useLocalSearchParams<{ total: string; correct: string; mode: string; passed: string }>();
  const { language, isPremium, lastAttempt } = useAppStore();
  const t = TR[language] || TR.en;
  const c = useAppStore((s) => s.colors);

  const [showReview, setShowReview] = useState(false);
  const [filterWrong, setFilterWrong] = useState(true);

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
  const hasAttempt = !!(lastAttempt && lastAttempt.questions.length > 0);
  const wrongCount = lastAttempt?.answers.filter((a) => !a.correct).length || 0;

  // V2 helpers
  const qT = (qu: any, l?: string) => qu?.question?.[l || language] || qu?.question?.no || '';
  const optText = (qu: any, optId: string, l?: string) => {
    const opt = qu?.options?.find((o: any) => o.id === optId);
    return opt?.text?.[l || language] || opt?.text?.no || '';
  };
  const eT = (qu: any, l?: string) => qu?.explanation?.[l || language] || qu?.explanation?.no || '';

  const reviewItems = hasAttempt
    ? lastAttempt!.questions.map((q, i) => {
        const a = lastAttempt!.answers[i];
        return { q, selected: a?.selected || null, correct: a?.correct || false };
      })
    : [];
  const visibleItems = filterWrong ? reviewItems.filter((x) => !x.correct) : reviewItems;

  if (showReview) {
    return (
      <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
        {/* Review Header */}
        <View style={[st.revHeader, { borderBottomColor: c.divider }]}>
          <TouchableOpacity style={[st.backBtn, { backgroundColor: c.card }]} onPress={() => setShowReview(false)}>
            <Ionicons name="arrow-back" size={22} color={c.text} />
          </TouchableOpacity>
          <Text style={[st.revTitle, { color: c.text }]}>{t.reviewTitle}</Text>
          <View style={{ width: 40 }} />
        </View>

        {/* Filter toggle */}
        {wrongCount > 0 && wrongCount < reviewItems.length && (
          <View style={st.filterRow}>
            <TouchableOpacity
              style={[st.filterChip, { backgroundColor: filterWrong ? c.accentBg : c.card, borderColor: filterWrong ? c.accent : c.cardBorder }]}
              onPress={() => setFilterWrong(true)}
            >
              <Text style={[st.filterText, { color: filterWrong ? c.accent : c.textSecondary }]}>
                {t.reviewWrong} ({wrongCount})
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[st.filterChip, { backgroundColor: !filterWrong ? c.accentBg : c.card, borderColor: !filterWrong ? c.accent : c.cardBorder }]}
              onPress={() => setFilterWrong(false)}
            >
              <Text style={[st.filterText, { color: !filterWrong ? c.accent : c.textSecondary }]}>
                {t.reviewAll} ({reviewItems.length})
              </Text>
            </TouchableOpacity>
          </View>
        )}

        <ScrollView contentContainerStyle={st.revScroll} showsVerticalScrollIndicator={false}>
          {visibleItems.length === 0 ? (
            <View style={st.emptyReview}>
              <Text style={st.emptyEmoji}>🎉</Text>
              <Text style={[st.emptyText, { color: c.textSecondary }]}>{t.noMistakes}</Text>
            </View>
          ) : (
            visibleItems.map((item, idx) => {
              const { q, selected, correct: wasCorrect } = item;
              const correctId = q.correctOptionId;
              return (
                <View key={q.id || idx} style={[st.revCard, { backgroundColor: c.card, borderColor: wasCorrect ? `${c.correct}40` : `${c.incorrect}40` }]}>
                  {/* Number + status */}
                  <View style={st.revCardHead}>
                    <View style={[st.revNum, { backgroundColor: wasCorrect ? c.correct : c.incorrect }]}>
                      <Ionicons name={wasCorrect ? 'checkmark' : 'close'} size={14} color="#0F172A" />
                    </View>
                    <Text style={[st.revNumText, { color: c.textMuted }]}>
                      {reviewItems.indexOf(item) + 1} / {reviewItems.length}
                    </Text>
                  </View>

                  {/* Question */}
                  <Text style={[st.revQ, { color: c.text }]}>{qT(q)}</Text>
                  {language !== 'th' && (
                    <Text style={[st.revQTh, { color: `${c.accent}B0` }]}>{qT(q, 'th')}</Text>
                  )}

                  {/* Your answer */}
                  {selected ? (
                    <View style={[st.revAnsBox, { backgroundColor: wasCorrect ? `${c.correct}15` : `${c.incorrect}15`, borderColor: wasCorrect ? c.correct : c.incorrect }]}>
                      <Text style={[st.revAnsLabel, { color: wasCorrect ? c.correct : c.incorrect }]}>{t.yourAnswer}</Text>
                      <Text style={[st.revAnsText, { color: c.text }]}>
                        {selected}. {optText(q, selected)}
                      </Text>
                    </View>
                  ) : (
                    <View style={[st.revAnsBox, { backgroundColor: `${c.incorrect}15`, borderColor: c.incorrect }]}>
                      <Text style={[st.revAnsLabel, { color: c.incorrect }]}>{t.notAnswered}</Text>
                    </View>
                  )}

                  {/* Correct answer (only if user was wrong) */}
                  {!wasCorrect && (
                    <View style={[st.revAnsBox, { backgroundColor: `${c.correct}15`, borderColor: c.correct }]}>
                      <Text style={[st.revAnsLabel, { color: c.correct }]}>{t.correctAnswer}</Text>
                      <Text style={[st.revAnsText, { color: c.text }]}>
                        {correctId}. {optText(q, correctId)}
                      </Text>
                    </View>
                  )}

                  {/* Explanation */}
                  <View style={[st.revExplBox, { borderTopColor: c.divider }]}>
                    <Text style={[st.revExplLabel, { color: c.textMuted }]}>{t.explanation}</Text>
                    <Text style={[st.revExpl, { color: c.textSecondary }]}>{eT(q)}</Text>
                    {language !== 'th' && (
                      <Text style={[st.revExplTh, { color: `${c.accent}90` }]}>{eT(q, 'th')}</Text>
                    )}
                  </View>
                </View>
              );
            })
          )}
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <ScrollView contentContainerStyle={st.scrollContent} showsVerticalScrollIndicator={false}>
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

          {/* Review button — only show if we have attempt data */}
          {hasAttempt && (
            <TouchableOpacity
              testID="result-review-btn"
              style={[st.reviewBtn, { backgroundColor: c.card, borderColor: wrongCount > 0 ? c.incorrect : c.correct }]}
              onPress={() => setShowReview(true)}
              activeOpacity={0.8}
            >
              <Ionicons
                name={wrongCount > 0 ? 'list-outline' : 'checkmark-done-outline'}
                size={20}
                color={wrongCount > 0 ? c.incorrect : c.correct}
              />
              <Text style={[st.reviewBtnText, { color: wrongCount > 0 ? c.incorrect : c.correct }]}>
                {wrongCount > 0 ? `${t.review} (${wrongCount})` : t.reviewAll}
              </Text>
              <Ionicons name="chevron-forward" size={18} color={c.textMuted} />
            </TouchableOpacity>
          )}
        </View>
      </ScrollView>

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
  scrollContent: { flexGrow: 1, justifyContent: 'center' },
  content: { justifyContent: 'center', alignItems: 'center', padding: 20 },
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
  badge: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingVertical: 7, borderRadius: 16, gap: 6, marginBottom: 16 },
  badgeT: { fontSize: 13, fontWeight: '600' },
  reviewBtn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    borderRadius: 14, paddingVertical: 14, paddingHorizontal: 16, gap: 8,
    borderWidth: 1.5, width: '100%',
  },
  reviewBtnText: { fontSize: 15, fontWeight: '700', flex: 1, textAlign: 'center' },
  actions: { padding: 20 },
  upgradeBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 13, gap: 8, borderWidth: 1.5, marginBottom: 10 },
  upgradeT: { fontSize: 15, fontWeight: '700' },
  btnRow: { flexDirection: 'row', gap: 10 },
  secBtn: { flex: 1, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 14, gap: 6, borderWidth: 1 },
  secT: { fontSize: 14, fontWeight: '600' },
  priBtn: { flex: 1, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 14, gap: 6 },
  priT: { fontSize: 14, fontWeight: '700', color: '#0F172A' },

  // Review screen
  revHeader: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1 },
  backBtn: { width: 40, height: 40, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  revTitle: { flex: 1, fontSize: 18, fontWeight: '800', textAlign: 'center' },
  filterRow: { flexDirection: 'row', padding: 14, gap: 8 },
  filterChip: { flex: 1, borderRadius: 12, paddingVertical: 10, alignItems: 'center', borderWidth: 1 },
  filterText: { fontSize: 13, fontWeight: '700' },
  revScroll: { padding: 14, paddingBottom: 30 },
  emptyReview: { paddingVertical: 60, alignItems: 'center' },
  emptyEmoji: { fontSize: 48, marginBottom: 12 },
  emptyText: { fontSize: 16, fontWeight: '600' },
  revCard: { borderRadius: 14, padding: 16, marginBottom: 12, borderWidth: 1 },
  revCardHead: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 10 },
  revNum: { width: 24, height: 24, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  revNumText: { fontSize: 12, fontWeight: '600' },
  revQ: { fontSize: 15, fontWeight: '700', lineHeight: 22, marginBottom: 4 },
  revQTh: { fontSize: 13, lineHeight: 20, marginBottom: 12 },
  revAnsBox: { borderRadius: 10, padding: 10, marginBottom: 8, borderWidth: 1 },
  revAnsLabel: { fontSize: 10, fontWeight: '800', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 },
  revAnsText: { fontSize: 14, fontWeight: '500', lineHeight: 19 },
  revExplBox: { marginTop: 6, paddingTop: 10, borderTopWidth: 1 },
  revExplLabel: { fontSize: 10, fontWeight: '800', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 },
  revExpl: { fontSize: 13, lineHeight: 19 },
  revExplTh: { fontSize: 12, lineHeight: 18, marginTop: 4 },
});
