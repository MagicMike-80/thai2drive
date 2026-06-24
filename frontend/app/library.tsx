import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  SafeAreaView,
  Linking,
  Animated,
  Platform,
  Modal,
  Dimensions,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import { LinearGradient } from 'expo-linear-gradient';
import { WebView } from 'react-native-webview';
import { useAppStore } from '../src/store/appStore';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';
const getFullUrl = (url: string) => url.startsWith('/') ? BACKEND_URL + url : url;

const LANG_FLAG: Record<string, string> = { no: '🇳🇴', th: '🇹🇭', en: '🇬🇧' };

const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Innholdsbibliotek',
    subtitle: 'Ryggraden for repetisjon',
    videos: 'Videoer',
    podcasts: 'Podcaster',
    all: 'Alle',
    loading: 'Laster...',
    empty: 'Ingen innhold tilgjengelig.',
    premiumLock: 'Premium',
    premiumCta: 'Lås opp alt innhold',
    new: 'NY',
    recommended: 'Michael anbefaler',
    minutes: 'min',
    studyBook: 'Studiebok',
    signs: 'Trafikkskilt',
    bookmarks: 'Bokmerker',
    history: 'Historikk',
    media: 'Anbefalt Multimedia',
  },
  th: {
    title: 'ห้องสมุดเนื้อหา',
    subtitle: 'ศูนย์กลางการทบทวน',
    videos: 'วิดีโอ',
    podcasts: 'พอดแคสต์',
    all: 'ทั้งหมด',
    loading: 'กำลังโหลด...',
    empty: 'ไม่มีเนื้อหาที่ใช้ได้',
    premiumLock: 'พี่เมียม',
    premiumCta: 'ปลดล็อกเนื้อหาทั้งหมด',
    new: 'ใหม่',
    recommended: 'ไมเคิลแนะนำ',
    minutes: 'นาที',
    studyBook: 'หนังสือเรียน',
    signs: 'ป้ายจราจร',
    bookmarks: 'บุ๊กมาร์ก',
    history: 'ประวัติ',
    media: 'มัลติมีเดียที่แนะนำ',
  },
  en: {
    title: 'Content Library',
    subtitle: 'The backbone of repetition',
    videos: 'Videos',
    podcasts: 'Podcasts',
    all: 'All',
    loading: 'Loading...',
    empty: 'No content available.',
    premiumLock: 'Premium',
    premiumCta: 'Unlock all content',
    new: 'NEW',
    recommended: 'Michael recommends',
    minutes: 'min',
    studyBook: 'Study Book',
    signs: 'Traffic Signs',
    bookmarks: 'Bookmarks',
    history: 'History',
    media: 'Recommended Media',
  },
};

interface VideoItem {
  id: string;
  youtube_url: string;
  title_no: string; title_th: string; title_en: string;
  topic_tags: string[];
  instructor_summary_no?: string; instructor_summary_th?: string; instructor_summary_en?: string;
  language?: string;
}

interface PodcastItem {
  id: string;
  file_path: string;
  title_no: string; title_th: string; title_en: string;
  topic_tags: string[];
  instructor_summary_no?: string; instructor_summary_th?: string; instructor_summary_en?: string;
  duration_seconds?: number;
  language?: string;
}

// ─── Pulsing waveform bars (decorative, plays animation when active) ──────────
function WaveIcon({ active, color }: { active: boolean; color: string }) {
  const anims = useRef([
    new Animated.Value(0.3),
    new Animated.Value(0.6),
    new Animated.Value(0.4),
    new Animated.Value(0.8),
    new Animated.Value(0.5),
  ]).current;

  useEffect(() => {
    if (!active) {
      anims.forEach(a => Animated.spring(a, { toValue: 0.3, useNativeDriver: false }).start());
      return;
    }
    const loops = anims.map((a, i) =>
      Animated.loop(
        Animated.sequence([
          Animated.timing(a, { toValue: 0.2 + Math.random() * 0.8, duration: 200 + i * 80, useNativeDriver: false }),
          Animated.timing(a, { toValue: 0.2 + Math.random() * 0.5, duration: 200 + i * 60, useNativeDriver: false }),
        ])
      )
    );
    loops.forEach(l => l.start());
    return () => loops.forEach(l => l.stop());
  }, [active]);

  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', height: 20, gap: 2 }}>
      {anims.map((anim, i) => (
        <Animated.View
          key={i}
          style={{
            width: 3,
            borderRadius: 2,
            backgroundColor: color,
            height: anim.interpolate({ inputRange: [0, 1], outputRange: [4, 20] }),
          }}
        />
      ))}
    </View>
  );
}

// ─── Premium lock overlay ─────────────────────────────────────────────────────
function PremiumOverlay({ t, onPress }: { t: Record<string, string>; onPress: () => void }) {
  return (
    <TouchableOpacity
      style={s.lockOverlay}
      onPress={onPress}
      activeOpacity={0.9}
    >
      <View style={s.lockBadge}>
        <Ionicons name="diamond" size={13} color="#fff" />
        <Text style={s.lockText}>{t.premiumLock}</Text>
      </View>
    </TouchableOpacity>
  );
}

// ─── YouTube video player modal ────────────────────────────────────────────────
function YouTubePlayerModal({
  visible, videoUrl, onClose, colors
}: {
  visible: boolean; videoUrl: string; onClose: () => void; colors: any;
}) {
  const getYouTubeId = (url: string) => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return match && match[2].length === 11 ? match[2] : null;
  };

  const videoId = getYouTubeId(videoUrl);
  const { height } = Dimensions.get('window');

  if (!videoId) return null;

  const embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&controls=1&modestbranding=1`;

  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={[s.playerBg, { backgroundColor: colors.bg }]}>
        <TouchableOpacity
          style={s.playerClose}
          onPress={onClose}
          activeOpacity={0.8}
        >
          <Ionicons name="close" size={28} color={colors.text} />
        </TouchableOpacity>

        <View style={[s.playerContainer, { height: height * 0.5 }]}>
          <WebView
            source={{ uri: embedUrl }}
            style={s.webview}
            allowsFullscreenVideo
            javaScriptEnabled
            scrollEnabled={false}
          />
        </View>
      </View>
    </Modal>
  );
}

// ─── Video card ───────────────────────────────────────────────────────────────
function VideoCard({
  item, lang, colors, t, onPress
}: {
  item: VideoItem; lang: string; colors: any; t: Record<string, string>;
  onPress: (url: string) => void;
}) {
  const title = (item as any)[`title_${lang}`] || item.title_no;
  const summary = (item as any)[`instructor_summary_${lang}`] || item.instructor_summary_no || '';
  const flag = LANG_FLAG[item.language || 'no'] || '🇳🇴';

  return (
    <TouchableOpacity
      style={[s.card, { backgroundColor: colors.card, borderColor: colors.cardBorder }]}
      onPress={() => onPress(item.youtube_url)}
      activeOpacity={0.85}
    >
      {/* Thumbnail area */}
      <View style={[s.videoThumb, { backgroundColor: 'rgba(239,68,68,0.12)' }]}>
        <View style={s.playCircle}>
          <Ionicons name="play" size={20} color="#fff" />
        </View>
        <View style={s.ytBadge}>
          <Ionicons name="logo-youtube" size={12} color="#EF4444" />
        </View>
      </View>

      <View style={s.cardBody}>
        <View style={s.cardMeta}>
          <Text style={[s.cardTypeLabel, { color: '#EF4444' }]}>VIDEO</Text>
          <Text style={[s.cardLang, { color: colors.textMuted }]}>{flag}</Text>
        </View>
        <Text style={[s.cardTitle, { color: colors.text }]} numberOfLines={2}>{title}</Text>
        {summary ? (
          <Text style={[s.cardSummary, { color: colors.textMuted }]} numberOfLines={2}>{summary}</Text>
        ) : null}
        <TagRow tags={item.topic_tags} colors={colors} />
      </View>

      <Ionicons name="play-circle" size={20} color={colors.accent} style={s.openIcon} />
    </TouchableOpacity>
  );
}

// ─── Podcast card ─────────────────────────────────────────────────────────────
function PodcastCard({
  item, lang, colors, t, isPremium, onPaywall,
}: {
  item: PodcastItem; lang: string; colors: any; t: Record<string, string>;
  isPremium: boolean; onPaywall: () => void;
}) {
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(false);

  const title = (item as any)[`title_${lang}`] || item.title_no;
  const summary = (item as any)[`instructor_summary_${lang}`] || item.instructor_summary_no || '';
  const flag = LANG_FLAG[item.language || 'no'] || '🇳🇴';
  const mins = item.duration_seconds ? Math.round(item.duration_seconds / 60) : null;

  useEffect(() => { return () => { sound?.unloadAsync(); }; }, [sound]);

  const togglePlayback = async () => {
    if (!isPremium) { onPaywall(); return; }
    if (loading) return;
    if (sound) {
      if (isPlaying) { await sound.pauseAsync(); setIsPlaying(false); }
      else { await sound.playAsync(); setIsPlaying(true); }
    } else {
      setLoading(true);
      try {
        const { sound: ns } = await Audio.Sound.createAsync(
          { uri: getFullUrl(item.file_path) },
          { shouldPlay: true }
        );
        setSound(ns);
        setIsPlaying(true);
        ns.setOnPlaybackStatusUpdate((st) => {
          if (st.isLoaded) {
            setIsPlaying(st.isPlaying);
            if (st.didJustFinish) { setIsPlaying(false); ns.setPositionAsync(0); }
          }
        });
      } catch { /* ignore */ }
      finally { setLoading(false); }
    }
  };

  return (
    <View style={[s.card, s.podcastCard, { backgroundColor: colors.card, borderColor: isPlaying ? colors.accent : colors.cardBorder }]}>
      {/* Left: play button */}
      <TouchableOpacity
        style={[s.podcastPlayBtn, { backgroundColor: isPremium ? (isPlaying ? colors.accent : `${colors.accent}22`) : 'rgba(148,163,184,0.15)' }]}
        onPress={togglePlayback}
        activeOpacity={0.8}
      >
        {loading ? (
          <ActivityIndicator size="small" color={colors.accent} />
        ) : !isPremium ? (
          <Ionicons name="lock-closed" size={18} color={colors.textMuted} />
        ) : isPlaying ? (
          <WaveIcon active={isPlaying} color={colors.accent} />
        ) : (
          <Ionicons name="play" size={18} color={colors.accent} />
        )}
      </TouchableOpacity>

      {/* Body */}
      <View style={s.cardBody}>
        <View style={s.cardMeta}>
          <Text style={[s.cardTypeLabel, { color: colors.accent }]}>PODCAST</Text>
          <Text style={[s.cardLang, { color: colors.textMuted }]}>{flag}</Text>
          {mins ? <Text style={[s.cardLang, { color: colors.textMuted }]}>{mins} {t.minutes}</Text> : null}
        </View>
        <Text style={[s.cardTitle, { color: colors.text }]} numberOfLines={2}>{title}</Text>
        {summary ? (
          <Text style={[s.cardSummary, { color: colors.textMuted }]} numberOfLines={2}>{summary}</Text>
        ) : null}
        <TagRow tags={item.topic_tags} colors={colors} />
      </View>

      {!isPremium && <PremiumOverlay t={t} onPress={onPaywall} />}
    </View>
  );
}

function TagRow({ tags, colors }: { tags: string[]; colors: any }) {
  if (!tags?.length) return null;
  return (
    <View style={s.tagRow}>
      {tags.slice(0, 3).map((tag) => (
        <View key={tag} style={[s.tag, { backgroundColor: `${colors.accent}18` }]}>
          <Text style={[s.tagText, { color: colors.accent }]}>{tag}</Text>
        </View>
      ))}
    </View>
  );
}

// ─── Hub Card ─────────────────────────────────────────────────────────────────
function HubCard({ icon, color, label, onPress, isDark, c }: any) {
  return (
    <TouchableOpacity
      style={[s.hubCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}
      onPress={onPress}
      activeOpacity={0.8}
    >
      <View style={[s.hubIconBg, { backgroundColor: `${color}15` }]}>
        <Ionicons name={icon} size={22} color={color} />
      </View>
      <Text style={[s.hubLabel, { color: c.text }]}>{label}</Text>
    </TouchableOpacity>
  );
}

// ─── Filter chip labels (hardcoded per spec) ─────────────────────────────────
const FILTER_CHIPS_NO = ['Bremsing', 'Reaksjonstid', 'Vikeplikt', 'Lysbruk'];
const FILTER_CHIPS_TH = ['เบรกเมื่อเห็นอันตราย', 'เวลาเรียกเร็กเซ่น', 'การหลีกหนี', 'การใช้แสง'];
const FILTER_CHIPS_EN = ['Braking', 'Reaction Time', 'Right of Way', 'Light Usage'];

// ─── Main screen ──────────────────────────────────────────────────────────────
export default function LibraryScreen() {
  const router = useRouter();
  const { language, colors, isPremium } = useAppStore();
  const t = TR[language] || {};
  const c = colors;
  const isDark = c.bg === '#0F172A' || c.bg === '#0B1222';

  const [activeTab, setActiveTab] = useState<'videos' | 'podcasts'>('videos');
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [podcasts, setPodcasts] = useState<PodcastItem[]>([]);
  const [loadingVideos, setLoadingVideos] = useState(true);
  const [loadingPodcasts, setLoadingPodcasts] = useState(true);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [playingVideoUrl, setPlayingVideoUrl] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/videos/for-topic?limit=50`)
      .then((r) => r.json())
      .then((d) => setVideos(d.videos || d || []))
      .catch(() => setVideos([]))
      .finally(() => setLoadingVideos(false));

    fetch(`${BACKEND_URL}/api/podcasts/for-topic?limit=50`)
      .then((r) => r.json())
      .then((d) => setPodcasts(d.podcasts || d || []))
      .catch(() => setPodcasts([]))
      .finally(() => setLoadingPodcasts(false));
  }, []);

  // Get filter chips for current language
  const filterChips = language === 'th' ? FILTER_CHIPS_TH : language === 'en' ? FILTER_CHIPS_EN : FILTER_CHIPS_NO;

  // Filter content by selected chip
  const filteredVideos = selectedTag ? videos.filter((v) => v.topic_tags?.includes(selectedTag)) : videos;
  const filteredPodcasts = selectedTag ? podcasts.filter((p) => p.topic_tags?.includes(selectedTag)) : podcasts;
  const isLoading = activeTab === 'videos' ? loadingVideos : loadingPodcasts;

  return (
    <SafeAreaView style={[s.root, { backgroundColor: c.bg }]}>

      {/* Header with gradient */}
      <LinearGradient
        colors={isDark ? ['#0B1222', '#0F172A'] : [c.bg, c.bg]}
        style={s.headerGrad}
      >
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn} activeOpacity={0.7}>
          <Ionicons name="chevron-back" size={24} color={c.text} />
        </TouchableOpacity>
        <View style={s.headerCenter}>
          <Text style={[s.headerTitle, { color: c.text }]}>{t.title}</Text>
          <Text style={[s.headerSub, { color: c.textMuted }]}>{t.subtitle}</Text>
        </View>
        <View style={{ width: 40 }} />
      </LinearGradient>

      {/* Hub Grid */}
      <View style={s.hubGrid}>
        <HubCard icon="book" color="#3B82F6" label={t.studyBook} onPress={() => router.push('/book')} isDark={isDark} c={c} />
        <HubCard icon="warning" color="#EF4444" label={t.signs} onPress={() => router.push('/signs')} isDark={isDark} c={c} />
        <HubCard icon="bookmark" color="#F59E0B" label={t.bookmarks} onPress={() => router.push('/bookmarks')} isDark={isDark} c={c} />
        <HubCard icon="time" color="#10B981" label={t.history} onPress={() => router.push('/history')} isDark={isDark} c={c} />
      </View>

      <Text style={[s.sectionTitle, { color: c.text }]}>{t.media}</Text>

      {/* Tab bar */}
      <View style={[s.tabBar, { borderBottomColor: c.divider, backgroundColor: c.bg }]}>
        {(['videos', 'podcasts'] as const).map((tab) => {
          const active = activeTab === tab;
          const icon = tab === 'podcasts' ? 'mic' : 'videocam';
          const label = t[tab];
          const count = tab === 'podcasts' ? podcasts.length : videos.length;
          return (
            <TouchableOpacity
              key={tab}
              style={[s.tab, active && [s.tabActive, { borderBottomColor: c.accent }]]}
              onPress={() => { setActiveTab(tab); setSelectedTag(null); }}
              activeOpacity={0.8}
            >
              <Ionicons name={active ? icon : `${icon}-outline` as any} size={17} color={active ? c.accent : c.textMuted} />
              <Text style={[s.tabText, { color: active ? c.accent : c.textMuted }]}>{label}</Text>
              {count > 0 && (
                <View style={[s.tabBadge, { backgroundColor: active ? c.accent : `${c.accent}30` }]}>
                  <Text style={[s.tabBadgeText, { color: active ? '#fff' : c.accent }]}>{count}</Text>
                </View>
              )}
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Filter chips - hardcoded per spec */}
      <ScrollView
        horizontal showsHorizontalScrollIndicator={false}
        style={[s.chipScroll, { backgroundColor: c.bg }]}
        contentContainerStyle={s.chipContent}
      >
        <TouchableOpacity
          style={[s.chip, { borderColor: !selectedTag ? c.accent : c.cardBorder, backgroundColor: !selectedTag ? `${c.accent}18` : 'transparent' }]}
          onPress={() => setSelectedTag(null)}
        >
          <Text style={[s.chipText, { color: !selectedTag ? c.accent : c.textMuted }]}>{t.all}</Text>
        </TouchableOpacity>
        {filterChips.map((chipLabel) => {
          const sel = selectedTag === chipLabel;
          return (
            <TouchableOpacity
              key={chipLabel}
              style={[s.chip, { borderColor: sel ? c.accent : c.cardBorder, backgroundColor: sel ? `${c.accent}18` : 'transparent' }]}
              onPress={() => setSelectedTag(sel ? null : chipLabel)}
            >
              <Text style={[s.chipText, { color: sel ? c.accent : c.textMuted }]}>{chipLabel}</Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      {/* Content list */}
      <ScrollView style={s.list} contentContainerStyle={s.listContent}>
        {isLoading ? (
          <View style={{ paddingTop: 60, alignItems: 'center' }}>
            <ActivityIndicator size="large" color={c.accent} />
          </View>
        ) : activeTab === 'videos' ? (
          filteredVideos.length === 0 ? (
            <Text style={[s.empty, { color: c.textMuted }]}>{t.empty}</Text>
          ) : (
            filteredVideos.map((item) => (
              <VideoCard
                key={item.id || item.youtube_url}
                item={item}
                lang={language}
                colors={c}
                t={t}
                onPress={(url) => setPlayingVideoUrl(url)}
              />
            ))
          )
        ) : (
          filteredPodcasts.length === 0 ? (
            <Text style={[s.empty, { color: c.textMuted }]}>{t.empty}</Text>
          ) : (
            filteredPodcasts.map((item) => (
              <PodcastCard
                key={item.id || item.file_path}
                item={item} lang={language} colors={c} t={t}
                isPremium={isPremium}
                onPaywall={() => router.push('/paywall')}
              />
            ))
          )
        )}

        {/* Bottom spacer */}
        <View style={{ height: 32 }} />
      </ScrollView>

      {/* YouTube video player modal */}
      <YouTubePlayerModal
        visible={!!playingVideoUrl}
        videoUrl={playingVideoUrl || ''}
        onClose={() => setPlayingVideoUrl(null)}
        colors={c}
      />
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  root: { flex: 1 },

  // Hub Grid
  hubGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    gap: 12,
  },
  hubCard: {
    width: '47%',
    flexGrow: 1,
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 14,
    borderWidth: 1,
    gap: 12,
  },
  hubIconBg: {
    width: 40, height: 40, borderRadius: 12,
    alignItems: 'center', justifyContent: 'center',
  },
  hubLabel: { fontSize: 14, fontWeight: '700' },
  sectionTitle: {
    fontSize: 16, fontWeight: '800',
    paddingHorizontal: 16, paddingTop: 16, paddingBottom: 8,
  },

  // Header
  headerGrad: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 16, paddingTop: 12, paddingBottom: 16,
  },
  backBtn: { width: 40, alignItems: 'flex-start', paddingTop: 2 },
  headerCenter: { flex: 1, alignItems: 'center' },
  headerTitle: { fontSize: 18, fontWeight: '700', letterSpacing: -0.3 },
  headerSub: { fontSize: 11, marginTop: 2, fontWeight: '500', opacity: 0.7 },

  // Tabs
  tabBar: {
    flexDirection: 'row', borderBottomWidth: StyleSheet.hairlineWidth,
    paddingHorizontal: 8,
  },
  tab: {
    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: 6, paddingVertical: 12, paddingHorizontal: 4,
  },
  tabActive: { borderBottomWidth: 2 },
  tabText: { fontSize: 14, fontWeight: '600' },
  tabBadge: {
    minWidth: 20, height: 18, borderRadius: 9,
    alignItems: 'center', justifyContent: 'center', paddingHorizontal: 5,
  },
  tabBadgeText: { fontSize: 11, fontWeight: '700' },

  // Chips
  chipScroll: { maxHeight: 52 },
  chipContent: {
    paddingHorizontal: 14, paddingVertical: 10, gap: 8,
    flexDirection: 'row', alignItems: 'center',
  },
  chip: {
    paddingHorizontal: 13, paddingVertical: 5,
    borderRadius: 20, borderWidth: 1,
  },
  chipText: { fontSize: 12, fontWeight: '600' },

  // List
  list: { flex: 1 },
  listContent: { padding: 14, gap: 10 },
  empty: { textAlign: 'center', marginTop: 60, fontSize: 15 },

  // Cards
  card: {
    flexDirection: 'row', alignItems: 'flex-start',
    borderRadius: 14, borderWidth: 1, padding: 12, gap: 10,
    overflow: 'hidden',
    ...Platform.select({ web: { boxShadow: '0 2px 12px rgba(0,0,0,0.12)' } as any }),
  },
  podcastCard: { position: 'relative' },

  videoThumb: {
    width: 64, height: 64, borderRadius: 10,
    alignItems: 'center', justifyContent: 'center', flexShrink: 0,
  },
  playCircle: {
    width: 36, height: 36, borderRadius: 18,
    backgroundColor: '#EF4444', alignItems: 'center', justifyContent: 'center',
    paddingLeft: 2,
  },
  ytBadge: {
    position: 'absolute', bottom: 4, right: 4,
    backgroundColor: 'rgba(0,0,0,0.6)', borderRadius: 4, padding: 2,
  },

  podcastPlayBtn: {
    width: 52, height: 52, borderRadius: 26,
    alignItems: 'center', justifyContent: 'center', flexShrink: 0,
    alignSelf: 'center',
  },

  cardBody: { flex: 1, minWidth: 0 },
  cardMeta: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 3 },
  cardTypeLabel: { fontSize: 9, fontWeight: '800', letterSpacing: 1.2 },
  cardLang: { fontSize: 12 },
  cardTitle: { fontSize: 15, fontWeight: '700', lineHeight: 21, letterSpacing: -0.2 },
  cardSummary: { fontSize: 12, marginTop: 4, lineHeight: 17, opacity: 0.75 },

  tagRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginTop: 7 },
  tag: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 10 },
  tagText: { fontSize: 10, fontWeight: '600', letterSpacing: 0.3 },

  openIcon: { alignSelf: 'center', marginLeft: 2, flexShrink: 0 },

  // Premium lock
  lockOverlay: {
    position: 'absolute', top: 0, right: 0, bottom: 0,
    width: 60, alignItems: 'flex-end', justifyContent: 'flex-start',
    paddingTop: 10, paddingRight: 10,
  },
  lockBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: 'rgba(99,102,241,0.9)',
    paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10,
  },
  lockText: { color: '#fff', fontSize: 10, fontWeight: '700' },

  // YouTube player modal
  playerBg: {
    flex: 1, justifyContent: 'center', alignItems: 'center',
    paddingHorizontal: 12,
  },
  playerClose: {
    position: 'absolute', top: 16, right: 16, zIndex: 10,
    width: 40, height: 40, alignItems: 'center', justifyContent: 'center',
  },
  playerContainer: {
    width: '100%', borderRadius: 12, overflow: 'hidden',
    backgroundColor: '#000',
  },
  webview: { flex: 1 },
});
