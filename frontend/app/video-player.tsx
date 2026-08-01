import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  ActivityIndicator, Dimensions, Image, Pressable, ScrollView,
  StyleSheet, Text, TouchableOpacity, View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Video, Audio, AVPlaybackStatus, ResizeMode } from 'expo-av';
import { LinearGradient } from 'expo-linear-gradient';
import { useAppStore } from '../src/store/appStore';
import { api, BACKEND_URL } from '../src/services/api';

const { width: SCREEN_W } = Dimensions.get('window');
const VIDEO_H = Math.round(SCREEN_W * 9 / 16) + 60;
const CARD_W = SCREEN_W - 48;

interface KnowledgeMoment {
  timestamp: number;
  label: string;
  imageUrl: string;
  color: string;
}

const CARD_COLORS = ['#00F5FF', '#FF007F', '#7000FF', '#AAFF00', '#FF6A00', '#CC44FF'];

// Backend gir video/thumb som relativ sti (/api/assets/...) — native trenger absolutt URL.
const assetUri = (path: string) => (path.startsWith('/') ? `${BACKEND_URL}${path}` : path);

const TR: Record<string, Record<string, string>> = {
  no: { loading: 'Laster...', checkTitle: 'Lite spørsmål', optionA: 'Ja', optionB: 'Nei', correctMsg: 'Riktig! 🎉', wrongMsg: 'Nesten! Michael forklarer...', nextVideo: 'Neste video', close: 'Lukk', notFound: 'Video ikke funnet', explains: 'Michael forklarer...' },
  th: { loading: 'กำลังโหลด...', checkTitle: 'คำถามเล็กน้อย', optionA: 'ใช่', optionB: 'ไม่ใช่', correctMsg: 'ถูกต้อง! 🎉', wrongMsg: 'เกือบแล้ว! ไมเคิลอธิบาย...', nextVideo: 'วิดีโอถัดไป', close: 'ปิด', notFound: 'ไม่พบวิดีโอ', explains: 'ไมเคิลอธิบาย...' },
  en: { loading: 'Loading...', checkTitle: 'Quick check', optionA: 'Yes', optionB: 'No', correctMsg: 'Correct! 🎉', wrongMsg: 'Almost! Michael explains...', nextVideo: 'Next video', close: 'Close', notFound: 'Video not found', explains: 'Michael explains...' },
};

export default function VideoPlayerScreen() {
  const router = useRouter();
  const { id, videoId } = useLocalSearchParams<{ id: string; videoId: string }>();
  const vidRef = useRef<Video>(null);
  const { language, colors: c } = useAppStore();
  const t = TR[language] || {};

  const [video, setVideo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [position, setPosition] = useState(0);
  const [duration, setDuration] = useState(120);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showCard, setShowCard] = useState<string | null>(null);
  const [passedIndices, setPassedIndices] = useState<number[]>([]);
  const [quizMode, setQuizMode] = useState(false);
  const [quizResult, setQuizResult] = useState<'correct' | 'wrong' | null>(null);

  const effectiveId = id || videoId;

  useEffect(() => {
    if (!effectiveId) return;
    api.getLearningVideos().then(vids => {
      const found = vids.find((v: any) => (v._id || v.id) === effectiveId);
      if (found) setVideo(found);
    }).catch(console.error).finally(() => setLoading(false));
    Audio.setAudioModeAsync({ playsInSilentModeIOS: true });
  }, [effectiveId]);

  const moments: KnowledgeMoment[] = video?.topic_tags?.length
    ? video.topic_tags.map((tag: string, i: number) => ({
        timestamp: ((i + 1) / (video.topic_tags.length + 1)) * duration,
        label: tag,
        imageUrl: video.thumbnail_url || '',
        color: CARD_COLORS[i % CARD_COLORS.length],
      }))
    : [];

  const videoUrl = video?.file_path ? assetUri(video.file_path) : '';

  const onPlaybackUpdate = useCallback((status: AVPlaybackStatus) => {
    if (!status.isLoaded) return;
    setPosition(status.positionMillis / 1000);
    setDuration(status.durationMillis ? status.durationMillis / 1000 : duration);
    setIsPlaying(status.isPlaying);

    if (status.didJustFinish) {
      setIsPlaying(false);
      setQuizMode(true);
    }
  }, [duration]);

  // Check for knowledge moments
  useEffect(() => {
    if (quizMode || moments.length === 0) return;
    moments.forEach((m, i) => {
      if (position >= m.timestamp - 0.5 && !passedIndices.includes(i)) {
        setShowCard(m.label);
        setPassedIndices(p => [...p, i]);
        setTimeout(() => setShowCard(null), 5000);
      }
    });
  }, [position, moments, passedIndices, quizMode]);

  const handleQuizAnswer = (answer: 'correct' | 'wrong') => {
    setQuizResult(answer);
  };

  if (loading) {
    return (
      <SafeAreaView style={[s.root, { backgroundColor: c.bg }]}>
        <View style={s.center}><ActivityIndicator size="large" color={c.accent} /></View>
      </SafeAreaView>
    );
  }

  if (!video) {
    return (
      <SafeAreaView style={[s.root, { backgroundColor: c.bg }]}>
        <View style={s.center}><Text style={{ color: c.textMuted }}>{t.notFound}</Text></View>
      </SafeAreaView>
    );
  }

  const progress = duration > 0 ? position / duration : 0;
  // Språkrenhet: kun aktivt språk — aldri lån tittel fra et annet språk.
  const title = language === 'th' ? (video.title_th || '')
    : language === 'en' ? (video.title_en || '')
    : (video.title_no || '');

  return (
    <SafeAreaView style={[s.root, { backgroundColor: '#000' }]}>
      {/* ── Header ── */}
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}>
          <Ionicons name="chevron-down" size={22} color="#fff" />
        </TouchableOpacity>
        <Text style={s.headerTitle} numberOfLines={1}>{title}</Text>
        <TouchableOpacity style={s.backBtn}>
          <Ionicons name="ellipsis-vertical" size={18} color="#fff" />
        </TouchableOpacity>
      </View>

      {/* ── Video Player ── */}
      <View style={s.videoWrap}>
        <Video
          ref={vidRef}
          source={{ uri: videoUrl }}
          style={s.video}
          resizeMode={ResizeMode.CONTAIN}
          isLooping={false}
          shouldPlay={false}
          useNativeControls
          onPlaybackStatusUpdate={onPlaybackUpdate}
        />

        {/* Knowledge Card pop-up */}
        {showCard && !quizMode && (
          <View style={s.kcWrap} pointerEvents="none">
            <LinearGradient
              colors={['rgba(13,14,21,0.92)', 'rgba(13,14,21,0.98)']}
              style={s.kcCard}
            >
              <View style={[s.kcAccent, { backgroundColor: moments.find(m => m.label === showCard)?.color || '#00F5FF' }]} />
              {video.thumbnail_url && (
                <Image source={{ uri: assetUri(video.thumbnail_url) }} style={s.kcImage} />
              )}
              <View style={s.kcText}>
                <Text style={s.kcLabel}>{showCard}</Text>
                <Text style={s.kcHint}>{t.explains}</Text>
              </View>
            </LinearGradient>
          </View>
        )}
      </View>

      {/* ── Glow Road timeline ── */}
      {!quizMode && (
        <View style={s.roadWrap}>
          <View style={[s.roadTrack, { backgroundColor: 'rgba(255,255,255,0.1)' }]}>
            <View style={[s.roadFill, { width: `${progress * 100}%`, backgroundColor: '#00F5FF' }]} />
            {moments.map((m, i) => {
              const pct = duration > 0 ? (m.timestamp / duration) * 100 : 0;
              const isPast = passedIndices.includes(i);
              return (
                <View
                  key={i}
                  style={[
                    s.roadDot,
                    {
                      left: `${pct}%`,
                      backgroundColor: isPast ? m.color : 'rgba(255,255,255,0.25)',
                      shadowColor: isPast ? m.color : 'transparent',
                    },
                  ]}
                />
              );
            })}
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.roadLabels}>
            {moments.map((m, i) => (
              <Text key={i} style={[s.roadLabel, { color: passedIndices.includes(i) ? m.color : 'rgba(255,255,255,0.3)' }]}>
                {m.label}
              </Text>
            ))}
          </ScrollView>
        </View>
      )}

      {/* ── Mini-check overlay ── */}
      {quizMode && (
        <View style={s.quizOverlay}>
          <LinearGradient
            colors={['rgba(13,14,21,0.95)', 'rgba(13,14,21,0.99)']}
            style={StyleSheet.absoluteFill}
          />
          <View style={s.quizContent}>
            <Ionicons name="help-circle" size={40} color="#00F5FF" />
            <Text style={s.quizTitle}>{t.checkTitle}</Text>
            <Text style={s.quizQuestion}>
              {language === 'th' ? 'คุณเข้าใจเนื้อหานี้หรือไม่?'
               : language === 'en' ? 'Did you understand this topic?'
               : 'Forsto du dette temaet?'}
            </Text>
            {!quizResult ? (
              <View style={s.quizBtns}>
                <TouchableOpacity style={[s.quizBtn, { backgroundColor: '#10B981' }]} onPress={() => handleQuizAnswer('correct')}>
                  <Text style={s.quizBtnText}>{t.optionA} 👍</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[s.quizBtn, { backgroundColor: '#EF4444' }]} onPress={() => handleQuizAnswer('wrong')}>
                  <Text style={s.quizBtnText}>{t.optionB} 🤔</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <View style={s.quizResultWrap}>
                <Text style={[s.quizResultText, { color: quizResult === 'correct' ? '#10B981' : '#EF4444' }]}>
                  {quizResult === 'correct' ? t.correctMsg : t.wrongMsg}
                </Text>
                <TouchableOpacity
                  style={[s.nextBtn, { backgroundColor: c.accent }]}
                  onPress={() => router.back()}
                >
                  <Text style={s.nextBtnText}>{t.close}</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>
      )}
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#000' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },

  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 12, paddingVertical: 8, zIndex: 10,
  },
  backBtn: { width: 36, height: 36, borderRadius: 18, alignItems: 'center', justifyContent: 'center' },
  headerTitle: { flex: 1, fontSize: 15, fontWeight: '600', color: '#fff', textAlign: 'center', marginHorizontal: 8 },

  videoWrap: { position: 'relative', width: SCREEN_W, height: VIDEO_H },
  video: { width: '100%', height: '100%' },

  // Knowledge Card
  kcWrap: {
    position: 'absolute', bottom: 16, left: 24, right: 24, zIndex: 20,
  },
  kcCard: {
    flexDirection: 'row', borderRadius: 16, overflow: 'hidden',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
    minHeight: 70, alignItems: 'center',
  },
  kcAccent: { width: 4, alignSelf: 'stretch' },
  kcImage: { width: 56, height: 56, borderRadius: 8, margin: 10 },
  kcText: { flex: 1, paddingRight: 12 },
  kcLabel: { fontSize: 14, fontWeight: '600', color: '#fff' },
  kcHint: { fontSize: 12, color: 'rgba(255,255,255,0.5)', marginTop: 3 },

  // Glow Road
  roadWrap: { paddingHorizontal: 24, paddingTop: 16, paddingBottom: 24 },
  roadTrack: { height: 3, borderRadius: 2, position: 'relative', overflow: 'visible' },
  roadFill: { height: '100%', borderRadius: 2 },
  roadDot: {
    position: 'absolute', top: -4, width: 11, height: 11, borderRadius: 6,
    marginLeft: -5.5, shadowOffset: { width: 0, height: 0 }, shadowOpacity: 0.8, shadowRadius: 6, elevation: 4,
  },
  roadLabels: { marginTop: 10 },
  roadLabel: { fontSize: 11, fontWeight: '500', marginRight: 16 },

  // Mini-check
  quizOverlay: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, zIndex: 30, justifyContent: 'center', alignItems: 'center' },
  quizContent: { alignItems: 'center', padding: 32, gap: 12 },
  quizTitle: { fontSize: 20, fontWeight: '700', color: '#fff' },
  quizQuestion: { fontSize: 15, color: 'rgba(255,255,255,0.7)', textAlign: 'center', marginBottom: 16 },
  quizBtns: { flexDirection: 'row', gap: 16 },
  quizBtn: { paddingHorizontal: 32, paddingVertical: 14, borderRadius: 12 },
  quizBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  quizResultWrap: { alignItems: 'center', gap: 16 },
  quizResultText: { fontSize: 18, fontWeight: '700', textAlign: 'center' },
  nextBtn: { paddingHorizontal: 28, paddingVertical: 12, borderRadius: 10 },
  nextBtnText: { color: '#fff', fontWeight: '700', fontSize: 15 },
});
