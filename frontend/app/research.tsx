import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import { LinearGradient } from 'expo-linear-gradient';
import { useAppStore } from '../src/store/appStore';
import { LanguageSwitcher } from '../src/components/LanguageSwitcher';
import { BottomNavBar } from '../src/components/BottomNavBar';

interface Track {
  filename: string;
  title: Record<string, string>;
  description: Record<string, string>;
}

const TRACKS: Track[] = [
  {
    filename: 'politi i kryss.mp3',
    title: {
      no: 'Politi i kryss',
      th: 'ตำรวจที่สี่แยก',
      en: 'Police in Intersections',
    },
    description: {
      no: 'Forstå politiets tegn og signaler når de dirigerer trafikken i et veikryss.',
      th: 'ทำความเข้าใจสัญญาณมือของตำรวจจราจรเมื่อควบคุมการจราจรที่สี่แยก',
      en: 'Understand police signals and hand signs when directing traffic in an intersection.',
    },
  },
  {
    filename: 'vikepliksregel.mp3',
    title: {
      no: 'Vikepliktsregel',
      th: 'กฎการให้ทาง',
      en: 'Right of Way Rule',
    },
    description: {
      no: 'Gjennomgang av de grunnleggende reglene for vikeplikt i norsk trafikk.',
      th: 'ทบทวนกฎพื้นฐานเกี่ยวกับการให้ทางในระบบจราจรของนอร์เวย์',
      en: 'Review of the fundamental rules for the right of way in Norwegian traffic.',
    },
  },
  {
    filename: 'vikeplikt.mp3',
    title: {
      no: 'Vikeplikt',
      th: 'การให้ทาง',
      en: 'Duty to Give Way',
    },
    description: {
      no: 'Hva innebærer vikeplikt i praksis, og hvordan opptre hensynsfullt?',
      th: 'การให้ทางในทางปฏิบัติหมายถึงอะไร และต้องปฏิบัติอย่างไรให้ปลอดภัย',
      en: 'What does the duty to give way mean in practice, and how to act considerately?',
    },
  },
];

const TR: Record<string, Record<string, string>> = {
  no: {
    headerTitle: 'The Research',
    headerSubtitle: 'Premium lydbibliotek',
    introTitle: 'Premium Lydbibliotek',
    introBody: 'Få dypere forståelse av trafikkreglene med våre spesialiserte lydspor. Lytt i bakgrunnen mens du er på farten.',
    errorTitle: 'Feil',
    errorMessage: 'Klarte ikke å spille av lydsporet.',
    loading: 'Laster...',
    playing: 'Spiller av',
    paused: 'Pauset',
  },
  th: {
    headerTitle: 'The Research',
    headerSubtitle: 'คลังบทเรียนเสียงพรีเมียม',
    introTitle: 'บทเรียนเสียงระดับพรีเมียม',
    introBody: 'ทำความเข้าใจกฎจราจรให้ลึกซึ้งยิ่งขึ้นผ่านเสียงอธิบายวิเคราะห์อย่างละเอียด สามารถฟังในขณะปิดหน้าจอหรือทำกิจกรรมอื่นได้',
    errorTitle: 'เกิดข้อผิดพลาด',
    errorMessage: 'ไม่สามารถเล่นไฟล์เสียงได้',
    loading: 'กำลังโหลด...',
    playing: 'กำลังเล่น',
    paused: 'หยุดชั่วคราว',
  },
  en: {
    headerTitle: 'The Research',
    headerSubtitle: 'Premium Audio Library',
    introTitle: 'Premium Audio Library',
    introBody: 'Gain a deeper understanding of traffic rules with our specialized audio tracks. Listen in the background on the go.',
    errorTitle: 'Error',
    errorMessage: 'Failed to play the audio track.',
    loading: 'Loading...',
    playing: 'Playing',
    paused: 'Paused',
  },
};

interface PlaybackState {
  filename: string | null;
  isPlaying: boolean;
  isBuffering: boolean;
  positionMillis: number;
  durationMillis: number;
}

export default function ResearchScreen() {
  const router = useRouter();
  const { language, colors: c, isDark } = useAppStore();
  const t = TR[language] || TR.en;

  const [playbackState, setPlaybackState] = useState<PlaybackState>({
    filename: null,
    isPlaying: false,
    isBuffering: false,
    positionMillis: 0,
    durationMillis: 0,
  });

  const soundRef = useRef<Audio.Sound | null>(null);
  const currentFilenameRef = useRef<string | null>(null);

  useEffect(() => {
    // Configure expo-av for background playback
    Audio.setAudioModeAsync({
      staysActiveInBackground: true,
      playsInSilentModeIOS: true,
      shouldDuckAndroid: true,
      playThroughEarpieceAndroid: false,
    }).catch((err) => console.log('Error setting audio mode', err));

    return () => {
      if (soundRef.current) {
        soundRef.current.unloadAsync().catch((err) => console.log('Error unloading', err));
      }
    };
  }, []);

  const onPlaybackStatusUpdate = (status: any) => {
    if (status.isLoaded) {
      setPlaybackState({
        filename: currentFilenameRef.current,
        isPlaying: status.isPlaying,
        isBuffering: status.isBuffering,
        positionMillis: status.positionMillis,
        durationMillis: status.durationMillis || 0,
      });

      // Handle automatic track stop/unload on completion
      if (status.didJustFinish) {
        setPlaybackState({
          filename: null,
          isPlaying: false,
          isBuffering: false,
          positionMillis: 0,
          durationMillis: 0,
        });
        currentFilenameRef.current = null;
      }
    } else {
      if (status.error) {
        console.log(`Playback status error: ${status.error}`);
      }
    }
  };

  const playTrack = async (filename: string) => {
    try {
      // Toggle play/pause if already loaded
      if (currentFilenameRef.current === filename && soundRef.current) {
        const status = await soundRef.current.getStatusAsync();
        if (status.isLoaded) {
          if (status.isPlaying) {
            await soundRef.current.pauseAsync();
          } else {
            await soundRef.current.playAsync();
          }
        }
        return;
      }

      // Stop and unload existing sound
      if (soundRef.current) {
        await soundRef.current.unloadAsync();
        soundRef.current = null;
      }

      setPlaybackState({
        filename,
        isPlaying: false,
        isBuffering: true,
        positionMillis: 0,
        durationMillis: 0,
      });
      currentFilenameRef.current = filename;

      const baseUrl = (process.env.EXPO_PUBLIC_BACKEND_URL || 'http://localhost:3000').replace(/\/$/, '');
      const url = `${baseUrl}/public_assets/${filename}`;

      const { sound } = await Audio.Sound.createAsync(
        { uri: url },
        { shouldPlay: true },
        onPlaybackStatusUpdate
      );
      soundRef.current = sound;
    } catch (err) {
      console.error('Error playing track:', err);
      Alert.alert(t.errorTitle, t.errorMessage);
      setPlaybackState({
        filename: null,
        isPlaying: false,
        isBuffering: false,
        positionMillis: 0,
        durationMillis: 0,
      });
      currentFilenameRef.current = null;
    }
  };

  const seekRelative = async (millis: number) => {
    if (soundRef.current) {
      const status = await soundRef.current.getStatusAsync();
      if (status.isLoaded) {
        const newPos = Math.max(0, Math.min(status.durationMillis || 0, status.positionMillis + millis));
        await soundRef.current.setPositionAsync(newPos);
      }
    }
  };

  const formatTime = (millis: number) => {
    if (isNaN(millis) || millis < 0) return '0:00';
    const totalSeconds = Math.floor(millis / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <LinearGradient
        colors={isDark ? ['#0B1222', '#0F172A', '#0B1222'] : ['#F4F8FD', '#FFFFFF', '#EEF5FB']}
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />

      <ScrollView contentContainerStyle={st.scroll} showsVerticalScrollIndicator={false}>
        {/* Top bar: Settings button + language switcher */}
        <View style={st.topBar}>
          <View style={st.topRight}>
            <LanguageSwitcher size="sm" />
            <TouchableOpacity
              testID="settings-btn"
              style={[st.iconBtn, { backgroundColor: c.card, borderColor: c.cardBorder }]}
              onPress={() => router.push('/settings')}
            >
              <Ionicons name="settings-outline" size={20} color={c.text} />
            </TouchableOpacity>
          </View>
          <TouchableOpacity
            style={[st.backBtn, { backgroundColor: c.card, borderColor: c.cardBorder }]}
            onPress={() => router.replace('/')}
          >
            <Ionicons name="chevron-back" size={20} color={c.text} />
          </TouchableOpacity>
        </View>

        {/* Header Title */}
        <View style={st.header}>
          <Text style={[st.title, { color: c.text }]}>{t.headerTitle}</Text>
          <Text style={[st.subtitle, { color: c.textMuted }]}>{t.headerSubtitle}</Text>
        </View>

        {/* Intro Premium Info Card */}
        <View style={[st.introCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
          <View style={[st.introIconBg, { backgroundColor: c.accentBg }]}>
            <Ionicons name="diamond" size={24} color={c.accent} />
          </View>
          <View style={st.introTextContainer}>
            <Text style={[st.introTitle, { color: c.text }]}>{t.introTitle}</Text>
            <Text style={[st.introBody, { color: c.textSecondary }]}>{t.introBody}</Text>
          </View>
        </View>

        {/* Track list */}
        <View style={st.tracksList}>
          {TRACKS.map((track) => {
            const isActive = playbackState.filename === track.filename;
            const isPlaying = isActive && playbackState.isPlaying;
            const isBuffering = isActive && playbackState.isBuffering;

            // Calculate progress percentage
            const progressPercent =
              playbackState.durationMillis > 0
                ? (playbackState.positionMillis / playbackState.durationMillis) * 100
                : 0;

            const titleText = track.title[language] || track.title.en;
            const descriptionText = track.description[language] || track.description.en;

            return (
              <View
                key={track.filename}
                style={[
                  st.trackCard,
                  {
                    backgroundColor: c.card,
                    borderColor: isActive ? c.accent : c.cardBorder,
                    borderWidth: isActive ? 1.5 : 1,
                  },
                ]}
              >
                <View style={st.trackRow}>
                  <View style={[st.trackIconWrap, { backgroundColor: isActive ? c.accentBg : c.letterBg }]}>
                    <Ionicons
                      name={isActive ? 'headset' : 'headset-outline'}
                      size={20}
                      color={isActive ? c.accent : c.textSecondary}
                    />
                  </View>

                  <View style={st.trackInfo}>
                    <Text style={[st.trackTitle, { color: c.text }]}>{titleText}</Text>
                    <Text style={[st.trackDesc, { color: c.textSecondary }]}>{descriptionText}</Text>
                  </View>

                  {/* Play/Pause Button on inactive or top-right of active */}
                  {!isActive && (
                    <TouchableOpacity
                      testID={`play-btn-${track.filename}`}
                      style={[st.playButtonMini, { backgroundColor: c.accent }]}
                      onPress={() => playTrack(track.filename)}
                      activeOpacity={0.8}
                    >
                      <Ionicons name="play" size={16} color="#0F172A" />
                    </TouchableOpacity>
                  )}
                </View>

                {/* Expanded Player Controls for Active Track */}
                {isActive && (
                  <View style={st.activePlayerSection}>
                    {/* Time Progress Bar */}
                    <View style={st.progressContainer}>
                      <View style={[st.progressBarBg, { backgroundColor: c.progressBg }]}>
                        <View style={[st.progressBarFill, { width: `${progressPercent}%`, backgroundColor: c.accent }]} />
                      </View>
                      <View style={st.timeRow}>
                        <Text style={[st.timeText, { color: c.textMuted }]}>
                          {formatTime(playbackState.positionMillis)}
                        </Text>
                        <Text style={[st.timeText, { color: c.textMuted }]}>
                          {formatTime(playbackState.durationMillis)}
                        </Text>
                      </View>
                    </View>

                    {/* Controls Row */}
                    <View style={st.controlsRow}>
                      {/* Skip Back 15s */}
                      <TouchableOpacity
                        style={[st.controlBtn, { borderColor: c.cardBorder }]}
                        onPress={() => seekRelative(-15000)}
                        disabled={isBuffering}
                        activeOpacity={0.7}
                      >
                        <Ionicons name="play-back-outline" size={20} color={c.text} />
                        <Text style={[st.skipText, { color: c.textMuted }]}>15s</Text>
                      </TouchableOpacity>

                      {/* Main Play/Pause/Buffer */}
                      <TouchableOpacity
                        testID={`play-pause-active-${track.filename}`}
                        style={[st.playButtonLarge, { backgroundColor: c.accent }]}
                        onPress={() => playTrack(track.filename)}
                        disabled={isBuffering}
                        activeOpacity={0.8}
                      >
                        {isBuffering ? (
                          <ActivityIndicator size="small" color="#0F172A" />
                        ) : (
                          <Ionicons name={isPlaying ? 'pause' : 'play'} size={24} color="#0F172A" />
                        )}
                      </TouchableOpacity>

                      {/* Skip Forward 15s */}
                      <TouchableOpacity
                        style={[st.controlBtn, { borderColor: c.cardBorder }]}
                        onPress={() => seekRelative(15000)}
                        disabled={isBuffering}
                        activeOpacity={0.7}
                      >
                        <Ionicons name="play-forward-outline" size={20} color={c.text} />
                        <Text style={[st.skipText, { color: c.textMuted }]}>15s</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                )}
              </View>
            );
          })}
        </View>
      </ScrollView>

      {/* Persistent Bottom Navigation Bar */}
      <BottomNavBar activeTab="research" />
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  container: {
    flex: 1,
  },
  scroll: {
    padding: 24,
    paddingBottom: 120, // Add bottom padding to prevent content overlap with BottomNavBar
  },
  topBar: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  topRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  iconBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
  },
  header: {
    marginBottom: 24,
  },
  title: {
    fontSize: 34,
    fontWeight: '800',
    letterSpacing: -1,
  },
  subtitle: {
    fontSize: 14,
    marginTop: 4,
  },
  introCard: {
    flexDirection: 'row',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    marginBottom: 28,
    alignItems: 'center',
    gap: 16,
  },
  introIconBg: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  introTextContainer: {
    flex: 1,
  },
  introTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 4,
  },
  introBody: {
    fontSize: 13,
    lineHeight: 18,
  },
  tracksList: {
    gap: 16,
  },
  trackCard: {
    borderRadius: 20,
    padding: 18,
    borderWidth: 1,
  },
  trackRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
  },
  trackIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  trackInfo: {
    flex: 1,
  },
  trackTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 4,
  },
  trackDesc: {
    fontSize: 12,
    lineHeight: 16,
  },
  playButtonMini: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  activePlayerSection: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: 'rgba(255, 255, 255, 0.1)',
  },
  progressContainer: {
    marginBottom: 16,
  },
  progressBarBg: {
    height: 6,
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  timeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 6,
  },
  timeText: {
    fontSize: 11,
    fontWeight: '600',
  },
  controlsRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 24,
  },
  controlBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 12,
    gap: 4,
  },
  skipText: {
    fontSize: 10,
    fontWeight: '700',
  },
  playButtonLarge: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 4,
  },
});
