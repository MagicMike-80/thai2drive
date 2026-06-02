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
const TR: Record<string, Record<string, string>> = {
  no: {
    title: '🚗 Michael Trafikklærer',       // Fix 5: consistent title
    inputPlaceholder: 'Still et spørsmål...',
    send: 'Send',
    errorMsg: 'Beklager, noe gikk galt. Prøv igjen.',
  },
  th: {
    title: '🚗 Michael Trafikklærer',
    inputPlaceholder: 'ถามคำถาม...',
    send: 'ส่ง',
    errorMsg: 'ขอโทษค่ะ มีข้อผิดพลาด กรุณาลองใหม่อีกครั้ง',
  },
  en: {
    title: '🚗 Michael Trafikklærer',
    inputPlaceholder: 'Ask a question...',
    send: 'Send',
    errorMsg: 'Sorry, something went wrong. Please try again.',
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
  const scrollRef = useRef<ScrollView>(null);

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
            <Text style={[s.headerSub, { color: '#10B981' }]}>● Online</Text>
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
          {allMessages.map((msg, i) => (
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
              {/* Fix 2: reply chips after last assistant message */}
              {msg.role === 'assistant' && msg.suggestions && msg.suggestions.length > 0 && i === allMessages.length - 1 && (
                <View style={s.replyChipsRow}>
                  {msg.suggestions.map((chip, ci) => (
                    <TouchableOpacity
                      key={ci}
                      style={[s.replyChip, { borderColor: 'rgba(59,130,246,.35)' }]}
                      onPress={() => sendMessage(chip)}
                      activeOpacity={0.75}
                    >
                      <Text style={s.replyChipText}>{chip}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              )}
            </React.Fragment>
          ))}

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
  replyChipsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 7, paddingLeft: 36, paddingTop: 4, paddingBottom: 2 },
  replyChip: { borderWidth: 1, borderRadius: 20, paddingHorizontal: 12, paddingVertical: 6, backgroundColor: 'rgba(59,130,246,.10)' },
  replyChipText: { fontSize: 12, fontWeight: '600', color: '#93C5FD' },

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
