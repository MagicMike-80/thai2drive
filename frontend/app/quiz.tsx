import React, { useEffect, useState, useRef, useCallback } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Animated } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as Speech from 'expo-speech';
import { useAppStore } from '../src/store/appStore';
import { api, Question } from '../src/services/api';
import { playCorrectSound, playIncorrectSound, cleanupSounds } from '../src/sounds';

const ANSWER_LETTERS = ['A', 'B', 'C', 'D'];
const EXAM_TIME_SECONDS = 90 * 60;
const EXAM_PASS_THRESHOLD = 85;

const T: Record<string, Record<string, string>> = {
  no: { checkAnswer: 'Sjekk svar', next: 'Neste', finish: 'Fullfør', correct: 'Riktig!', incorrect: 'Feil!', tapTranslate: 'Trykk for Thai' },
  th: { checkAnswer: 'ตรวจคำตอบ', next: 'ถัดไป', finish: 'เสร็จสิ้น', correct: 'ถูกต้อง!', incorrect: 'ผิด!', tapTranslate: 'แตะเพื่อแปล' },
  en: { checkAnswer: 'Check Answer', next: 'Next', finish: 'Finish', correct: 'Correct!', incorrect: 'Incorrect!', tapTranslate: 'Tap for Thai' },
};

export default function QuizScreen() {
  const router = useRouter();
  const { mode, category } = useLocalSearchParams<{ mode: string; category: string }>();
  const { language, deviceId, addBookmark, removeBookmark, isBookmarked, setProgress, colors, soundEnabled } = useAppStore();
  const t = T[language] || T.no;
  const c = colors;

  const [questions, setQuestions] = useState<Question[]>([]);
  const [idx, setIdx] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [answered, setAnswered] = useState(false);
  const [loading, setLoading] = useState(true);
  const [startTime] = useState(new Date());
  const [history, setHistory] = useState<any[]>([]);
  const [showThai, setShowThai] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [timer, setTimer] = useState(EXAM_TIME_SECONDS);

  const fade = useRef(new Animated.Value(1)).current;
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isExam = mode === 'exam';

  useEffect(() => {
    loadQuestions();
    return () => { if (timerRef.current) clearInterval(timerRef.current); Speech.stop(); cleanupSounds(); };
  }, []);

  useEffect(() => {
    if (isExam && !loading && questions.length > 0) {
      timerRef.current = setInterval(() => {
        setTimer((p) => { if (p <= 1) { if (timerRef.current) clearInterval(timerRef.current); handleTimeUp(); return 0; } return p - 1; });
      }, 1000);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [loading, questions.length]);

  const loadQuestions = async () => {
    try {
      const qs = await api.getRandomQuestions(isExam ? 45 : 10, category === 'all' ? undefined : category);
      setQuestions(qs);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleTimeUp = useCallback(() => {
    const correct = history.filter((a) => a.correct).length;
    goResults(correct, questions.length > 0 ? (correct / questions.length) * 100 : 0);
  }, [history, questions.length]);

  const q = questions[idx];

  const qText = (qu: Question, l?: string) => (qu as any)[`question_text_${l || language}`] || qu.question_text_no;
  const aText = (qu: Question, letter: string, l?: string) => (qu as any)[`answer_${letter.toLowerCase()}_${l || language}`] || (qu as any)[`answer_${letter.toLowerCase()}_no`];
  const eText = (qu: Question, l?: string) => (qu as any)[`explanation_${l || language}`] || qu.explanation_no;

  const handleCheck = async () => {
    if (!selected || !q) return;
    setAnswered(true);
    const correct = selected === q.correct_answer;

    // Play sound
    if (soundEnabled) {
      if (correct) playCorrectSound(); else playIncorrectSound();
    }

    setHistory((p) => [...p, { question_id: q.id, selected_answer: selected, correct }]);
    try {
      await api.updateProgress(deviceId, correct, q.category);
      setProgress(await api.getProgress(deviceId));
    } catch (e) {}
  };

  const handleNext = () => {
    if (idx >= questions.length - 1) { finishQuiz(); return; }
    Animated.sequence([
      Animated.timing(fade, { toValue: 0, duration: 100, useNativeDriver: true }),
      Animated.timing(fade, { toValue: 1, duration: 100, useNativeDriver: true }),
    ]).start();
    setTimeout(() => { setIdx((p) => p + 1); setSelected(null); setAnswered(false); setShowThai(false); }, 100);
  };

  const finishQuiz = async () => {
    if (timerRef.current) clearInterval(timerRef.current);
    const correct = history.filter((a) => a.correct).length;
    const pct = (correct / questions.length) * 100;
    try {
      await api.saveQuizAttempt({
        device_id: deviceId, mode: mode || 'practice', category: category === 'all' ? undefined : category,
        total_questions: questions.length, correct_answers: correct, score_percentage: pct,
        passed: isExam ? pct >= EXAM_PASS_THRESHOLD : undefined, questions_answered: history, started_at: startTime.toISOString(),
      });
    } catch (e) {}
    goResults(correct, pct);
  };

  const goResults = (correct: number, pct: number) => {
    router.replace({ pathname: '/results', params: { total: questions.length.toString(), correct: correct.toString(), mode: mode || 'practice', passed: isExam ? (pct >= EXAM_PASS_THRESHOLD ? 'true' : 'false') : '' } });
  };

  const handleBookmark = async () => { if (!q) return; isBookmarked(q.id) ? await removeBookmark(q.id) : await addBookmark(q.id); };

  const speakThai = () => {
    if (!q) return;
    if (speaking) { Speech.stop(); setSpeaking(false); return; }
    setSpeaking(true);
    Speech.speak(qText(q, 'th'), { language: 'th-TH', rate: 0.85, onDone: () => setSpeaking(false), onError: () => setSpeaking(false) });
  };

  const fmtTime = (s: number) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  if (loading || !q) return (
    <SafeAreaView style={[s.container, { backgroundColor: c.bg }]}>
      <View style={s.center}>{loading ? <ActivityIndicator testID="quiz-loading" size="large" color={c.accent} /> : <Text style={{ color: c.incorrect }}>No questions</Text>}</View>
    </SafeAreaView>
  );

  const bookmarked = isBookmarked(q.id);
  const timerWarn = isExam && timer < 300;

  return (
    <SafeAreaView style={[s.container, { backgroundColor: c.bg }]}>
      {/* Header */}
      <View style={[s.header]}>
        <TouchableOpacity testID="quiz-exit-btn" style={[s.iconBtn, { backgroundColor: c.card }]} onPress={() => router.back()}>
          <Ionicons name="close" size={20} color={c.text} />
        </TouchableOpacity>
        <View style={s.progWrap}>
          <Text style={[s.progText, { color: c.textSecondary }]}>{idx + 1} / {questions.length}</Text>
          <View style={[s.progBar, { backgroundColor: c.progressBg }]}>
            <View style={[s.progFill, { width: `${((idx + 1) / questions.length) * 100}%`, backgroundColor: c.accent }]} />
          </View>
        </View>
        <TouchableOpacity testID="quiz-bookmark-btn" style={[s.iconBtn, { backgroundColor: c.card }]} onPress={handleBookmark}>
          <Ionicons name={bookmarked ? 'bookmark' : 'bookmark-outline'} size={20} color={bookmarked ? c.accent : c.text} />
        </TouchableOpacity>
      </View>

      {/* Timer */}
      {isExam && (
        <View style={[s.timerBar, { backgroundColor: timerWarn ? c.incorrectBg : c.accentBg }]}>
          <Ionicons name="timer-outline" size={15} color={timerWarn ? c.incorrect : c.accent} />
          <Text style={[s.timerText, { color: timerWarn ? c.incorrect : c.accent }]}>{fmtTime(timer)}</Text>
        </View>
      )}

      <ScrollView contentContainerStyle={s.scroll} showsVerticalScrollIndicator={false}>
        <Animated.View style={{ opacity: fade }}>
          {/* Question */}
          <TouchableOpacity testID="question-card" style={[s.qCard, { backgroundColor: c.card, borderColor: c.cardBorder }]} onPress={() => setShowThai(!showThai)} activeOpacity={0.9}>
            <Text style={[s.qText, { color: c.text }]}>{qText(q)}</Text>
            {!showThai && language !== 'th' && (
              <View style={s.hintRow}><Ionicons name="language-outline" size={13} color={c.accent} /><Text style={[s.hintText, { color: c.accent }]}>{t.tapTranslate}</Text></View>
            )}
            {showThai && language !== 'th' && (
              <View style={s.thaiWrap}>
                <View style={[s.thaiLine, { backgroundColor: `${c.accent}30` }]} />
                <Text style={[s.thaiText, { color: c.accent }]}>{qText(q, 'th')}</Text>
                <TouchableOpacity testID="tts-btn" style={[s.ttsBtn, { backgroundColor: c.accentBg }]} onPress={speakThai}>
                  <Ionicons name={speaking ? 'volume-high' : 'volume-medium-outline'} size={16} color={c.accent} />
                  <Text style={{ fontSize: 13 }}>🇹🇭</Text>
                </TouchableOpacity>
              </View>
            )}
          </TouchableOpacity>

          {/* Answers */}
          <View style={s.ansWrap}>
            {ANSWER_LETTERS.map((L) => {
              const isSel = selected === L;
              const isCor = q.correct_answer === L;
              let bg = c.answerBg, border = c.answerBorder, txtCol = c.text, letBg = c.letterBg, dim = false;

              if (answered) {
                if (isCor) { bg = c.correctBg; border = c.correct; txtCol = c.correct; letBg = c.correct; }
                else if (isSel) { bg = c.incorrectBg; border = c.incorrect; txtCol = c.incorrect; letBg = c.incorrect; }
                else { dim = true; }
              } else if (isSel) { bg = c.accentBg; border = c.accent; letBg = c.accent; }

              return (
                <TouchableOpacity key={L} testID={`answer-btn-${L}`} style={[s.ansBtn, { backgroundColor: bg, borderColor: border }, dim && s.dim]} onPress={() => !answered && setSelected(L)} disabled={answered} activeOpacity={0.7}>
                  <View style={[s.letCircle, { backgroundColor: letBg }]}><Text style={s.letText}>{L}</Text></View>
                  <Text style={[s.ansText, { color: txtCol }]}>{aText(q, L)}</Text>
                  {answered && isCor && <Ionicons name="checkmark-circle" size={20} color={c.correct} />}
                  {answered && isSel && !isCor && <Ionicons name="close-circle" size={20} color={c.incorrect} />}
                </TouchableOpacity>
              );
            })}
          </View>

          {/* Inline feedback — no card, no box */}
          {answered && (
            <View style={s.feedback}>
              <View style={s.fbRow}>
                <Ionicons name={selected === q.correct_answer ? 'checkmark-circle' : 'close-circle'} size={16} color={selected === q.correct_answer ? c.correct : c.incorrect} />
                <Text style={[s.fbStatus, { color: selected === q.correct_answer ? c.correct : c.incorrect }]}>
                  {selected === q.correct_answer ? t.correct : t.incorrect}
                </Text>
              </View>
              <Text style={[s.fbExpl, { color: c.textSecondary }]}>{eText(q)}</Text>
              {language !== 'th' && <Text style={[s.fbThai, { color: `${c.accent}B0` }]}>{eText(q, 'th')}</Text>}
            </View>
          )}
        </Animated.View>
      </ScrollView>

      {/* Action */}
      <View style={s.actWrap}>
        {!answered ? (
          <TouchableOpacity testID="check-answer-btn" style={[s.actBtn, { backgroundColor: selected ? c.accent : c.letterBg }]} onPress={handleCheck} disabled={!selected}>
            <Text style={[s.actText, { color: selected ? '#0F172A' : c.textMuted }]}>{t.checkAnswer}</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity testID="next-btn" style={[s.actBtn, { backgroundColor: c.accent }]} onPress={handleNext}>
            <Text style={[s.actText, { color: '#0F172A' }]}>{idx >= questions.length - 1 ? t.finish : t.next}</Text>
            <Ionicons name="arrow-forward" size={18} color="#0F172A" />
          </TouchableOpacity>
        )}
      </View>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingVertical: 10, gap: 10 },
  iconBtn: { width: 38, height: 38, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  progWrap: { flex: 1 },
  progText: { fontSize: 12, fontWeight: '600', textAlign: 'center', marginBottom: 5 },
  progBar: { height: 5, borderRadius: 3 },
  progFill: { height: '100%', borderRadius: 3 },
  timerBar: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 6, gap: 5 },
  timerText: { fontSize: 15, fontWeight: '700', fontVariant: ['tabular-nums'] },
  scroll: { paddingHorizontal: 14, paddingTop: 6, paddingBottom: 10 },
  qCard: { borderRadius: 14, padding: 18, marginBottom: 14, borderWidth: 1 },
  qText: { fontSize: 18, fontWeight: '700', lineHeight: 26 },
  hintRow: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 10, opacity: 0.6 },
  hintText: { fontSize: 11 },
  thaiWrap: { marginTop: 10 },
  thaiLine: { height: 1, marginBottom: 10 },
  thaiText: { fontSize: 15, lineHeight: 22 },
  ttsBtn: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 8, alignSelf: 'flex-start', paddingHorizontal: 10, paddingVertical: 5, borderRadius: 16 },
  ansWrap: { gap: 12 },
  ansBtn: { flexDirection: 'row', alignItems: 'center', borderRadius: 12, paddingVertical: 13, paddingHorizontal: 14, borderWidth: 1.5 },
  dim: { opacity: 0.35 },
  letCircle: { width: 32, height: 32, borderRadius: 10, justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  letText: { fontSize: 14, fontWeight: '700', color: '#F8FAFC' },
  ansText: { flex: 1, fontSize: 15, lineHeight: 21 },
  feedback: { marginTop: 16, paddingHorizontal: 2 },
  fbRow: { flexDirection: 'row', alignItems: 'center', gap: 5, marginBottom: 4 },
  fbStatus: { fontSize: 13, fontWeight: '700' },
  fbExpl: { fontSize: 13, lineHeight: 19, opacity: 0.8 },
  fbThai: { fontSize: 12, lineHeight: 18, marginTop: 3 },
  actWrap: { paddingHorizontal: 14, paddingTop: 10, paddingBottom: 14 },
  actBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 14, gap: 6 },
  actText: { fontSize: 15, fontWeight: '700' },
});
