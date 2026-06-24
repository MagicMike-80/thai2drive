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
  Linking,
  Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import { useAppStore } from '../src/store/appStore';
import { BottomNavBar } from '../src/components/BottomNavBar';

// ─── Translation strings ─────────────────────────────────────────────────────
const TR: Record<string, Record<string, any>> = {
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
    readAloud: 'Les høyt',
    categories: {
      'Traffic Signs': 'Trafikkskilt', 'Road Rules': 'Trafikkregler', 'Right of Way': 'Vikeplikt',
      'Speed Limits': 'Fartsgrenser', 'Safety': 'Sikkerhet', 'Driving Conditions': 'Kjøreforhold',
      'Situations': 'Situasjoner', 'Traffic Rules': 'Grunnregler', 'Road Conditions': 'Veiforhold',
    },
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
    readAloud: 'อ่านออกเสียง',
    categories: {
      'Traffic Signs': 'ป้ายจราจร', 'Road Rules': 'กฎจราจร', 'Right of Way': 'การให้ทาง',
      'Speed Limits': 'ขีดจำกัดความเร็ว', 'Safety': 'ความปลอดภัย', 'Driving Conditions': 'สภาพการขับขี่',
      'Situations': 'สถานการณ์', 'Traffic Rules': 'กฎพื้นฐาน', 'Road Conditions': 'สภาพถนน',
    },
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
    readAloud: 'Read aloud',
    categories: {
      'Traffic Signs': 'Traffic Signs', 'Road Rules': 'Road Rules', 'Right of Way': 'Right of Way',
      'Speed Limits': 'Speed Limits', 'Safety': 'Safety', 'Driving Conditions': 'Driving Conditions',
      'Situations': 'Situations', 'Traffic Rules': 'Traffic Rules', 'Road Conditions': 'Road Conditions',
    },
  },
};

// ─── Types ───────────────────────────────────────────────────────────────────
interface Message {
  role: 'user' | 'assistant';
  content: string;
  suggestions?: string[];
}

interface Topic { icon: string; text: string; }

interface LangSession {
  sessionId: string | null;
  messages: Message[];
  showSuggestions: boolean;
  feedbackMap: Record<number, 'pending' | 'negative' | 'done'>;
}
const emptySession = (): LangSession => ({
  sessionId: null, messages: [], showSuggestions: true, feedbackMap: {},
});

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

const getFullUrl = (url: string) => url.startsWith('/') ? BACKEND_URL + url : url;

// ─── Visual Cards for V5 ──────────────────────────────────────────────────────
function VideoCard({ youtubeUrl, title, colors }: { youtubeUrl: string; title: string; colors: any }) {
  const handleOpen = () => {
    Linking.openURL(youtubeUrl).catch((err) => console.error("Error opening URL", err));
  };

  return (
    <TouchableOpacity
      style={[s.videoCard, { backgroundColor: colors.card, borderColor: colors.cardBorder }]}
      onPress={handleOpen}
      activeOpacity={0.8}
    >
      <View style={s.videoThumbnailPlaceholder}>
        <Ionicons name="play-circle" size={40} color="#EF4444" />
      </View>
      <View style={{ flex: 1, paddingVertical: 8 }}>
        <Text style={s.videoLabel}>VIDEOFORKLARING</Text>
        <Text style={[s.videoTitle, { color: colors.text }]} numberOfLines={2}>{title}</Text>
      </View>
    </TouchableOpacity>
  );
}

function PodcastCard({ audioUrl, title, colors }: { audioUrl: string; title: string; colors: any }) {
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    return () => {
      if (sound) {
        sound.unloadAsync();
      }
    };
  }, [sound]);

  const togglePlayback = async () => {
    if (loading) return;

    if (sound) {
      if (isPlaying) {
        await sound.pauseAsync();
        setIsPlaying(false);
      } else {
        await sound.playAsync();
        setIsPlaying(true);
      }
    } else {
      setLoading(true);
      try {
        const { sound: newSound } = await Audio.Sound.createAsync(
          { uri: getFullUrl(audioUrl) },
          { shouldPlay: true }
        );
        setSound(newSound);
        setIsPlaying(true);
        newSound.setOnPlaybackStatusUpdate((status) => {
          if (status.isLoaded) {
            setIsPlaying(status.isPlaying);
            if (status.didJustFinish) {
              setIsPlaying(false);
              newSound.setPositionAsync(0);
            }
          }
        });
      } catch (error) {
        console.error("Error loading sound", error);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <View style={[s.podcastCard, { backgroundColor: colors.card, borderColor: colors.cardBorder }]}>
      <View style={{ flex: 1 }}>
        <Text style={s.podcastLabel}>PODCAST</Text>
        <Text style={[s.podcastTitle, { color: colors.text }]}>{title}</Text>
      </View>
      <TouchableOpacity
        style={[s.podcastPlayBtn, { backgroundColor: colors.accent }]}
        onPress={togglePlayback}
        activeOpacity={0.8}
      >
        {loading ? (
          <ActivityIndicator size="small" color="#fff" />
        ) : (
          <Ionicons name={isPlaying ? "pause" : "play"} size={20} color="#fff" />
        )}
      </TouchableOpacity>
    </View>
  );
}

function ImageCard({ imageUrl, caption, colors }: { imageUrl: string; caption: string; colors: any }) {
  return (
    <View style={[s.imageCard, { backgroundColor: colors.card, borderColor: colors.cardBorder }]}>
      <Image
        source={{ uri: getFullUrl(imageUrl) }}
        style={s.imageContent}
        resizeMode="contain"
      />
      {caption ? (
        <Text style={[s.imageCaption, { color: colors.textMuted }]}>{caption}</Text>
      ) : null}
    </View>
  );
}

function MessageContent({ text, lang, colors }: { text: string; lang: string; colors: any }) {
  // Clean markdown syntax to raw text for display
  const clean = text
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/__(.+?)__/g, '$1')
    .replace(/\*([^*\n]+?)\*/g, '$1')
    .replace(/_([^_\n]+?)_/g, '$1')
    .replace(/^[-*]{3,}$/gm, '')
    .replace(/^[\-\*]\s+/gm, '• ')
    .replace(/`([^`]+)`/g, '$1')
    .trim();

  const blocks = clean.split(/\n{2,}/);

  return (
    <View style={{ gap: 8 }}>
      {blocks.map((block, idx) => {
        const trimmed = block.trim();
        if (!trimmed) return null;

        // Video tag match: [video: url | title_no | title_th | title_en]
        const vidMatch = trimmed.match(/^\[video:\s*([^\|\]]+)(?:\|\s*([^\|\]]+))?(?:\|\s*([^\|\]]+))?(?:\|\s*([^\]]+))?\]$/i);
        if (vidMatch) {
          const url = vidMatch[1].trim();
          const titleNo = (vidMatch[2] || '').trim();
          const titleTh = (vidMatch[3] || '').trim();
          const titleEn = (vidMatch[4] || '').trim();
          const title = lang === 'th' ? titleTh : lang === 'en' ? titleEn : titleNo;
          return <VideoCard key={idx} youtubeUrl={url} title={title || 'Video'} colors={colors} />;
        }

        // Podcast tag match: [podcast: url | title_no | title_th | title_en]
        const podMatch = trimmed.match(/^\[podcast:\s*([^\|\]]+)(?:\|\s*([^\|\]]+))?(?:\|\s*([^\|\]]+))?(?:\|\s*([^\]]+))?\]$/i);
        if (podMatch) {
          const url = podMatch[1].trim();
          const titleNo = (podMatch[2] || '').trim();
          const titleTh = (podMatch[3] || '').trim();
          const titleEn = (podMatch[4] || '').trim();
          const title = lang === 'th' ? titleTh : lang === 'en' ? titleEn : titleNo;
          return <PodcastCard key={idx} audioUrl={url} title={title || 'Podcast'} colors={colors} />;
        }

        // Image tag match: [image: url | caption_no | caption_th | caption_en]
        const imgMatch = trimmed.match(/^\[image:\s*([^\|\]]+)(?:\|\s*([^\|\]]+))?(?:\|\s*([^\|\]]+))?(?:\|\s*([^\]]+))?\]$/i);
        if (imgMatch) {
          const url = imgMatch[1].trim();
          const capNo = (imgMatch[2] || '').trim();
          const capTh = (imgMatch[3] || '').trim();
          const capEn = (imgMatch[4] || '').trim();
          const caption = lang === 'th' ? capTh : lang === 'en' ? capEn : capNo;
          return <ImageCard key={idx} imageUrl={url} caption={caption} colors={colors} />;
        }

        // Advice box: block starts with advice header (🚗 Praktisk råd: / 🚗 คำแนะนำ: / 🚗 Practical tip:)
        if (/^🚗\s*(Praktisk råd|คำแนะนำ|Practical tip)/i.test(trimmed)) {
          const lines = trimmed.split('\n');
          const header = lines[0].trim();
          const bodyLines = lines.slice(1).map(l => l.trim()).filter(Boolean);
          return (
            <View key={idx} style={[s.adviceBox, { borderColor: colors.accent + '44', backgroundColor: colors.accent + '11' }]}>
              <Text style={[s.adviceHdr, { color: colors.accent }]}>{header}</Text>
              {bodyLines.map((line, lidx) => (
                <Text key={lidx} style={[s.adviceLine, { color: colors.text }]}>{line}</Text>
              ))}
            </View>
          );
        }

        // Section header: single short line ending with ":"
        const isSingleLine = trimmed.indexOf('\n') === -1;
        if (isSingleLine && trimmed.endsWith(':') && trimmed.length < 40) {
          return (
            <Text key={idx} style={[s.sectionHdr, { color: colors.accent }]}>
              {trimmed}
            </Text>
          );
        }

        // Regular paragraph
        return (
          <Text key={idx} style={[s.bubbleText, { color: colors.text }]}>
            {trimmed}
          </Text>
        );
      })}
    </View>
  );
}

// ─── Component ───────────────────────────────────────────────────────────────
export default function TeacherScreen() {
  const router = useRouter();
  const { language, colors, deviceId } = useAppStore();
  const c = colors;
  const t = TR[language] || TR.no;
  const lang = language || 'no';

  // Per-language session state — each language keeps its own chat history
  const [sessions, setSessions] = useState<Record<string, LangSession>>({
    no: emptySession(), th: emptySession(), en: emptySession(),
  });
  const [welcomeMsg, setWelcomeMsg] = useState<string>('');
  const [topics, setTopics] = useState<Topic[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<ScrollView>(null);

  // Derive current language's session
  const sess = sessions[lang] ?? emptySession();
  const { messages, sessionId, showSuggestions, feedbackMap } = sess;

  const updSess = useCallback((fn: (s: LangSession) => LangSession) => {
    setSessions(prev => ({ ...prev, [lang]: fn(prev[lang] ?? emptySession()) }));
  }, [lang]);

  const [speakingIndex, setSpeakingIndex] = useState<number | null>(null);
  const teacherSoundRef = useRef<Audio.Sound | null>(null);

  const stopTts = async () => {
    setSpeakingIndex(null);
    if (teacherSoundRef.current) {
      try {
        await teacherSoundRef.current.stopAsync();
        await teacherSoundRef.current.unloadAsync();
      } catch {}
      teacherSoundRef.current = null;
    }
  };

  const handleSpeak = useCallback(async (text: string, msgIndex: number) => {
    const cleanText = text
      .replace(/\[(video|audio|podcast|image|url):[^\]]+\]/gi, '')
      .replace(/[🛑🚗💡⚠️📝❓✨😊]/g, '')
      .trim();
    if (!cleanText) return;

    if (speakingIndex === msgIndex) {
      await stopTts();
      return;
    }
    
    await stopTts();
    setSpeakingIndex(msgIndex);

    try {
      const targetLang = lang === 'th' ? 'th-TH' : lang === 'no' ? 'nb-NO' : 'en-US';
      const url = `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/tts?lang=${targetLang}&text=${encodeURIComponent(cleanText)}`;
      
      const { sound } = await Audio.Sound.createAsync(
        { uri: url },
        { shouldPlay: true }
      );
      
      teacherSoundRef.current = sound;
      
      sound.setOnPlaybackStatusUpdate((status: any) => {
        if (status.isLoaded && status.didJustFinish) {
          setSpeakingIndex(null);
          sound.unloadAsync();
        }
      });
    } catch (e) {
      console.warn('[Teacher TTS] playback failed', e);
      setSpeakingIndex(null);
    }
  }, [speakingIndex, lang]);

  // Cancel speech on language switch or screen unmount
  React.useEffect(() => {
    return () => {
      stopTts();
    };
  }, [lang]);

  const sendFeedback = useCallback(async (
    msgIndex: number,
    allMsgs: Message[],
    helpful: boolean,
    reason?: string,
  ) => {
    updSess(s => ({ ...s, feedbackMap: { ...s.feedbackMap, [msgIndex]: 'done' } }));
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
    } catch { /* fire-and-forget */ }
  }, [updSess, sessionId, lang]);

  // Fetch welcome + topics on language change
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
      } catch {}
    })();
  }, [lang]);

  const allMessages: Message[] = welcomeMsg
    ? [{ role: 'assistant', content: welcomeMsg }, ...messages]
    : messages;

  const sendMessage = useCallback(async (text: string) => {
    const msg = text.trim();
    if (!msg || loading) return;

    setInput('');
    setLoading(true);

    // Read sessionId and add user message atomically
    let capturedSessionId: string | null = null;
    setSessions(prev => {
      const s = prev[lang] ?? emptySession();
      capturedSessionId = s.sessionId;
      return {
        ...prev,
        [lang]: { ...s, showSuggestions: false, messages: [...s.messages, { role: 'user', content: msg }] },
      };
    });

    setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);

    // Check if the message is asking about weak topics
    const cleanMsg = msg.replace(/^[\S]{1,2}\s+/, '').trim().toLowerCase();
    const isWeakTopic = (
      cleanMsg === 'hva bør jeg øve på?' || cleanMsg === 'hva bør jeg øve på' ||
      cleanMsg === 'ฉันควรฝึกเรื่องอะไร?' || cleanMsg === 'ฉันควรฝึกเรื่องอะไร' ||
      cleanMsg === 'what should i practise?' || cleanMsg === 'what should i practise' ||
      cleanMsg === 'what should i practice?' || cleanMsg === 'what should i practice'
    );

    let payloadMsg = msg;
    if (isWeakTopic) {
      let statsText = "No quiz attempts recorded yet.";
      if (deviceId) {
        try {
          const statsRes = await fetch(`${BACKEND_URL}/api/stats/me?device_id=${encodeURIComponent(deviceId)}`);
          if (statsRes.ok) {
            const stats = await statsRes.json();
            if (stats && stats.overall && stats.overall.total_q > 0) {
              const lines = [];
              lines.push(`Overall Accuracy: ${Math.round(stats.overall.pct)}% (${stats.overall.total_correct}/${stats.overall.total_q} correct across ${stats.overall.attempts} attempts)`);
              lines.push("\nAccuracy by category (sorted from lowest to highest):");
              if (Array.isArray(stats.by_category)) {
                stats.by_category.forEach((c: any) => {
                  const catMap = t.categories || {};
                  const catDisplayName = catMap[c.category] || c.category;
                  lines.push(`- ${catDisplayName} (${c.category}): ${Math.round(c.pct)}% accuracy (${c.total_correct}/${c.total_q} correct, ${c.attempts} attempts)`);
                });
              }
              statsText = lines.join("\n");
            }
          }
        } catch (e) {
          console.error("Failed to fetch stats for Michael context in mobile app:", e);
        }
      }
      payloadMsg = msg + '\n\n'
        + '<stats_context>\n'
        + 'STUDENT QUIZ PERFORMANCE AND STATISTICS:\n'
        + statsText + '\n'
        + '</stats_context>';
    }

    try {
      const res = await fetch(`${BACKEND_URL}/api/teacher/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: capturedSessionId, message: payloadMsg, language: lang }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      setSessions(prev => {
        const s = prev[lang] ?? emptySession();
        return {
          ...prev,
          [lang]: {
            ...s,
            sessionId: s.sessionId || data.session_id || null,
            messages: [...s.messages, {
              role: 'assistant' as const,
              content: data.reply,
              suggestions: data.suggestions || [],
            }],
          },
        };
      });
    } catch {
      setSessions(prev => {
        const s = prev[lang] ?? emptySession();
        return {
          ...prev,
          [lang]: { ...s, messages: [...s.messages, { role: 'assistant' as const, content: t.errorMsg as string }] },
        };
      });
    } finally {
      setLoading(false);
      setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 150);
    }
  }, [loading, lang, t, deviceId]);

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
                    {msg.role === 'user' ? (
                      <Text style={[s.bubbleText, { color: '#fff' }]}>
                        {msg.content}
                      </Text>
                    ) : (
                      <MessageContent text={msg.content} lang={lang} colors={c} />
                    )}
                  </View>
                  {msg.role === 'assistant' && (
                    <TouchableOpacity
                      style={s.speakBtn}
                      onPress={() => handleSpeak(msg.content, i)}
                      activeOpacity={0.7}
                      accessibilityLabel={t.readAloud as string}
                    >
                      <Ionicons
                        name={speakingIndex === i ? 'stop-circle' : 'volume-high'}
                        size={16}
                        color={speakingIndex === i ? '#EF4444' : '#6B7280'}
                      />
                    </TouchableOpacity>
                  )}
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
                          onPress={() => updSess(s => ({ ...s, feedbackMap: { ...s.feedbackMap, [i]: 'negative' } }))}
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
        <View style={[s.inputBar, { backgroundColor: c.card, borderTopColor: c.cardBorder, marginBottom: 88 }]}>
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
      <BottomNavBar activeTab="teacher" />
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

  // Speak button
  speakBtn: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'flex-end',
    marginBottom: 2,
  },

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

  // Video Card
  videoCard: {
    flexDirection: 'row',
    borderRadius: 14,
    borderWidth: 1,
    overflow: 'hidden',
    marginTop: 8,
    marginBottom: 4,
    height: 90,
  },
  videoThumbnailPlaceholder: {
    width: 90,
    height: '100%',
    backgroundColor: '#1E293B',
    justifyContent: 'center',
    alignItems: 'center',
    borderRightWidth: 1,
    borderRightColor: 'rgba(255,255,255,.05)',
  },
  videoLabel: {
    fontSize: 9,
    fontWeight: '800',
    color: '#EF4444',
    letterSpacing: 1,
    marginBottom: 4,
    paddingHorizontal: 12,
  },
  videoTitle: {
    fontSize: 13,
    fontWeight: '600',
    paddingHorizontal: 12,
    lineHeight: 18,
  },

  // Podcast Card
  podcastCard: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 14,
    borderWidth: 1,
    padding: 12,
    marginTop: 8,
    marginBottom: 4,
    gap: 12,
  },
  podcastLabel: {
    fontSize: 9,
    fontWeight: '800',
    color: '#8B5CF6',
    letterSpacing: 1,
    marginBottom: 4,
  },
  podcastTitle: {
    fontSize: 13,
    fontWeight: '600',
    lineHeight: 18,
  },
  podcastPlayBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },

  // Image Card
  imageCard: {
    borderRadius: 14,
    borderWidth: 1,
    padding: 8,
    marginTop: 8,
    marginBottom: 4,
    overflow: 'hidden',
    alignItems: 'center',
  },
  imageContent: {
    width: '100%',
    height: 180,
    borderRadius: 8,
  },
  imageCaption: {
    fontSize: 11,
    marginTop: 6,
    textAlign: 'center',
    lineHeight: 15,
  },

  // Advice Box
  adviceBox: {
    borderRadius: 14,
    borderWidth: 1,
    padding: 12,
    marginVertical: 6,
  },
  adviceHdr: {
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 6,
  },
  adviceLine: {
    fontSize: 13,
    lineHeight: 18,
    marginBottom: 2,
  },

  // Section Header
  sectionHdr: {
    fontSize: 14,
    fontWeight: '700',
    marginTop: 10,
    marginBottom: 4,
  },
});
