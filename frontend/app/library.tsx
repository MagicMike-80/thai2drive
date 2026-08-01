import React, { useEffect, useState, useCallback } from 'react';
import {
  ActivityIndicator, Image, Linking, ScrollView, StyleSheet,
  Text, TextInput, TouchableOpacity, View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useFocusEffect } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';
import { useAppStore } from '../src/store/appStore';
import { api, BACKEND_URL } from '../src/services/api';

// ── Language filter ──────────────────────────────────────────────
const LANG_ORDER = ['no', 'th', 'en'] as const;
type LangCode = typeof LANG_ORDER[number];
const LANG_FLAGS: Record<LangCode, string> = { no: '🇳🇴', th: '🇹🇭', en: '🇬🇧' };

// ── Trilingual strings ───────────────────────────────────────────
const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Bibliotek', videos: 'Videoer', podcasts: 'Podcaster', articles: 'Artikler',
    search: 'Søk etter videoer, emner...', continueWatching: 'Fortsett å se',
    allTopics: 'Alle Emner', loading: 'Laster...', empty: 'Ingen innhold ennå.',
    play: 'Spill av', stop: 'Stopp', continueBtn: 'Fortsett', completed: 'fullført',
    norwegian: 'Norsk tale', thai: 'Thai tale', min: 'min',
  },
  th: {
    title: 'ห้องสมุด', videos: 'วิดีโอ', podcasts: 'พอดแคสต์', articles: 'บทความ',
    search: 'ค้นหาวิดีโอ หัวข้อ...', continueWatching: 'ดูต่อ',
    allTopics: 'ทุกหัวข้อ', loading: 'กำลังโหลด...', empty: 'ยังไม่มีเนื้อหา',
    play: 'เล่น', stop: 'หยุด', continueBtn: 'ดูต่อ', completed: 'เสร็จ',
    norwegian: 'เสียงนอร์เวย์', thai: 'เสียงไทย', min: 'นาที',
  },
  en: {
    title: 'Library', videos: 'Videos', podcasts: 'Podcasts', articles: 'Articles',
    search: 'Search videos, topics...', continueWatching: 'Continue Watching',
    allTopics: 'All Topics', loading: 'Loading...', empty: 'No content yet.',
    play: 'Play', stop: 'Stop', continueBtn: 'Continue', completed: 'completed',
    norwegian: 'Norwegian audio', thai: 'Thai audio', min: 'min',
  },
};

type Tab = 'videos' | 'podcasts';
const NEON_COLORS = ['#00F5FF', '#FF007F', '#7000FF', '#AAFF00', '#FF6A00', '#CC44FF'];

export default function LibraryScreen() {
  const router = useRouter();
  const { language, colors: c } = useAppStore();
  const t = TR[language] || {};
  const [langFilter, setLangFilter] = useState<LangCode>(language as LangCode || 'no');

  const [tab, setTab] = useState<Tab>('videos');
  const [allVideos, setAllVideos] = useState<any[]>([]);
  const [podcasts, setPodcasts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [playingId, setPlayingId] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [continueId, setContinueId] = useState<string | null>(null);
  const soundRef = React.useRef<Audio.Sound | null>(null);

  // Load progress from AsyncStorage
  useFocusEffect(useCallback(() => {
    AsyncStorage.getItem('t2d_continue_watching').then(val => {
      if (val) setContinueId(val);
    }).catch(() => {});
  }, []));

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getLearningVideos(langFilter),
      api.getLearningPodcasts(langFilter),
    ])
      .then(([vids, pods]) => { setAllVideos(vids); setPodcasts(pods); })
      .catch(console.error)
      .finally(() => setLoading(false));
    return () => { soundRef.current?.unloadAsync(); };
  }, [langFilter]);

  // Språkrenhet: kun aktivt språk. Mangler teksten, vises ingenting (Fail-Stop).
  const titleFor = (item: any) => {
    if (language === 'th') return item.title_th || '';
    if (language === 'en') return item.title_en || '';
    return item.title_no || '';
  };

  const descFor = (item: any) => {
    if (language === 'th') return item.description_th || '';
    if (language === 'en') return item.description_en || '';
    return item.description_no || '';
  };

  // Backend gir thumbs som relativ sti (/api/assets/thumbs/...) — native trenger absolutt URL.
  const assetUri = (path: string) => (path.startsWith('/') ? `${BACKEND_URL}${path}` : path);

  const filteredVideos = allVideos.filter(v => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return titleFor(v).toLowerCase().includes(q);
  });

  const toggleAudio = async (item: any) => {
    const id = item._id || item.id;
    if (playingId === id) {
      await soundRef.current?.stopAsync();
      await soundRef.current?.unloadAsync();
      soundRef.current = null;
      setPlayingId(null);
      return;
    }
    const audioUrl = item.audio_url || item.url || '';
    const youtubeUrl = item.youtube_url || '';
    if (!audioUrl && youtubeUrl) {
      Linking.openURL(youtubeUrl).catch(console.error);
      return;
    }
    if (!audioUrl) return;
    try {
      await soundRef.current?.unloadAsync();
      soundRef.current = null;
      await Audio.setAudioModeAsync({ playsInSilentModeIOS: true });
      const { sound } = await Audio.Sound.createAsync(
        { uri: audioUrl.startsWith('/') ? `${BACKEND_URL}${audioUrl}` : audioUrl },
        { shouldPlay: true }
      );
      soundRef.current = sound;
      setPlayingId(id);
      sound.setOnPlaybackStatusUpdate((s: any) => {
        if (s.didJustFinish) { setPlayingId(null); sound.unloadAsync(); }
      });
    } catch (e) { console.error('Audio error', e); }
  };

  const continueVideo = allVideos.find(v => (v._id || v.id) === continueId) || allVideos[0];

  return (
    <SafeAreaView style={[s.root, { backgroundColor: c.bg }]}>
      {/* ── Header ── */}
      <View style={s.header}>
        <Text style={s.logo}><Text style={{ color: '#FF9933' }}>●</Text> Thai2Drive</Text>
        <View style={{ flexDirection: 'row', gap: 6 }}>
          {LANG_ORDER.map(lc => (
            <TouchableOpacity key={lc} onPress={() => setLangFilter(lc)}>
              <Text style={{ fontSize: 20, opacity: langFilter === lc ? 1 : 0.35 }}>
                {LANG_FLAGS[lc]}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
        <TouchableOpacity onPress={() => router.push('/settings')}>
          <Ionicons name="settings-outline" size={22} color={c.textMuted} />
        </TouchableOpacity>
      </View>

      {/* ── Page title ── */}
      <Text style={[s.pageTitle, { color: c.text }]}>{t.title}</Text>

      {/* ── Search bar ── */}
      <View style={[s.searchBar, { backgroundColor: 'rgba(0,0,0,0.3)', borderColor: 'rgba(255,255,255,0.1)' }]}>
        <Ionicons name="search" size={16} color={c.textMuted} style={{ marginRight: 10 }} />
        <TextInput
          style={[s.searchInput, { color: c.text }]}
          placeholder={t.search}
          placeholderTextColor={c.textMuted}
          value={search}
          onChangeText={setSearch}
        />
      </View>

      {/* ── Tabs ── */}
      <View style={[s.tabRow, { backgroundColor: 'rgba(0,0,0,0.2)' }]}>
        {(['videos', 'podcasts'] as Tab[]).map(tabId => (
          <TouchableOpacity
            key={tabId}
            style={[s.tab, tab === tabId && s.tabActive]}
            onPress={() => setTab(tabId)}
          >
            <Ionicons
              name={tabId === 'videos' ? 'film-outline' : 'mic-outline'}
              size={14} color={tab === tabId ? c.text : c.textMuted}
            />
            <Text style={[s.tabText, { color: tab === tabId ? c.text : c.textMuted }]}>
              {(t as any)[tabId]}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {loading ? (
        <View style={s.center}><ActivityIndicator size="large" color={c.accent} /></View>
      ) : (
        <ScrollView contentContainerStyle={s.scroll} showsVerticalScrollIndicator={false}>
          {tab === 'videos' && (
            <>
              {/* ── Continue Watching ── */}
              {continueVideo && (
                <>
                  <Text style={[s.sectionTitle, { color: c.text }]}>{t.continueWatching}</Text>
                  <TouchableOpacity
                    style={[s.heroCard, { borderColor: 'rgba(0,240,255,0.3)' }]}
                    onPress={() => (router as any).push({ pathname: '/video-player', params: { id: continueVideo._id || continueVideo.id } })}
                    activeOpacity={0.85}
                  >
                    <Image
                      source={{ uri: assetUri(continueVideo.thumbnail_url || '') }}
                      style={s.heroBg}
                    />
                    <LinearGradient
                      colors={['rgba(0,0,0,0.1)', 'rgba(0,0,0,0.85)']}
                      locations={[0, 0.7]}
                      style={s.heroOverlay}
                    >
                      <View style={s.heroHeader}>
                        <Text style={s.heroTitle} numberOfLines={2}>{titleFor(continueVideo)}</Text>
                        <TouchableOpacity style={s.bookmarkBtn}>
                          <Ionicons name="bookmark-outline" size={16} color="#fff" />
                        </TouchableOpacity>
                      </View>
                      <View style={s.progressTrack}>
                        <View style={[s.progressFill, { width: '35%' }]} />
                      </View>
                      <Text style={s.progressText}>35% {t.completed}</Text>
                      <View style={s.playBtn}>
                        <Ionicons name="play" size={20} color="#000" style={{ marginLeft: 2 }} />
                      </View>
                    </LinearGradient>
                  </TouchableOpacity>
                </>
              )}

              {/* ── All Topics ── */}
              <Text style={[s.sectionTitle, { color: c.text, marginTop: continueVideo ? 0 : 16 }]}>
                {t.allTopics}
              </Text>
              {filteredVideos.length === 0 ? (
                <Text style={[s.empty, { color: c.textMuted }]}>{t.empty}</Text>
              ) : filteredVideos.map((vid, idx) => {
                const id = vid._id || vid.id || idx.toString();
                const colorIdx = idx % NEON_COLORS.length;
                const neon = NEON_COLORS[colorIdx];
                const isPlaying = playingId === id;
                return (
                  <TouchableOpacity
                    key={id}
                    style={[s.subjectCard, { borderLeftColor: neon }]}
                    onPress={() => (router as any).push({ pathname: '/video-player', params: { id } })}
                    activeOpacity={0.85}
                  >
                    {vid.thumbnail_url ? (
                      <>
                        <Image source={{ uri: assetUri(vid.thumbnail_url) }} style={s.subjectBg} />
                        <LinearGradient
                          colors={['rgba(0,0,0,0.1)', 'rgba(0,0,0,0.8)']}
                          locations={[0, 0.6]}
                          style={s.subjectOverlay}
                        >
                          <View style={s.subjectTop}>
                            <Text style={s.subjectTitle} numberOfLines={2}>{titleFor(vid)}</Text>
                            <TouchableOpacity style={s.bookmarkBtn}>
                              <Ionicons name="bookmark-outline" size={14} color="#fff" />
                            </TouchableOpacity>
                          </View>
                          <View style={s.subjectBottom}>
                            <Text style={s.langBadge}>
                              {vid.language === 'th' ? '🇹🇭 ' : '🇳🇴 '}
                              {vid.language === 'th' ? t.thai : t.norwegian}
                            </Text>
                            {isPlaying ? (
                              <View style={[s.miniPlayBtn, { backgroundColor: '#ef4444' }]}>
                                <Ionicons name="stop" size={14} color="#fff" />
                              </View>
                            ) : vid.file_path && (
                              <View style={[s.miniPlayBtn, { backgroundColor: neon }]}>
                                <Ionicons name="play" size={14} color="#000" />
                              </View>
                            )}
                          </View>
                        </LinearGradient>
                      </>
                    ) : (
                      <View style={{ flex: 1, padding: 16, justifyContent: 'center' }}>
                        <Text style={[s.subjectTitle, { color: c.text }]} numberOfLines={2}>{titleFor(vid)}</Text>
                        <View style={{ flexDirection: 'row', gap: 8, marginTop: 10 }}>
                          <Text style={s.tag}>{t.videos}</Text>
                        </View>
                      </View>
                    )}
                  </TouchableOpacity>
                );
              })}
            </>
          )}

          {tab === 'podcasts' && (
            podcasts.length === 0
              ? <Text style={[s.empty, { color: c.textMuted }]}>{t.empty}</Text>
              : podcasts.map((pod, idx) => {
                  const id = pod._id || pod.id || idx.toString();
                  const isPlaying = playingId === id;
                  const colorIdx = idx % NEON_COLORS.length;
                  const neon = NEON_COLORS[colorIdx];
                  return (
                    <TouchableOpacity
                      key={id}
                      style={[s.subjectCard, { borderLeftColor: neon, minHeight: 80 }]}
                      onPress={() => toggleAudio(pod)}
                      activeOpacity={0.85}
                    >
                      <View style={{ flex: 1, padding: 16, flexDirection: 'row', alignItems: 'center' }}>
                        <View style={[s.podIconWrap, { backgroundColor: isPlaying ? neon : 'rgba(255,255,255,0.05)' }]}>
                          <Ionicons
                            name={isPlaying ? 'stop' : 'mic'}
                            size={22}
                            color={isPlaying ? '#000' : neon}
                          />
                        </View>
                        <View style={{ flex: 1, marginLeft: 12 }}>
                          <Text style={[s.subjectTitle, { color: c.text }]} numberOfLines={2}>{titleFor(pod)}</Text>
                          <View style={{ flexDirection: 'row', gap: 8, marginTop: 6 }}>
                            <Text style={s.tag}>{pod.language === 'th' ? '🇹🇭' : '🇳🇴'}</Text>
                            <Text style={s.tag}>{t.podcasts}</Text>
                          </View>
                        </View>
                      </View>
                    </TouchableOpacity>
                  );
                })
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  root: { flex: 1 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  scroll: { padding: 16, paddingBottom: 40 },

  // Header
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 20, paddingTop: 8, paddingBottom: 4,
  },
  logo: { fontSize: 18, fontWeight: '700', letterSpacing: -0.3 },

  // Page title
  pageTitle: { fontSize: 28, fontWeight: '600', textAlign: 'center', marginVertical: 8 },

  // Search bar
  searchBar: {
    flexDirection: 'row', alignItems: 'center',
    borderWidth: 1, borderRadius: 12, paddingHorizontal: 14, paddingVertical: 10,
    marginHorizontal: 16, marginBottom: 16,
  },
  searchInput: { flex: 1, fontSize: 14, fontFamily: 'Inter' },

  // Tabs
  tabRow: {
    flexDirection: 'row', borderRadius: 12, padding: 4,
    marginHorizontal: 16, marginBottom: 20,
  },
  tab: {
    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: 6, paddingVertical: 10, borderRadius: 8,
  },
  tabActive: {
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
  },
  tabText: { fontSize: 13, fontWeight: '600' },

  // Section
  sectionTitle: { fontSize: 17, fontWeight: '600', marginBottom: 12, marginTop: 16 },

  // Hero card (Continue Watching)
  heroCard: {
    height: 160, borderRadius: 16, overflow: 'hidden', marginBottom: 8,
    borderWidth: 1,
  },
  heroBg: { position: 'absolute', width: '100%', height: '100%' },
  heroOverlay: {
    flex: 1, padding: 16, justifyContent: 'space-between',
  },
  heroHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  heroTitle: { fontSize: 16, fontWeight: '600', color: '#fff', flex: 1, textShadowColor: 'rgba(0,0,0,0.5)', textShadowOffset: { width: 0, height: 2 }, textShadowRadius: 4 },
  bookmarkBtn: {
    width: 30, height: 30, borderRadius: 15,
    backgroundColor: 'rgba(255,255,255,0.1)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center', justifyContent: 'center', marginLeft: 8,
  },
  progressTrack: {
    width: '100%', height: 4, backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 2, overflow: 'hidden', marginBottom: 6,
  },
  progressFill: { height: '100%', backgroundColor: '#00F5FF', borderRadius: 2 },
  progressText: { fontSize: 11, color: 'rgba(255,255,255,0.6)' },
  playBtn: {
    position: 'absolute', top: '50%', left: '50%',
    width: 44, height: 44, borderRadius: 22,
    backgroundColor: 'rgba(0,240,255,0.85)',
    alignItems: 'center', justifyContent: 'center',
    marginLeft: -22, marginTop: -22,
  },

  // Subject card
  subjectCard: {
    borderRadius: 16, overflow: 'hidden', marginBottom: 12,
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderLeftWidth: 4, minHeight: 100,
  },
  subjectBg: { position: 'absolute', width: '100%', height: '100%' },
  subjectOverlay: { flex: 1, padding: 14, justifyContent: 'space-between', minHeight: 100 },
  subjectTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  subjectTitle: { fontSize: 15, fontWeight: '600', color: '#fff', flex: 1, textShadowColor: 'rgba(0,0,0,0.4)', textShadowOffset: { width: 0, height: 1 }, textShadowRadius: 3 },
  subjectBottom: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 },
  langBadge: {
    fontSize: 11, paddingHorizontal: 8, paddingVertical: 3,
    backgroundColor: 'rgba(0,0,0,0.5)', borderRadius: 4, overflow: 'hidden',
    color: 'rgba(255,255,255,0.8)',
  },
  miniPlayBtn: { width: 28, height: 28, borderRadius: 14, alignItems: 'center', justifyContent: 'center' },
  tag: {
    fontSize: 11, paddingHorizontal: 8, paddingVertical: 3,
    backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: 4, overflow: 'hidden',
    color: 'rgba(255,255,255,0.6)',
  },

  // Podcast icon
  podIconWrap: {
    width: 48, height: 48, borderRadius: 24,
    alignItems: 'center', justifyContent: 'center',
  },

  // Empty
  empty: { fontSize: 15, textAlign: 'center', marginTop: 40 },
});
