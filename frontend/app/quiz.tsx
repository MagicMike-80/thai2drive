import React, { useEffect, useState, useRef, useCallback } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Animated, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as Speech from 'expo-speech';
import { useAppStore } from '../src/store/appStore';
import { api, Question } from '../src/services/api';
import { playCorrectSound, playIncorrectSound, cleanupSounds } from '../src/sounds';
import { useScreenProtection } from '../src/hooks/useScreenProtection';

const LETTERS = ['A', 'B', 'C', 'D'];
const EXAM_TIME = 90 * 60;
const PASS = 85;

const T: Record<string, Record<string, string>> = {
  no: { check: 'Sjekk svar', next: 'Neste', finish: 'Fullfør', correct: 'Riktig!', incorrect: 'Feil!', hint: 'Trykk for Thai', limitMsg: 'Gratis grense nådd', unlock: 'Lås opp Premium', listen: 'Lytt', listening: 'Spiller...', listenExpl: 'Lytt' },
  th: { check: 'ตรวจคำตอบ', next: 'ถัดไป', finish: 'เสร็จสิ้น', correct: 'ถูกต้อง!', incorrect: 'ผิด!', hint: 'แตะเพื่อแปล', limitMsg: 'ถึงขีดจำกัดฟรี', unlock: 'ปลดล็อค Premium', listen: 'ฟัง', listening: 'กำลังเล่น...', listenExpl: 'ฟัง' },
  en: { check: 'Check Answer', next: 'Next', finish: 'Finish', correct: 'Correct!', incorrect: 'Incorrect!', hint: 'Tap for Thai', limitMsg: 'Free limit reached', unlock: 'Unlock Premium', listen: 'Listen', listening: 'Playing...', listenExpl: 'Listen' },
};

export default function QuizScreen() {
  const router = useRouter();
  const { mode, category } = useLocalSearchParams<{ mode: string; category: string }>();
  const store = useAppStore();
  const { language, deviceId, addBookmark, removeBookmark, isBookmarked, setProgress, colors: c, soundEnabled, isPremium, incrementFreeQuestions, canAnswerFree, updateStreak } = store;
  const t = T[language] || T.no;

  // Screen capture protection
  useScreenProtection(language);

  const [questions, setQuestions] = useState<Question[]>([]);
  const [idx, setIdx] = useState(0);
  const [sel, setSel] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(true);
  const [startTime] = useState(new Date());
  const [hist, setHist] = useState<any[]>([]);
  const [showTh, setShowTh] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [timer, setTimer] = useState(EXAM_TIME);
  const [showLimit, setShowLimit] = useState(false);
  const [ttsPlaying, setTtsPlaying] = useState<'question' | 'explanation' | null>(null);

  const fade = useRef(new Animated.Value(1)).current;
  const glowAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isExam = mode === 'exam';

  useEffect(() => { loadQ(); return () => { if (timerRef.current) clearInterval(timerRef.current); Speech.stop(); cleanupSounds(); }; }, []);

  // Stop TTS when question changes
  useEffect(() => { stopTts(); }, [idx]);

  useEffect(() => {
    if (isExam && !loading && questions.length > 0) {
      timerRef.current = setInterval(() => {
        setTimer((p) => { if (p <= 1) { if (timerRef.current) clearInterval(timerRef.current); timeUp(); return 0; } return p - 1; });
      }, 1000);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [loading, questions.length]);

  const loadQ = async () => {
    try { setQuestions(await api.getRandomQuestions(isExam ? 45 : 10, category === 'all' ? undefined : category)); } catch (e) {}
    finally { setLoading(false); }
  };

  const timeUp = useCallback(() => {
    const cor = hist.filter((a) => a.correct).length;
    goRes(cor, questions.length > 0 ? (cor / questions.length) * 100 : 0);
  }, [hist, questions.length]);

  const q = questions[idx];
  const qT = (qu: Question, l?: string) => (qu as any)[`question_text_${l || language}`] || qu.question_text_no;
  const aT = (qu: Question, L: string, l?: string) => (qu as any)[`answer_${L.toLowerCase()}_${l || language}`] || (qu as any)[`answer_${L.toLowerCase()}_no`];
  const eT = (qu: Question, l?: string) => (qu as any)[`explanation_${l || language}`] || qu.explanation_no;

  const handleCheck = async () => {
    if (!sel || !q) return;
    setDone(true);
    const cor = sel === q.correct_answer;

    // Animate: subtle scale press on correct
    if (cor) {
      Animated.sequence([
        Animated.timing(scaleAnim, { toValue: 0.98, duration: 75, useNativeDriver: true }),
        Animated.timing(scaleAnim, { toValue: 1.0, duration: 150, useNativeDriver: true }),
      ]).start();
    }
    // Glow pulse
    Animated.sequence([
      Animated.timing(glowAnim, { toValue: 1, duration: 200, useNativeDriver: false }),
      Animated.timing(glowAnim, { toValue: 0, duration: 600, useNativeDriver: false }),
    ]).start();

    if (soundEnabled) { cor ? playCorrectSound() : playIncorrectSound(); }

    setHist((p) => [...p, { question_id: q.id, selected_answer: sel, correct: cor }]);
    if (!isPremium) incrementFreeQuestions();
    await updateStreak();
    try { await api.updateProgress(deviceId, cor, q.category); setProgress(await api.getProgress(deviceId)); } catch (e) {}
  };

  const handleNext = () => {
    if (idx >= questions.length - 1) { finishQ(); return; }
    if (!canAnswerFree()) { setShowLimit(true); return; }
    // Smooth slide transition
    Animated.timing(fade, { toValue: 0, duration: 120, useNativeDriver: true }).start(() => {
      setIdx((p) => p + 1); setSel(null); setDone(false); setShowTh(false); setShowLimit(false);
      Animated.timing(fade, { toValue: 1, duration: 120, useNativeDriver: true }).start();
    });
  };

  const finishQ = async () => {
    if (timerRef.current) clearInterval(timerRef.current);
    const cor = hist.filter((a) => a.correct).length;
    const pct = (cor / questions.length) * 100;
    try { await api.saveQuizAttempt({ device_id: deviceId, mode: mode || 'practice', category: category === 'all' ? undefined : category, total_questions: questions.length, correct_answers: cor, score_percentage: pct, passed: isExam ? pct >= PASS : undefined, questions_answered: hist, started_at: startTime.toISOString() }); } catch (e) {}
    goRes(cor, pct);
  };

  const goRes = (cor: number, pct: number) => {
    router.replace({ pathname: '/results', params: { total: questions.length.toString(), correct: cor.toString(), mode: mode || 'practice', passed: isExam ? (pct >= PASS ? 'true' : 'false') : '' } });
  };

  const stopTts = () => { Speech.stop(); setTtsPlaying(null); setSpeaking(false); };

  const langCode = (l: string) => l === 'th' ? 'th-TH' : l === 'no' ? 'nb-NO' : 'en-US';

  const speakSequence = async (segments: { text: string; lang: string }[]) => {
    for (let i = 0; i < segments.length; i++) {
      const s = segments[i];
      await new Promise<void>((resolve) => {
        Speech.speak(s.text, {
          language: langCode(s.lang),
          rate: s.lang === 'th' ? 0.85 : 0.9,
          onDone: resolve,
          onError: resolve,
          onStopped: resolve,
        });
      });
    }
  };

  const speakQuestion = async () => {
    if (!q) return;
    if (ttsPlaying === 'question') { stopTts(); return; }
    stopTts();
    setTtsPlaying('question');
    setSpeaking(true);

    const segments: { text: string; lang: string }[] = [];
    // Always read question in current language first
    segments.push({ text: qT(q), lang: language });
    // Always read Thai translation (core feature for Thai users)
    if (language !== 'th') segments.push({ text: qT(q, 'th'), lang: 'th' });
    // Answer options in current language
    for (const L of LETTERS) {
      segments.push({ text: `${L}. ${aT(q, L)}`, lang: language });
    }
    // Answer options in Thai
    if (language !== 'th') {
      for (const L of LETTERS) {
        segments.push({ text: `${L}. ${aT(q, L, 'th')}`, lang: 'th' });
      }
    }

    await speakSequence(segments);
    setTtsPlaying(null);
    setSpeaking(false);
  };

  const speakExplanation = async () => {
    if (!q) return;
    if (ttsPlaying === 'explanation') { stopTts(); return; }
    stopTts();
    setTtsPlaying('explanation');
    setSpeaking(true);

    const segments: { text: string; lang: string }[] = [];
    // Read explanation in current language
    segments.push({ text: eT(q), lang: language });
    // Always read Thai explanation
    if (language !== 'th') segments.push({ text: eT(q, 'th'), lang: 'th' });

    await speakSequence(segments);
    setTtsPlaying(null);
    setSpeaking(false);
  };

  const fmtT = (s: number) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  if (loading || !q) return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <View style={st.center}>{loading ? <ActivityIndicator testID="quiz-loading" size="large" color={c.accent} /> : <Text style={{ color: c.incorrect }}>No questions</Text>}</View>
    </SafeAreaView>
  );

  const bm = isBookmarked(q.id);
  const tw = isExam && timer < 300;

  // Glow interpolation for selected answer
  const glowOpacity = glowAnim.interpolate({ inputRange: [0, 1], outputRange: [0, 0.3] });

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      {/* Header */}
      <View style={st.hdr}>
        <TouchableOpacity testID="quiz-exit-btn" style={[st.iBtn, { backgroundColor: c.card }]} onPress={() => router.back()}>
          <Ionicons name="close" size={20} color={c.text} />
        </TouchableOpacity>
        <View style={st.pWrap}>
          <Text style={[st.pTxt, { color: c.textSecondary }]}>{idx + 1} / {questions.length}</Text>
          <View style={[st.pBar, { backgroundColor: c.progressBg }]}>
            <View style={[st.pFill, { width: `${((idx + 1) / questions.length) * 100}%`, backgroundColor: c.accent }]} />
          </View>
        </View>
        <TouchableOpacity testID="quiz-bookmark-btn" style={[st.iBtn, { backgroundColor: c.card }]} onPress={() => { if (q) bm ? removeBookmark(q.id) : addBookmark(q.id); }}>
          <Ionicons name={bm ? 'bookmark' : 'bookmark-outline'} size={20} color={bm ? c.accent : c.text} />
        </TouchableOpacity>
      </View>

      {isExam && (
        <View style={[st.tmr, { backgroundColor: tw ? c.incorrectBg : c.accentBg }]}>
          <Ionicons name="timer-outline" size={15} color={tw ? c.incorrect : c.accent} />
          <Text style={[st.tmrTxt, { color: tw ? c.incorrect : c.accent }]}>{fmtT(timer)}</Text>
        </View>
      )}

      <ScrollView contentContainerStyle={st.scr} showsVerticalScrollIndicator={false}>
        <Animated.View style={{ opacity: fade, transform: [{ scale: scaleAnim }] }}>
          {/* Question */}
          <View style={[st.qCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            {q.image_url ? (
              <Image
                testID="question-image"
                source={{ uri: q.image_url }}
                style={[st.qImg, { borderColor: c.cardBorder }]}
                resizeMode="contain"
              />
            ) : null}
            <TouchableOpacity testID="question-card" onPress={() => setShowTh(!showTh)} activeOpacity={0.9}>
              <Text style={[st.qTxt, { color: c.text }]}>{qT(q)}</Text>
            </TouchableOpacity>
            {language !== 'th' && (
              <TouchableOpacity onPress={() => setShowTh(!showTh)} style={st.translateRow}>
                <Ionicons name="language-outline" size={13} color={c.accent} />
                <Text style={[st.hintT, { color: c.accent }]}>{t.hint}</Text>
              </TouchableOpacity>
            )}
            {showTh && language !== 'th' && (
              <View style={st.thW}>
                <View style={[st.thL, { backgroundColor: `${c.accent}30` }]} />
                <Text style={[st.thTxt, { color: c.accent }]}>{qT(q, 'th')}</Text>
              </View>
            )}
          </View>

          {/* TTS Listen Button — subtle, highlights on tap */}
          <TouchableOpacity
            testID="tts-question-btn"
            onPress={speakQuestion}
            activeOpacity={1}
            style={[st.listenBtn, { backgroundColor: ttsPlaying === 'question' ? c.accentBg : c.card, borderColor: ttsPlaying === 'question' ? c.accent : c.cardBorder, opacity: ttsPlaying === 'question' ? 1 : 0.55 }]}
          >
            <Text style={st.listenIcon}>{ttsPlaying === 'question' ? '🔊' : '🔈'}</Text>
            <Text style={[st.listenText, { color: ttsPlaying === 'question' ? c.accent : c.textSecondary }]}>
              {ttsPlaying === 'question' ? t.listening : t.listen}
            </Text>
          </TouchableOpacity>

          {/* Answers with glow */}
          <View style={st.aW}>
            {LETTERS.map((L) => {
              const isSel = sel === L, isCor = q.correct_answer === L;
              let bg = c.answerBg, border = c.answerBorder, txt = c.text, letBg = c.letterBg, dim = false;
              if (done) {
                if (isCor) { bg = c.correctBg; border = c.correct; txt = c.correct; letBg = c.correct; }
                else if (isSel) { bg = c.incorrectBg; border = c.incorrect; txt = c.incorrect; letBg = c.incorrect; }
                else dim = true;
              } else if (isSel) { bg = c.accentBg; border = c.accent; letBg = c.accent; }

              return (
                <View key={L} style={{ position: 'relative' }}>
                  {/* Glow effect behind selected answer */}
                  {done && (isCor || (isSel && !isCor)) && (
                    <Animated.View style={[st.glow, { backgroundColor: isCor ? c.correct : c.incorrect, opacity: glowOpacity, borderRadius: 12 }]} />
                  )}
                  <TouchableOpacity testID={`answer-btn-${L}`} style={[st.aBtn, { backgroundColor: bg, borderColor: border }, dim && st.dim]} onPress={() => !done && setSel(L)} disabled={done} activeOpacity={0.7}>
                    <View style={[st.lC, { backgroundColor: letBg }]}><Text style={st.lT}>{L}</Text></View>
                    <Text style={[st.aTxt, { color: txt }]}>{aT(q, L)}</Text>
                    {done && isCor && <Ionicons name="checkmark-circle" size={20} color={c.correct} />}
                    {done && isSel && !isCor && <Ionicons name="close-circle" size={20} color={c.incorrect} />}
                  </TouchableOpacity>
                </View>
              );
            })}
          </View>

          {/* Inline feedback */}
          {done && (
            <View style={st.fb}>
              <View style={st.fbR}>
                <Ionicons name={sel === q.correct_answer ? 'checkmark-circle' : 'close-circle'} size={15} color={sel === q.correct_answer ? '#6EE7A8' : c.incorrect} />
                <Text style={[st.fbS, { color: sel === q.correct_answer ? '#6EE7A8' : c.incorrect }]}>{sel === q.correct_answer ? t.correct : t.incorrect}</Text>
                <TouchableOpacity testID="tts-explanation-btn" style={[st.ttsSmall, { opacity: ttsPlaying === 'explanation' ? 1 : 0.4 }]} onPress={speakExplanation} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
                  <Ionicons name={ttsPlaying === 'explanation' ? 'volume-high' : 'volume-medium-outline'} size={15} color={ttsPlaying === 'explanation' ? c.accent : c.textSecondary} />
                </TouchableOpacity>
              </View>
              <Text style={[st.fbE, { color: c.textSecondary }]}>{eT(q)}</Text>
              {language !== 'th' && <Text style={[st.fbTh, { color: `${c.accent}B0` }]}>{eT(q, 'th')}</Text>}
            </View>
          )}

          {/* Free limit message */}
          {showLimit && (
            <View style={[st.limitCard, { backgroundColor: `${c.accent}12` }]}>
              <Text style={[st.limitMsg, { color: c.textSecondary }]}>{t.limitMsg}</Text>
              <TouchableOpacity testID="quiz-unlock-btn" style={[st.limitBtn, { backgroundColor: c.accent }]} onPress={() => router.push('/paywall')}>
                <Ionicons name="diamond" size={16} color="#0F172A" />
                <Text style={st.limitBtnTxt}>{t.unlock}</Text>
              </TouchableOpacity>
            </View>
          )}
        </Animated.View>
      </ScrollView>

      {/* Action */}
      {!showLimit && (
        <View style={st.actW}>
          {!done ? (
            <TouchableOpacity testID="check-answer-btn" style={[st.actB, { backgroundColor: sel ? c.accent : c.letterBg }]} onPress={handleCheck} disabled={!sel}>
              <Text style={[st.actT, { color: sel ? '#0F172A' : c.textMuted }]}>{t.check}</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity testID="next-btn" style={[st.actB, { backgroundColor: c.accent }]} onPress={handleNext}>
              <Text style={[st.actT, { color: '#0F172A' }]}>{idx >= questions.length - 1 ? t.finish : t.next}</Text>
              <Ionicons name="arrow-forward" size={18} color="#0F172A" />
            </TouchableOpacity>
          )}
        </View>
      )}
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  hdr: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingVertical: 10, gap: 10 },
  iBtn: { width: 38, height: 38, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  pWrap: { flex: 1 },
  pTxt: { fontSize: 12, fontWeight: '600', textAlign: 'center', marginBottom: 5 },
  pBar: { height: 5, borderRadius: 3 },
  pFill: { height: '100%', borderRadius: 3 },
  tmr: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 6, gap: 5 },
  tmrTxt: { fontSize: 15, fontWeight: '700', fontVariant: ['tabular-nums'] },
  scr: { paddingHorizontal: 14, paddingTop: 6, paddingBottom: 10 },
  qCard: { borderRadius: 14, padding: 18, marginBottom: 10, borderWidth: 1 },
  qImg: { width: '100%', height: 180, borderRadius: 10, marginBottom: 14, borderWidth: 1 },
  qTxt: { fontSize: 18, fontWeight: '700', lineHeight: 26 },
  translateRow: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 10, opacity: 0.6 },
  hintT: { fontSize: 11 },
  thW: { marginTop: 10 },
  thL: { height: 1, marginBottom: 10 },
  thTxt: { fontSize: 15, lineHeight: 22 },
  listenBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', borderRadius: 14, paddingVertical: 14, marginBottom: 14, gap: 8, borderWidth: 1, opacity: 0.6 },
  listenIcon: { fontSize: 18 },
  listenText: { fontSize: 15, fontWeight: '600' },
  aW: { gap: 12 },
  aBtn: { flexDirection: 'row', alignItems: 'center', borderRadius: 12, paddingVertical: 13, paddingHorizontal: 14, borderWidth: 1.5 },
  dim: { opacity: 0.35 },
  glow: { position: 'absolute', top: -2, left: -2, right: -2, bottom: -2 },
  lC: { width: 32, height: 32, borderRadius: 10, justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  lT: { fontSize: 14, fontWeight: '700', color: '#F8FAFC' },
  aTxt: { flex: 1, fontSize: 15, lineHeight: 21 },
  fb: { marginTop: 16, paddingHorizontal: 2 },
  fbR: { flexDirection: 'row', alignItems: 'center', gap: 5, marginBottom: 4 },
  fbS: { fontSize: 13, fontWeight: '500', flex: 1 },
  ttsSmall: { width: 28, height: 28, borderRadius: 14, justifyContent: 'center', alignItems: 'center' },
  fbE: { fontSize: 13, lineHeight: 19, opacity: 0.75 },
  fbTh: { fontSize: 12, lineHeight: 18, marginTop: 3 },
  limitCard: { marginTop: 16, borderRadius: 16, paddingVertical: 16, paddingHorizontal: 20, alignItems: 'center' },
  limitMsg: { fontSize: 13, fontWeight: '500', textAlign: 'center', marginBottom: 14 },
  limitBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', borderRadius: 12, paddingVertical: 12, paddingHorizontal: 24, gap: 6 },
  limitBtnTxt: { fontSize: 14, fontWeight: '700', color: '#0F172A' },
  actW: { paddingHorizontal: 14, paddingTop: 10, paddingBottom: 14 },
  actB: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 14, gap: 6 },
  actT: { fontSize: 15, fontWeight: '700' },
});
