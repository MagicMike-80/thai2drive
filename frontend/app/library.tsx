import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator, Linking, ScrollView, StyleSheet,
  Text, TouchableOpacity, View,
} from 'react-native';
// Note: Linking kept for potential future youtube_url fallback
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import { useAppStore } from '../src/store/appStore';
import { api } from '../src/services/api';

const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Bibliotek', videos: 'Filmer', podcasts: 'Podcaster',
    loading: 'Laster...', empty: 'Ingen innhold ennå.',
    play: 'Spill av', stop: 'Stopp', openYoutube: 'Åpne YouTube',
    videoCount: 'videoer', podcastCount: 'podcaster',
  },
  th: {
    title: 'ห้องสมุด', videos: 'วิดีโอ', podcasts: 'พอดแคสต์',
    loading: 'กำลังโหลด...', empty: 'ยังไม่มีเนื้อหา',
    play: 'เล่น', stop: 'หยุด', openYoutube: 'เปิด YouTube',
    videoCount: 'วิดีโอ', podcastCount: 'พอดแคสต์',
  },
  en: {
    title: 'Library', videos: 'Videos', podcasts: 'Podcasts',
    loading: 'Loading...', empty: 'No content yet.',
    play: 'Play', stop: 'Stop', openYoutube: 'Open YouTube',
    videoCount: 'videos', podcastCount: 'podcasts',
  },
};

type Tab = 'videos' | 'podcasts';

export default function LibraryScreen() {
  const router = useRouter();
  const { language, colors: c } = useAppStore();
  const t = TR[language] || TR.no;

  const [tab, setTab] = useState<Tab>('videos');
  const [videos, setVideos] = useState<any[]>([]);
  const [podcasts, setPodcasts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [playingId, setPlayingId] = useState<string | null>(null);
  const soundRef = React.useRef<Audio.Sound | null>(null);

  useEffect(() => {
    Promise.all([api.getLearningVideos(), api.getLearningPodcasts()])
      .then(([vids, pods]) => { setVideos(vids); setPodcasts(pods); })
      .catch(console.error)
      .finally(() => setLoading(false));
    return () => { soundRef.current?.unloadAsync(); };
  }, []);

  const titleFor = (item: any) => {
    if (language === 'th') return item.title_th || item.title_no || item.title_en || item.title || '';
    if (language === 'en') return item.title_en || item.title_no || item.title_th || item.title || '';
    return item.title_no || item.title_en || item.title_th || item.title || '';
  };

  const descFor = (item: any) => {
    if (language === 'th') return item.description_th || item.description_no || item.description_en || item.description || '';
    if (language === 'en') return item.description_en || item.description_no || item.description_th || item.description || '';
    return item.description_no || item.description_en || item.description_th || item.description || '';
  };

  // Unified audio toggle — used by both videos and podcasts tabs
  const toggleAudio = async (item: any) => {
    const id = item._id || item.id;
    if (playingId === id) {
      await soundRef.current?.stopAsync();
      await soundRef.current?.unloadAsync();
      soundRef.current = null;
      setPlayingId(null);
      return;
    }
    // Prefer audio_url (GridFS); fall back to youtube_url for legacy entries
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
        { uri: audioUrl.startsWith('/') ? `https://www.thai2drive.no${audioUrl}` : audioUrl },
        { shouldPlay: true }
      );
      soundRef.current = sound;
      setPlayingId(id);
      sound.setOnPlaybackStatusUpdate((s: any) => {
        if (s.didJustFinish) { setPlayingId(null); sound.unloadAsync(); }
      });
    } catch (e) { console.error('Audio error', e); }
  };

  return (
    <SafeAreaView style={[s.root, { backgroundColor: c.bg }]}>
      {/* Header */}
      <View style={[s.header, { borderBottomColor: c.divider }]}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}>
          <Ionicons name="arrow-back" size={22} color={c.text} />
        </TouchableOpacity>
        <Text style={[s.headerTitle, { color: c.text }]}>{t.title}</Text>
        <View style={{ width: 36 }} />
      </View>

      {/* Tabs */}
      <View style={[s.tabs, { borderBottomColor: c.divider }]}>
        {(['videos', 'podcasts'] as Tab[]).map(tabId => (
          <TouchableOpacity
            key={tabId}
            style={[s.tab, tab === tabId && { borderBottomColor: c.accent, borderBottomWidth: 2.5 }]}
            onPress={() => setTab(tabId)}
          >
            <Ionicons
              name={tabId === 'videos' ? 'film-outline' : 'mic-outline'}
              size={16}
              color={tab === tabId ? c.accent : c.textMuted}
            />
            <Text style={[s.tabText, { color: tab === tabId ? c.accent : c.textMuted }]}>
              {t[tabId]}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {loading ? (
        <View style={s.center}><ActivityIndicator size="large" color={c.accent} /></View>
      ) : (
        <ScrollView contentContainerStyle={s.list} showsVerticalScrollIndicator={false}>
          {tab === 'videos' && (
            videos.length === 0
              ? <Text style={[s.empty, { color: c.textMuted }]}>{t.empty}</Text>
              : videos.map((vid, idx) => {
                  const id = vid._id || vid.id || idx.toString();
                  const isPlaying = playingId === id;
                  return (
                    <View key={id} style={[s.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
                      <View style={[s.podIcon, { backgroundColor: isPlaying ? c.accent : c.letterBg }]}>
                        <Ionicons
                          name={isPlaying ? 'stop' : 'film'}
                          size={24}
                          color={isPlaying ? '#0F172A' : c.accent}
                        />
                      </View>
                      <View style={s.cardBody}>
                        <Text style={[s.cardTitle, { color: c.text }]} numberOfLines={2}>{titleFor(vid)}</Text>
                        {descFor(vid) ? (
                          <Text style={[s.cardDesc, { color: c.textSecondary }]} numberOfLines={2}>{descFor(vid)}</Text>
                        ) : null}
                        <TouchableOpacity
                          style={[s.actionBtn, { backgroundColor: isPlaying ? '#ef4444' : c.accent }]}
                          onPress={() => toggleAudio(vid)}
                        >
                          <Ionicons
                            name={isPlaying ? 'stop-circle-outline' : 'play-circle-outline'}
                            size={16}
                            color="#fff"
                          />
                          <Text style={s.actionBtnText}>{isPlaying ? t.stop : t.play}</Text>
                        </TouchableOpacity>
                      </View>
                    </View>
                  );
                })
          )}

          {tab === 'podcasts' && (
            podcasts.length === 0
              ? <Text style={[s.empty, { color: c.textMuted }]}>{t.empty}</Text>
              : podcasts.map((pod, idx) => {
                  const id = pod._id || pod.id || idx.toString();
                  const isPlaying = playingId === id;
                  return (
                    <View key={id} style={[s.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
                      <View style={[s.podIcon, { backgroundColor: isPlaying ? c.accent : c.letterBg }]}>
                        <Ionicons name={isPlaying ? 'stop' : 'mic'} size={24} color={isPlaying ? '#0F172A' : c.accent} />
                      </View>
                      <View style={s.cardBody}>
                        <Text style={[s.cardTitle, { color: c.text }]} numberOfLines={2}>{titleFor(pod)}</Text>
                        {descFor(pod) ? (
                          <Text style={[s.cardDesc, { color: c.textSecondary }]} numberOfLines={2}>{descFor(pod)}</Text>
                        ) : null}
                        <TouchableOpacity
                          style={[s.actionBtn, { backgroundColor: isPlaying ? '#ef4444' : c.accent }]}
                          onPress={() => toggleAudio(pod)}
                        >
                          <Ionicons name={isPlaying ? 'stop-circle-outline' : 'play-circle-outline'} size={16} color="#fff" />
                          <Text style={s.actionBtnText}>{isPlaying ? t.stop : t.play}</Text>
                        </TouchableOpacity>
                      </View>
                    </View>
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
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 1,
  },
  headerTitle: { fontSize: 18, fontWeight: '700' },
  backBtn: { padding: 6 },
  tabs: {
    flexDirection: 'row', borderBottomWidth: 1,
  },
  tab: {
    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: 6, paddingVertical: 12,
  },
  tabText: { fontSize: 14, fontWeight: '600' },
  list: { padding: 14, gap: 12 },
  empty: { fontSize: 15, textAlign: 'center', marginTop: 40 },
  card: {
    flexDirection: 'row', borderRadius: 12, borderWidth: 1,
    overflow: 'hidden', alignItems: 'flex-start',
  },
  thumbWrap: { width: 80 },
  thumb: { width: 80, height: 80, alignItems: 'center', justifyContent: 'center' },
  podIcon: { width: 64, height: 64, alignItems: 'center', justifyContent: 'center', margin: 10, borderRadius: 32 },
  cardBody: { flex: 1, padding: 12, gap: 6 },
  cardTitle: { fontSize: 15, fontWeight: '600', lineHeight: 20 },
  cardDesc: { fontSize: 13, lineHeight: 18 },
  actionBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 12, paddingVertical: 7, borderRadius: 8,
    alignSelf: 'flex-start', marginTop: 4,
  },
  actionBtnText: { color: '#fff', fontSize: 13, fontWeight: '600' },
});
