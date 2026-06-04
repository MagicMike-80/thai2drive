import React, { useState, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';

// ─── Translation strings ─────────────────────────────────────────────────────
const TR: Record<string, Record<string, string | string[]>> = {
  no: {
    title: '🚗 Michael Trafikklærer',
    online: '● Online',
    inputPlaceholder: 'Still et spørsmål...',
    send: 'Send',
    errorMsg: 'Beklager, noe gikk galt. Prøv igjen.',
    feedbackQ: 'Hjalp dette?',
    thumbsYes: '👍 Ja',
    thumbsNo: '👎 Nei',
    feedbackThanks: 'Takk for tilbakemeldingen 🙏',
    feedbackReasons: ['For langt', 'For vanskelig', 'Feil språk', 'Svarte ikke på spørsmålet'],
  },
  th: {
    title: '🚗 ไมเคิล ครูสอนขับรถ',
    online: '● ออนไลน์',
    inputPlaceholder: 'ถามคำถาม...',
    send: 'ส่ง',
    errorMsg: 'ขอโทษครับ มีข้อผิดพลาด กรุณาลองใหม่อีกครั้ง',
    feedbackQ: 'คำตอบนี้ช่วยไหม?',
    thumbsYes: '👍 ช่วย',
    thumbsNo: '👎 ไม่ช่วย',
    feedbackThanks: 'ขอบคุณสำหรับความคิดเห็น 🙏',
    feedbackReasons: ['ยาวเกินไป', 'ยากเกินไป', 'ผิดภาษา', 'ไม่ตอบคำถาม'],
  },
  en: {
    title: '🚗 Michael Driving Instructor',
    online: '● Online',
    inputPlaceholder: 'Ask a question...',
    send: 'Send',
    errorMsg: 'Sorry, something went wrong. Please try again.',
    feedbackQ: 'Was this helpful?',
    thumbsYes: '👍 Yes',
    thumbsNo: '👎 No',
    feedbackThanks: 'Thanks for the feedback 🙏',
    feedbackReasons: ['Too long', 'Too difficult', 'Wrong language', 'Did not answer'],
  },
};

// ─── Types ───────────────────────────────────────────────────────────────────
interface Message {
  role: 'user' | 'assistant';
  content: string;
  suggestions?: string[];          // Fix 2: carry reply chips
}

interface Topic { icon: string; text: string; }

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

// ─── Component ───────────────────────────────────────────────────────────────
export default function TeacherScreen() {
  const router = useRouter();
  const { language, colors } = useAppStore();
  const c = colors;
  const t = TR[language] || TR.no;
  const lang = language || 'no';

  const [messages, setMessages] = useState<Message[]>([]);
  const [welcomeMsg, setWelcomeMsg] = useState<string>('');   // Fix 4: from backend
  const [topics, setTopics] = useState<Topic[]>([]);           // Fix 3: from backend
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  // feedback: key = index in allMessages, value = 'pending' | 'negative' | 'done'
  const [feedbackMap, setFeedbackMap] = useState<Record<number, 'pending' | 'negative' | 'done'>>({});
  const scrollRef = useRef<ScrollView>(null);

  const sendFeedback = useCallback(async (
    msgIndex: number,
    allMsgs: Message[],
    helpful: boolean,
    reason?: string,
  ) => {
    setFeedbackMap((prev) => ({ ...prev, [msgIndex]: 'done' }));
    const assistantMsg = allMsgs[msgIndex];
    const precedingMsg = msgIndex > 0 ? allMsgs[msgIndex - 1] : null;
    try {
      await fetch(`${BACKEND_URL}/api/teacher/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          language: lang,
          user_message: precedingMsg?.role === 'user' ? precedingMsg.content : null,
          assistant_answer: assistantMsg?.content ?? null,
          helpful,
          reason: reason ?? null,
          source: 'web',
        }),
      });
    } catch { /* fire-and-forget — don't break the chat on feedback error */ }
  }, [sessionId, lang]);

  // Fix 3 + 4: fetch welcome + topics from backend on mount / language change
  React.useEffect(() => {
    (async () => {
      try {
        const [wRes, tRes] = await Promise.all([
          fetch(`${BACKEND_URL}/api/teacher/welcome?lang=${lang}`),
          fetch(`${BACKEND_URL}/api/teacher/topics?lang=${lang}`),
        ]);
        const wData = await wRes.json();
        const tData = await tRes.json();
        setWelcomeMsg(wData.welcome || '');
        setTopics(tData.topics || []);
      } catch {
        // Fallback: keep empty (component handles gracefully)
      }
    })();
  }, [lang]);

  const allMessages: Message[] = welcomeMsg
    ? [{ role: 'assistant', content: welcomeMsg }, ...messages]
    : messages;

  const sendMessage = useCallback(async (text: string) => {
    const msg = text.trim();
    if (!msg || loading) return;

    setInput('');
    setShowSuggestions(false);
    setLoading(true);

    const userMsg: Message = { role: 'user', content: msg };
    setMessages((prev) => [...prev, userMsg]);

    setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);

    try {
      const res = await fetch(`${BACKEND_URL}/api/teacher/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: msg, language: lang }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      if (data.session_id && !sessionId) setSessionId(data.session_id);

      // Fix 2: store suggestions with the message
      const assistantMsg: Message = {
        role: 'assistant',
        content: data.reply,
        suggestions: data.suggestions || [],
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [...prev, { role: 'assistant', content: t.errorMsg }]);
    } finally {
      setLoading(false);
      setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 150);
    }
  }, [loading, sessionId, lang, t]);

  return (
    <SafeAreaView style={[s.safe, { backgroundColor: c.bg }]}>
      {/* Header */}
      <View style={[s.header, { borderBottomColor: c.cardBorder }]}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn} activeOpacity={0.7}>
          <Ionicons name="chevron-back" size={24} color={c.text} />
        </TouchableOpacity>
        <View style={s.headerCenter}>
          <View style={[s.avatarSmall, { backgroundColor: '#1E3A5F' }]}>
            <Text style={s.avatarEmoji}>🚗</Text>
          </View>
          <View>
            <Text style={[s.headerTitle, { color: c.text }]}>{t.title}</Text>
            <Text style={[s.headerSub, { color: '#10B981' }]}>{t.online}</Text>
          </View>
        </View>
        <View style={{ width: 40 }} />
      </View>

      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={0}
      >
        {/* Messages */}
        <ScrollView
          ref={scrollRef}
          style={s.messageList}
          contentContainerStyle={s.messageListContent}
          keyboardShouldPersistTaps="handled"
          onContentSizeChange={() => scrollRef.current?.scrollToEnd({ animated: false })}
        >
          {allMessages.map((msg, i) => {
            // Don't show feedback for welcome message (index 0 when welcomeMsg is set)
            const isWelcome = welcomeMsg && i === 0;
            const fb = feedbackMap[i];
            const reasons = t.feedbackReasons as string[];
            return (
              <React.Fragment key={i}>
                <View style={[s.bubbleRow, msg.role === 'user' ? s.bubbleRowUser : s.bubbleRowAssistant]}>
                  {msg.role === 'assistant' && (
                    <View style={[s.avatarTiny, { backgroundColor: '#1E3A5F' }]}>
                      <Text style={s.avatarTinyEmoji}>🚗</Text>
                    </View>
                  )}
                  <View style={[
                    s.bubble,
                    msg.role === 'user'
                      ? [s.bubbleUser, { backgroundColor: c.accent }]
                      : [s.bubbleAssistant, { backgroundColor: c.card, borderColor: c.cardBorder }],
                  ]}>
                    <Text style={[s.bubbleText, { color: msg.role === 'user' ? '#fff' : c.text }]}>
                      {msg.content}
                    </Text>
                  </View>
                </View>

                {/* Feedback buttons — shown under every real assistant reply */}
                {msg.role === 'assistant' && !isWelcome && !loading && (
                  <View style={s.feedbackWrap}>
                    {fb === 'done' ? (
                      <Text style={s.feedbackThanks}>{t.feedbackThanks as string}</Text>
                    ) : fb === 'negative' ? (
                      <View style={s.feedbackReasons}>
                        {reasons.map((r, ri) => (
                          <TouchableOpacity
                            key={ri}
                            style={[s.feedbackReasonBtn, { borderColor: c.cardBorder }]}
                            onPress={() => sendFeedback(i, allMessages, false, r)}
                            activeOpacity={0.75}
                          >
                            <Text style={[s.feedbackReasonText, { color: c.text }]}>{r}</Text>
                          </TouchableOpacity>
                        ))}
                      </View>
                    ) : (
                      <View style={s.feedbackBtns}>
                        <Text style={[s.feedbackQ, { color: c.textMuted }]}>{t.feedbackQ as string}</Text>
                        <TouchableOpacity
                          style={[s.feedbackBtn, s.feedbackBtnYes]}
                          onPress={() => sendFeedback(i, allMessages, true)}
                          activeOpacity={0.8}
                        >
                          <Text style={s.feedbackBtnText}>{t.thumbsYes as string}</Text>
                        </TouchableOpacity>
                        <TouchableOpacity
                          style={[s.feedbackBtn, { borderColor: c.cardBorder }]}
                          onPress={() => setFeedbackMap((prev) => ({ ...prev, [i]: 'negative' }))}
                          activeOpacity={0.8}
                        >
                          <Text style={[s.feedbackBtnText, { color: c.text }]}>{t.thumbsNo as string}</Text>
                        </TouchableOpacity>
                      </View>
                    )}
                  </View>
                )}

                {/* Reply chips after last assistant message */}
                {msg.role === 'assistant' && msg.suggestions && msg.suggestions.length > 0 && i === allMessages.length - 1 && (
                  <View style={s.replyChipsWrap}>
                    <Text style={s.replyChipsHdr}>
                      {lang === 'th' ? '🚗 เลือกหัวข้อ:' : lang === 'en' ? '🚗 Choose topic:' : '🚗 Velg tema:'}
                    </Text>
                    {msg.suggestions.map((chip, ci) => (
                      <TouchableOpacity
                        key={ci}
                        style={s.replyChipBtn}
                        onPress={() => sendMessage(chip)}
                        activeOpacity={0.75}
                      >
                        <Text style={s.replyChipBtnText}>{chip}</Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                )}
              </React.Fragment>
            );
          })}

          {loading && (
            <View style={[s.bubbleRow, s.bubbleRowAssistant]}>
              <View style={[s.avatarTiny, { backgroundColor: '#1E3A5F' }]}>
                <Text style={s.avatarTinyEmoji}>🚗</Text>
              </View>
              <View style={[s.bubble, s.bubbleAssistant, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
                <ActivityIndicator size="small" color={c.accent} />
              </View>
            </View>
          )}

          {/* Fix 3: topics from backend API, shown only at start */}
          {showSuggestions && messages.length === 0 && topics.length > 0 && (
            <View style={s.suggestionsWrap}>
              {topics.map((topic, i) => (
                <TouchableOpacity
                  key={i}
                  style={[s.suggestBtn, { backgroundColor: c.card, borderColor: c.cardBorder }]}
                  onPress={() => sendMessage(`${topic.icon} ${topic.text}`)}
                  activeOpacity={0.75}
                >
                  <Text style={s.suggestIcon}>{topic.icon}</Text>
                  <Text style={[s.suggestText, { color: c.text }]}>{topic.text}</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </ScrollView>

        {/* Input bar */}
        <View style={[s.inputBar, { backgroundColor: c.card, borderTopColor: c.cardBorder }]}>
          <TextInput
            style={[s.input, { backgroundColor: c.bg, color: c.text, borderColor: c.cardBorder }]}
            placeholder={t.inputPlaceholder}
            placeholderTextColor={c.textMuted}
            value={input}
            onChangeText={setInput}
            multiline
            maxLength={1000}
            returnKeyType="send"
            onSubmitEditing={() => sendMessage(input)}
            blurOnSubmit={false}
          />
          <TouchableOpacity
            style={[s.sendBtn, { backgroundColor: input.trim() ? c.accent : c.cardBorder }]}
            onPress={() => sendMessage(input)}
            disabled={!input.trim() || loading}
            activeOpacity={0.8}
          >
            <Ionicons name="send" size={18} color="#fff" />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// ─── Styles ──────────────────────────────────────────────────────────────────
const s = StyleSheet.create({
  safe: { flex: 1 },

  // Header
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 12,
    paddingVertical: 12,
    borderBottomWidth: 1,
  },
  backBtn: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  headerCenter: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  headerTitle: { fontSize: 15, fontWeight: '700' },
  headerSub: { fontSize: 11, marginTop: 1 },
  avatarSmall: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarEmoji: { fontSize: 18 },

  // Message list
  messageList: { flex: 1 },
  messageListContent: { padding: 16, paddingBottom: 8, gap: 12 },

  // Bubble rows
  bubbleRow: { flexDirection: 'row', alignItems: 'flex-end', gap: 8, maxWidth: '100%' },
  bubbleRowUser: { justifyContent: 'flex-end' },
  bubbleRowAssistant: { justifyContent: 'flex-start' },

  // Avatar (tiny, beside assistant bubble)
  avatarTiny: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    flexShrink: 0,
  },
  avatarTinyEmoji: { fontSize: 14 },

  // Bubbles
  bubble: {
    maxWidth: '78%',
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  bubbleUser: { borderBottomRightRadius: 4 },
  bubbleAssistant: { borderWidth: 1, borderBottomLeftRadius: 4 },
  bubbleText: { fontSize: 14, lineHeight: 21 },

  // Reply chips (after assistant message)
  replyChipsWrap: { marginTop: 10, marginBottom: 4, gap: 8, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,.06)', paddingTop: 12 },
  replyChipsHdr: { fontSize: 11, fontWeight: '800', letterSpacing: 1, color: '#FF9933', textTransform: 'uppercase', marginBottom: 4 },
  replyChipBtn: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1a2744', borderWidth: 1, borderColor: 'rgba(59,130,246,.30)', borderRadius: 12, paddingHorizontal: 16, paddingVertical: 12 },
  replyChipBtnText: { fontSize: 14, fontWeight: '700', color: '#F8FAFC' },

  // Suggestion buttons
  suggestionsWrap: { marginTop: 16, gap: 8 },
  suggestBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1,
  },
  suggestIcon: { fontSize: 18 },
  suggestText: { fontSize: 14, fontWeight: '500', flex: 1 },

  // Feedback
  feedbackWrap: { marginLeft: 36, marginTop: 4, marginBottom: 2 },
  feedbackBtns: { flexDirection: 'row', alignItems: 'center', gap: 8, flexWrap: 'wrap' },
  feedbackQ: { fontSize: 11, marginRight: 4 },
  feedbackBtn: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, borderWidth: 1, borderColor: 'transparent' },
  feedbackBtnYes: { backgroundColor: '#10B981' },
  feedbackBtnText: { fontSize: 13, fontWeight: '600', color: '#fff' },
  feedbackThanks: { fontSize: 11, color: '#10B981' },
  feedbackReasons: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginTop: 2 },
  feedbackReasonBtn: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 12, borderWidth: 1 },
  feedbackReasonText: { fontSize: 12 },

  // Input bar
  inputBar: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 8,
    padding: 12,
    borderTopWidth: 1,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 14,
    maxHeight: 100,
    lineHeight: 20,
  },
  sendBtn: {
    width: 42,
    height: 42,
    borderRadius: 21,
    justifyContent: 'center',
    alignItems: 'center',
    flexShrink: 0,
  },
});
