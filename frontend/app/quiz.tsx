import React, { useEffect, useState, useRef, useCallback } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Animated, Image, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as Speech from 'expo-speech';
import * as Haptics from 'expo-haptics';
import { Platform, Vibration } from 'react-native';
import { useAppStore } from '../src/store/appStore';
import { api, Question } from '../src/services/api';
import { playCorrectSound, playIncorrectSound, cleanupSounds } from '../src/sounds';
import { useScreenProtection } from '../src/hooks/useScreenProtection';
import { aiLearningApi } from '../src/services/aiLearning';
import { ExplanationCard } from '../src/components/ExplanationCard';

const LETTERS = ['A', 'B', 'C', 'D'];
const EXAM_TIME = 90 * 60;
const PASS = 85;

const T: Record<string, Record<string, string>> = {
  no: { check: 'Sjekk svar', next: 'Neste', finish: 'Fullfør', correct: 'Riktig!', incorrect: 'Feil!', hint: 'Trykk for Thai', limitMsg: 'Gratis grense nådd', unlock: 'Lås opp Premium', listen: 'Lytt', listening: 'Spiller...', listenExpl: 'Lytt', accountTitle: 'Opprett konto for å fortsette', accountBody: 'Du har brukt opp 10 gratis spørsmål. Opprett en konto for å fortsette og få tilgang til pakketilbud.', accountSignup: 'Opprett konto', accountLogin: 'Logg inn', accountCancel: 'Avbryt' },
  th: { check: 'ตรวจคำตอบ', next: 'ถัดไป', finish: 'เสร็จสิ้น', correct: 'ถูกต้อง!', incorrect: 'ผิด!', hint: 'แตะเพื่อแปล', limitMsg: 'ถึงขีดจำกัดฟรี', unlock: 'ปลดล็อค Premium', listen: 'ฟัง', listening: 'กำลังเล่น...', listenExpl: 'ฟัง', accountTitle: 'สร้างบัญชีเพื่อดำเนินการต่อ', accountBody: 'คุณใช้คำถามฟรี 10 ข้อหมดแล้ว สร้างบัญชีเพื่อดำเนินการต่อและรับข้อเสนอแพ็กเกจ', accountSignup: 'สร้างบัญชี', accountLogin: 'เข้าสู่ระบบ', accountCancel: 'ยกเลิก' },
  en: { check: 'Check Answer', next: 'Next', finish: 'Finish', correct: 'Correct!', incorrect: 'Incorrect!', hint: 'Tap for Thai', limitMsg: 'Free limit reached', unlock: 'Unlock Premium', listen: 'Listen', listening: 'Playing...', listenExpl: 'Listen', accountTitle: 'Create an account to continue', accountBody: 'You have used your 10 free questions. Create an account to continue and see package offers.', accountSignup: 'Create account', accountLogin: 'Log in', accountCancel: 'Cancel' },
};

export default function QuizScreen() {
  const router = useRouter();
  const { mode, category } = useLocalSearchParams<{ mode: string; category: string }>();
  const store = useAppStore();
  const { language, deviceId, addBookmark, removeBookmark, isBookmarked, setProgress, colors: c, soundEnabled, soundStyle, hapticsEnabled, isPremium, isAuthenticated, incrementFreeQuestions, canAnswerFree, freeRemaining, needsAccountGate, updateStreak, setLastAttempt } = store;
  const t = T[language] || T.en;

  // Screen capture protection
  useScreenProtection(language);

  // ── Auth + paywall gate ──
  // Shows the right destination when a free user tries to continue past their
  // 10-question limit:
  //   • Guest (not logged in)  → Alert → /signup or /login (with redirect=paywall)
  //   • Logged-in free user    → /paywall directly
  const showAccountOrPaywall = useCallback(() => {
    if (isPremium) return false; // premium has unlimited
    if (canAnswerFree()) return false; // still has free quota
    if (!isAuthenticated) {
      // Guest hit the lifetime limit — must sign up or log in first
      Alert.alert(
        t.accountTitle,
        t.accountBody,
        [
          { text: t.accountCancel, style: 'cancel', onPress: () => router.back() },
          { text: t.accountLogin, onPress: () => router.replace({ pathname: '/login', params: { redirect: 'paywall' } }) },
          { text: t.accountSignup, onPress: () => router.replace({ pathname: '/signup', params: { redirect: 'paywall' } }) },
        ],
        { cancelable: false },
      );
    } else {
      // Already authenticated — go straight to paywall
      router.replace('/paywall');
    }
    return true;
  }, [isPremium, isAuthenticated, t]);

  // Gate: if free user has no quota left when entering quiz, redirect appropriately
  useEffect(() => {
    if (!isPremium && !canAnswerFree()) {
      showAccountOrPaywall();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
  const [ttsSpeed, setTtsSpeed] = useState(1.0); // 1x, 1.5x, 2x
  const ttsSpeedRef = useRef(1.0); // Live ref so speakSequence always reads the current speed
  const ttsCancelled = useRef(false);
  const ttsGen = useRef(0); // Monotonic counter — invalidates any in-flight speakSequence
  const voiceMapRef = useRef<Record<string, string | undefined>>({}); // lang → preferred voice identifier

  const fade = useRef(new Animated.Value(1)).current;
  const glowAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const questionStartedAt = useRef<number>(Date.now());
  const isExam = mode === 'exam';
  const isReviewWrong = mode === 'review-wrong';
  const isDaily = mode === 'daily';
  const isSmart = mode === 'smart';

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
    try {
      if (isReviewWrong) {
        const last = useAppStore.getState().lastAttempt;
        if (last && last.questions.length > 0) {
          const wrong = last.questions.filter((q, i) => !last.answers[i]?.correct);
          setQuestions(wrong);
        }
      } else if (isSmart) {
        // Smart practice — adaptive queue from AI engine
        try {
          const data = await aiLearningApi.getSmartPractice(deviceId, 10);
          if (data && data.questions.length > 0) {
            setQuestions(data.questions);
          } else {
            // fallback: random
            setQuestions(await api.getRandomQuestions(10));
          }
        } catch {
          setQuestions(await api.getRandomQuestions(10));
        }
      } else if (isDaily) {
        // Daily test — cached per calendar day
        const today = new Date().toISOString().slice(0, 10);
        const cacheKey = `dailyTest_${today}`;
        try {
          const cached = await AsyncStorage.getItem(cacheKey);
          if (cached) {
            setQuestions(JSON.parse(cached));
          } else {
            const q = await api.getRandomQuestions(5);
            await AsyncStorage.setItem(cacheKey, JSON.stringify(q));
            // Cleanup old daily caches (> 1 day old)
            const allKeys = await AsyncStorage.getAllKeys();
            const oldDailyKeys = allKeys.filter((k) => k.startsWith('dailyTest_') && k !== cacheKey && k !== `dailyTest_result_${today}`);
            if (oldDailyKeys.length > 0) await AsyncStorage.multiRemove(oldDailyKeys);
            setQuestions(q);
          }
        } catch (e) {
          setQuestions(await api.getRandomQuestions(5));
        }
      } else {
        const maxQ = isExam ? 45 : 10;
        const count = Math.min(maxQ, freeRemaining());
        const qs = await api.getRandomQuestions(Math.max(1, count), category === 'all' ? undefined : category);
        // Debug: log full question objects so we can verify live text matches DB
        if (qs?.[0]) {
          console.log('[Quiz DEBUG] First question loaded:', JSON.stringify({
            id: qs[0].id,
            'question.en': qs[0].question?.en,
            'options.en': qs[0].options?.map((o: any) => o.text?.en),
            correct: qs[0].correctOptionId,
            'explanation.en': qs[0].explanation?.en,
          }, null, 2));
        }
        setQuestions(qs);
      }
    } catch (e) {}
    finally { setLoading(false); }
  };

  const timeUp = useCallback(() => {
    const cor = hist.filter((a) => a.correct).length;
    // Save attempt even on time-up
    setLastAttempt({
      questions,
      answers: hist.map((h) => ({ questionId: h.question_id, selected: h.selected_answer, correct: h.correct })),
      mode: mode || 'practice',
      category: category === 'all' ? undefined : (category as string | undefined),
      startedAt: startTime.toISOString(),
    });
    goRes(cor, questions.length > 0 ? (cor / questions.length) * 100 : 0);
  }, [hist, questions, mode, category, startTime, setLastAttempt]);

  const q = questions[idx];

  // V2 helpers: access localized text from nested schema
  const qT = (qu: Question, l?: string) => qu.question?.[l || language] || qu.question?.no || '';
  const optText = (qu: Question, optId: string, l?: string) => {
    const opt = qu.options?.find(o => o.id === optId);
    return opt?.text?.[l || language] || opt?.text?.no || '';
  };
  const eT = (qu: Question, l?: string) => qu.explanation?.[l || language] || qu.explanation?.no || '';

  const handleCheck = async () => {
    if (!sel || !q) return;
    setDone(true);
    const cor = sel === q.correctOptionId;

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

    if (soundEnabled || hapticsEnabled) {
      const opts = { soundEnabled, hapticsEnabled, style: soundStyle };
      cor ? playCorrectSound(opts) : playIncorrectSound(opts);
    }

    setHist((p) => [...p, { question_id: q.id, selected_answer: sel, correct: cor }]);
    if (!isPremium) incrementFreeQuestions();
    await updateStreak();
    try { await api.updateProgress(deviceId, cor, q.category); setProgress(await api.getProgress(deviceId)); } catch (e) {}

    // AI learning: record attempt (fire-and-forget, never blocks quiz)
    aiLearningApi.recordAttempt({
      device_id:     deviceId,
      question_id:   q.id,
      is_correct:    cor,
      time_taken_ms: Date.now() - questionStartedAt.current,
      category:      q.category || '',
      mode:          mode || 'practice',
      difficulty:    q.difficulty || 'medium',
    });
  };

  const handleNext = () => {
    tickHaptic();
    stopTts(); // Stop any playing TTS immediately
    if (idx >= questions.length - 1) { finishQ(); return; }
    // Free user hit the lifetime cap → route to account gate or paywall
    if (showAccountOrPaywall()) return;
    // Smooth slide transition
    Animated.timing(fade, { toValue: 0, duration: 120, useNativeDriver: true }).start(() => {
      questionStartedAt.current = Date.now();
      setIdx((p) => p + 1); setSel(null); setDone(false); setShowTh(false); setShowLimit(false);
      Animated.timing(fade, { toValue: 1, duration: 120, useNativeDriver: true }).start();
    });
  };

  const finishQ = async () => {
    if (timerRef.current) clearInterval(timerRef.current);
    const cor = hist.filter((a) => a.correct).length;
    const pct = (cor / questions.length) * 100;
    // Save full attempt to store for review on results screen
    setLastAttempt({
      questions,
      answers: hist.map((h) => ({ questionId: h.question_id, selected: h.selected_answer, correct: h.correct })),
      mode: mode || 'practice',
      category: category === 'all' ? undefined : category,
      startedAt: startTime.toISOString(),
    });
    // Mark daily test as done
    if (isDaily) {
      const today = new Date().toISOString().slice(0, 10);
      await AsyncStorage.setItem(`dailyTest_result_${today}`, JSON.stringify({ correct: cor, total: questions.length, pct, at: new Date().toISOString() }));
    }
    try { await api.saveQuizAttempt({ device_id: deviceId, mode: mode || 'practice', category: category === 'all' ? undefined : category, total_questions: questions.length, correct_answers: cor, score_percentage: pct, passed: isExam ? pct >= PASS : undefined, questions_answered: hist, started_at: startTime.toISOString() }); } catch (e) {}
    goRes(cor, pct);
    // After results navigation, gate fires automatically on next quiz mount via useEffect.
    // But also show here in case store hydration was delayed on the previous mount.
    if (!isPremium && !canAnswerFree()) {
      showAccountOrPaywall();
    }
  };

  const goRes = (cor: number, pct: number) => {
    router.replace({ pathname: '/results', params: { total: questions.length.toString(), correct: cor.toString(), mode: mode || 'practice', passed: isExam ? (pct >= PASS ? 'true' : 'false') : '' } });
  };

  // Stop any in-flight TTS *cleanly*. The generation counter is enough to make
  // speakSequence bail between segments — so we only need a SINGLE Speech.stop().
  // Earlier versions scheduled delayed stops at 30ms/250ms which killed the first
  // 1–2 segments of the NEXT playback when the user rapidly tapped play again.
  const stopTts = () => {
    ttsGen.current += 1; // invalidates any in-flight speakSequence
    ttsCancelled.current = true;
    setTtsPlaying(null);
    setSpeaking(false);
    try { Speech.stop(); } catch {}
  };

  const langCode = (l: string) => l === 'th' ? 'th-TH' : l === 'no' ? 'nb-NO' : 'en-US';

  // Light tactile tick. Used for answer-letter selection and the next button.
  // Always falls back to Vibration on Android in case Haptics isn't available
  // (some OEM ROMs disable it for non-system apps).
  const tickHaptic = () => {
    if (!hapticsEnabled || Platform.OS === 'web') return;
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light).catch(() => {});
    } catch {}
    if (Platform.OS === 'android') {
      try { Vibration.vibrate(10); } catch {}
    }
  };

  // Prefer male voices for speech. Expo Speech doesn't expose "gender" directly,
  // so we heuristically match voice identifiers/names against known male markers.
  // Google TTS uses x-ttm (Thai male), x-stm/wavenet-D (male English), etc.
  // We pick per-language once on mount and cache the identifier.
  const MALE_PATTERNS: Record<string, RegExp[]> = {
    'th-TH': [/-ttm\b|-stm\b|\bmale\b|-a\b|\bm01\b/i],
    'nb-NO': [/-ttm\b|-wavenet-b\b|-wavenet-c\b|\bmale\b|\bm01\b/i],
    'en-US': [/-wavenet-[abd]\b|-neural2-[abd]\b|-ttm\b|\bmale\b|\bm01\b/i],
  };

  useEffect(() => {
    (async () => {
      try {
        const voices = await Speech.getAvailableVoicesAsync();
        const pickFor = (lang: string): string | undefined => {
          const candidates = voices.filter((v: any) =>
            typeof v.language === 'string' && v.language.toLowerCase().startsWith(lang.toLowerCase())
          );
          if (!candidates.length) return undefined;
          const patterns = MALE_PATTERNS[lang] || [];
          // 1) Match against known male patterns on identifier + name
          for (const p of patterns) {
            const hit = candidates.find((v: any) => p.test(v.identifier || '') || p.test(v.name || ''));
            if (hit) return hit.identifier;
          }
          // 2) Fall back to the first "enhanced/local" voice if available (better quality)
          const enhanced = candidates.find((v: any) => String(v.quality || '').toLowerCase() === 'enhanced');
          return (enhanced || candidates[0]).identifier;
        };
        voiceMapRef.current = {
          'th-TH': pickFor('th-TH'),
          'nb-NO': pickFor('nb-NO'),
          'en-US': pickFor('en-US'),
        };
        // One-time log so user can see what was picked
        console.log('[Speech] Picked voices:', voiceMapRef.current);
      } catch (e) {
        console.warn('[Speech] voice enumeration failed', e);
      }
    })();
  }, []);

  const SPEED_OPTIONS = [
    { label: '1x', value: 1.0 },
    { label: '1.5x', value: 1.5 },
    { label: '2x', value: 2.0 },
  ];

  // Change speed: update state + ref live; if currently speaking, restart current playback
  const changeSpeed = (v: number) => {
    if (v === ttsSpeed) return;
    ttsSpeedRef.current = v;
    setTtsSpeed(v);
    // If audio is playing, stop and restart with new speed
    const wasPlaying = ttsPlaying;
    if (wasPlaying) {
      stopTts();
      setTimeout(() => {
        if (wasPlaying === 'question') speakQuestion();
        else if (wasPlaying === 'explanation') speakExplanation();
      }, 160);
    }
  };

  const speakSequence = async (segments: { text: string; lang: string }[]) => {
    ttsCancelled.current = false;
    const myGen = ++ttsGen.current; // claim this generation; any newer stopTts will invalidate us

    // ── Android TTS warm-up (initial) ──
    // Speech.stop() (called by stopTts before us) doesn't fully drain on Android
    // for ~150-250ms. Any Speech.speak() fired during that window is silently
    // dropped — that was the "starts from B" bug. We unconditionally wait here
    // so the first segment (the question itself) ALWAYS plays.
    await new Promise(r => setTimeout(r, 220));
    if (ttsCancelled.current || ttsGen.current !== myGen) return;

    for (let i = 0; i < segments.length; i++) {
      if (ttsCancelled.current || ttsGen.current !== myGen) break;
      const s = segments[i];
      const code = langCode(s.lang);
      const baseRate = s.lang === 'th' ? 0.85 : 0.9;
      const rate = Math.min(2.0, Math.max(0.1, baseRate * ttsSpeedRef.current));

      // ── Inter-segment safety on Android ──
      // After onDone fires for the previous segment, the Android TTS engine
      // is still finalizing for ~50-200ms. Calling Speech.speak() during
      // that window silently drops the utterance — that was the
      // "skips option A" bug. We poll Speech.isSpeakingAsync() until the
      // engine reports idle, then add a small fixed gap. iOS doesn't have
      // this bug, so we use a much shorter delay there.
      if (i > 0) {
        if (Platform.OS === 'android') {
          // Poll up to ~1.5s (usually idle within 50-100ms)
          for (let tries = 0; tries < 30; tries++) {
            if (ttsCancelled.current || ttsGen.current !== myGen) break;
            try {
              const speaking = await Speech.isSpeakingAsync();
              if (!speaking) break;
            } catch {}
            await new Promise(r => setTimeout(r, 50));
          }
          // Fixed gap so the next utterance is reliably accepted
          if (!ttsCancelled.current && ttsGen.current === myGen) {
            await new Promise(r => setTimeout(r, 180));
          }
        } else {
          await new Promise(r => setTimeout(r, 80));
        }
        if (ttsCancelled.current || ttsGen.current !== myGen) break;
      }

      // NOTE: intentionally NOT passing `voice`. On Android, picking a voice
      // identifier via getAvailableVoicesAsync() is unreliable — if the exact
      // voice isn't installed/downloaded, Speech.speak silently drops the first
      // 1–2 utterances before falling back to default. Using only `language`
      // lets Android pick the default installed voice for that locale.
      await new Promise<void>((resolve) => {
        let resolved = false;
        const finish = () => { if (!resolved) { resolved = true; resolve(); } };
        Speech.speak(s.text, {
          language: code,
          rate,
          onDone: finish,
          onError: finish,
          onStopped: finish,
        });
      });
      // Extra guard: if we were cancelled while a segment was running, bail now
      if (ttsCancelled.current || ttsGen.current !== myGen) break;
    }
  };

  const speakQuestion = async () => {
    if (!q) return;
    if (ttsPlaying === 'question') { stopTts(); return; }
    stopTts();
    setTtsPlaying('question');
    setSpeaking(true);

    const segments: { text: string; lang: string }[] = [];
    // Always read in Thai only
    segments.push({ text: qT(q, 'th'), lang: 'th' });
    for (const L of LETTERS) {
      segments.push({ text: `${L}. ${optText(q, L, 'th')}`, lang: 'th' });
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
    // Always read explanation in Thai only
    segments.push({ text: eT(q, 'th'), lang: 'th' });

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
        <TouchableOpacity testID="quiz-exit-btn" style={[st.iBtn, { backgroundColor: c.card }]} onPress={() => { stopTts(); router.back(); }}>
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

          <View style={[st.qCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
                {q.bildeUrl && q.has_real_image ? (
                  <Image
                    testID="question-image"
                    source={{ uri: q.bildeUrl }}
                    style={st.qImg}
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

              {/* Audio controls */}
              <View style={st.audioRow}>
                <TouchableOpacity
                  testID="tts-question-btn"
                  onPress={speakQuestion}
                  activeOpacity={0.7}
                  style={[st.playBtn, { backgroundColor: ttsPlaying === 'question' ? c.accent : c.card, borderColor: ttsPlaying === 'question' ? c.accent : c.cardBorder }]}
                >
                  <Ionicons
                    name={ttsPlaying === 'question' ? 'pause' : 'play'}
                    size={16}
                    color={ttsPlaying === 'question' ? '#0F172A' : c.textSecondary}
                  />
                </TouchableOpacity>
                {SPEED_OPTIONS.map((opt) => {
                  const active = ttsSpeed === opt.value;
                  return (
                    <TouchableOpacity
                      key={opt.value}
                      testID={`tts-speed-${opt.label}`}
                      style={[st.speedChip, active && { backgroundColor: c.accentBg }]}
                      onPress={() => changeSpeed(opt.value)}
                      activeOpacity={0.7}
                      hitSlop={{ top: 8, bottom: 8, left: 4, right: 4 }}
                    >
                      <Text style={[st.speedText, { color: active ? c.accent : c.textMuted, fontWeight: active ? '800' : '600' }]}>{opt.label}</Text>
                    </TouchableOpacity>
                  );
                })}
              </View>

          <View style={st.aW}>
            {LETTERS.map((L) => {
              const isSel = sel === L, isCor = q.correctOptionId === L;
              let bg = c.answerBg, border = c.answerBorder, txt = c.text, letBg = c.letterBg, dim = false;
              // letterOnColored = true whenever the letter circle is a saturated
              // brand color (orange/green/red). In that case we need WHITE text
              // for guaranteed contrast on BOTH dark and light themes — the
              // theme's letterText is dark navy in light mode and would
              // disappear on the orange/green/red circle.
              let letterOnColored = false;
              if (done) {
                if (isCor) { bg = c.correctBg; border = c.correct; txt = c.correct; letBg = c.correct; letterOnColored = true; }
                else if (isSel) { bg = c.incorrectBg; border = c.incorrect; txt = c.incorrect; letBg = c.incorrect; letterOnColored = true; }
                else dim = true;
              } else if (isSel) { bg = c.accentBg; border = c.accent; letBg = c.accent; letterOnColored = true; }

              return (
                <View key={L} style={{ position: 'relative' }}>
                  {/* Glow effect behind selected answer */}
                  {done && (isCor || (isSel && !isCor)) && (
                    <Animated.View style={[st.glow, { backgroundColor: isCor ? c.correct : c.incorrect, opacity: glowOpacity, borderRadius: 12 }]} />
                  )}
                  <TouchableOpacity testID={`answer-btn-${L}`} style={[st.aBtn, { backgroundColor: bg, borderColor: border }, dim && st.dim]} onPress={() => { if (!done) { tickHaptic(); setSel(L); } }} disabled={done} activeOpacity={0.7}>
                    <View style={[st.lC, { backgroundColor: letBg }]}><Text style={[st.lT, { color: letterOnColored ? '#FFFFFF' : c.letterText }]}>{L}</Text></View>
                    <Text style={[st.aTxt, { color: txt }]}>{optText(q, L)}</Text>
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
                <Ionicons name={sel === q.correctOptionId ? 'checkmark-circle' : 'close-circle'} size={15} color={sel === q.correctOptionId ? '#6EE7A8' : c.incorrect} />
                <Text style={[st.fbS, { color: sel === q.correctOptionId ? '#6EE7A8' : c.incorrect }]}>{sel === q.correctOptionId ? t.correct : t.incorrect}</Text>
                <TouchableOpacity testID="tts-explanation-btn" style={[st.ttsSmall, { opacity: ttsPlaying === 'explanation' ? 1 : 0.4 }]} onPress={speakExplanation} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
                  <Ionicons name={ttsPlaying === 'explanation' ? 'volume-high' : 'volume-medium-outline'} size={15} color={ttsPlaying === 'explanation' ? c.accent : c.textSecondary} />
                </TouchableOpacity>
              </View>
              <Text style={[st.fbE, { color: c.textSecondary }]}>{eT(q)}</Text>
              {language !== 'th' && <Text style={[st.fbTh, { color: `${c.accent}B0` }]}>{eT(q, 'th')}</Text>}

              {/* AI deep explanation — on-demand */}
              <ExplanationCard
                questionId={q.id}
                correctOptionId={q.correctOptionId}
                options={q.options || []}
                lang={language}
                colors={c}
              />
            </View>
          )}

          {/* Free limit message */}
          {showLimit && (
            <View style={[st.limitCard, { backgroundColor: `${c.accent}12` }]}>
              <Text style={[st.limitMsg, { color: c.textSecondary }]}>{t.limitMsg}</Text>
              <TouchableOpacity testID="quiz-unlock-btn" style={[st.limitBtn, { backgroundColor: c.accent }]} onPress={showAccountOrPaywall}>
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
  qCard: { borderRadius: 16, padding: 20, marginBottom: 14, borderWidth: 1 },
  qImg: { width: '100%', height: 200, borderRadius: 12, marginBottom: 18, backgroundColor: 'transparent' },
  qTxt: { fontSize: 21, fontWeight: '700', lineHeight: 30, letterSpacing: -0.3 },
  translateRow: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 12, opacity: 0.65 },
  hintT: { fontSize: 12 },
  thW: { marginTop: 12 },
  thL: { height: 1, marginBottom: 10 },
  thTxt: { fontSize: 16, lineHeight: 24 },
  audioRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10, marginBottom: 18, paddingHorizontal: 4 },
  playBtn: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center', borderWidth: 1.5 },
  speedChip: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 14 },
  speedText: { fontSize: 13, letterSpacing: 0.2 },
  aW: { gap: 12 },
  aBtn: { flexDirection: 'row', alignItems: 'center', borderRadius: 14, paddingVertical: 15, paddingHorizontal: 16, borderWidth: 1.5 },
  dim: { opacity: 0.45 },
  glow: { position: 'absolute', top: -2, left: -2, right: -2, bottom: -2 },
  lC: { width: 34, height: 34, borderRadius: 11, justifyContent: 'center', alignItems: 'center', marginRight: 14 },
  lT: { fontSize: 15, fontWeight: '700' },
  aTxt: { flex: 1, fontSize: 16, lineHeight: 23 },
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
