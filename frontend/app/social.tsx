import React, { useRef } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, ScrollView,
  SafeAreaView, Linking, Platform, Animated,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useAppStore } from '../src/store/appStore';

// ── Social links ─────────────────────────────────────────────────────────────
const FACEBOOK_URL   = 'https://www.facebook.com/profile.php?id=61565991554372';
const TIKTOK_URL     = 'https://www.tiktok.com/@thai2drive.no';
const YOUTUBE_CHAN   = 'https://www.youtube.com/channel/UCe965d1YB8Ds7mPSa5LOvRA';

// Facebook Page Plugin iframe (works cross-origin in browsers)
const FB_EMBED_SRC =
  'https://www.facebook.com/plugins/page.php' +
  '?href=https%3A%2F%2Fwww.facebook.com%2Fprofile.php%3Fid%3D61565991554372' +
  '&tabs=timeline&width=320&height=480' +
  '&small_header=true&adapt_container_width=true&hide_cover=false&show_facepile=false';

// YouTube latest-uploads embed (channel RSS → embed via YouTube channel)
const YT_EMBED_SRC =
  'https://www.youtube.com/embed?listType=user_uploads' +
  '&list=UCe965d1YB8Ds7mPSa5LOvRA&rel=0&modestbranding=1';

// ── Web-only iframe helper ────────────────────────────────────────────────────
function WebIframe({ src, height }: { src: string; height: number }) {
  if (Platform.OS !== 'web') return null;
  return React.createElement('iframe', {
    src,
    width: '100%',
    height,
    style: {
      border: 'none',
      borderRadius: 12,
      display: 'block',
      background: 'transparent',
    },
    allow: 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture',
    allowFullScreen: true,
    loading: 'lazy',
  });
}

// ── Translations ──────────────────────────────────────────────────────────────
const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Følg Thai2Drive',
    subtitle: 'Videoer, tips og trafikklærdom på sosiale medier',
    follow: 'Følg oss',
    open: 'Åpne',
    watchVideos: 'Se videoer',
    ytTitle: 'YouTube-kanal',
    ytDesc: 'Fullstendige video­forklaringer av trafikkteori, vikeplikt, bremselengde og mer — på norsk og thai.',
    fbTitle: 'Facebook-side',
    fbDesc: 'Oppdateringer, læringsinnhold og fellesskap for Thai-studenter som tar norsk lappen.',
    ttTitle: 'TikTok',
    ttDesc: 'Korte tips fra Michael Trafikklærer — perfekt for en rask repetisjon i hverdagen.',
    ytSubs: 'Videoer',
    fbLikes: 'Følgere',
    ttFollowers: 'Følgere',
    share: 'Del med venner',
    embedded: 'Innebygd visning',
    tapToOpen: 'Trykk for å åpne',
  },
  th: {
    title: 'ติดตาม Thai2Drive',
    subtitle: 'วิดีโอ เคล็ดลับ และความรู้จราจรบนโซเชียลมีเดีย',
    follow: 'ติดตาม',
    open: 'เปิด',
    watchVideos: 'ดูวิดีโอ',
    ytTitle: 'YouTube Channel',
    ytDesc: 'วิดีโออธิบายทฤษฎีจราจรแบบเต็มเรื่อง — วิกพลิกต์ ระยะเบรก และอีกมาก เป็นภาษานอร์เวย์และภาษาไทย',
    fbTitle: 'Facebook Page',
    fbDesc: 'อัปเดตและคอมมูนิตี้สำหรับนักเรียนไทยที่สอบใบขับขี่นอร์เวย์',
    ttTitle: 'TikTok',
    ttDesc: 'เคล็ดลับสั้นจากครูไมเคิล — เหมาะสำหรับทบทวนเร็วๆ ในชีวิตประจำวัน',
    ytSubs: 'วิดีโอ',
    fbLikes: 'ผู้ติดตาม',
    ttFollowers: 'ผู้ติดตาม',
    share: 'แชร์กับเพื่อน',
    embedded: 'ดูแบบฝัง',
    tapToOpen: 'แตะเพื่อเปิด',
  },
  en: {
    title: 'Follow Thai2Drive',
    subtitle: 'Videos, tips and traffic theory on social media',
    follow: 'Follow',
    open: 'Open',
    watchVideos: 'Watch videos',
    ytTitle: 'YouTube Channel',
    ytDesc: 'Full video explanations of traffic theory, right-of-way, braking distance and more — in Norwegian and Thai.',
    fbTitle: 'Facebook Page',
    fbDesc: 'Updates, learning content and community for Thai students taking the Norwegian driving test.',
    ttTitle: 'TikTok',
    ttDesc: 'Quick tips from Michael the Driving Instructor — perfect for a fast daily review.',
    ytSubs: 'Videos',
    fbLikes: 'Followers',
    ttFollowers: 'Followers',
    share: 'Share with friends',
    embedded: 'Embedded view',
    tapToOpen: 'Tap to open',
  },
};

// ── Animated platform card ────────────────────────────────────────────────────
function PlatformCard({
  children,
  onPress,
}: {
  children: React.ReactNode;
  onPress: () => void;
}) {
  const scale = useRef(new Animated.Value(1)).current;
  const pressIn  = () => Animated.spring(scale, { toValue: 0.97, useNativeDriver: true, speed: 50, bounciness: 0 }).start();
  const pressOut = () => Animated.spring(scale, { toValue: 1,    useNativeDriver: true, speed: 40, bounciness: 5 }).start();

  return (
    <Animated.View style={{ transform: [{ scale }] }}>
      <TouchableOpacity
        onPress={onPress}
        onPressIn={pressIn}
        onPressOut={pressOut}
        activeOpacity={1}
      >
        {children}
      </TouchableOpacity>
    </Animated.View>
  );
}

// ── Main screen ───────────────────────────────────────────────────────────────
export default function SocialScreen() {
  const router = useRouter();
  const { language, colors } = useAppStore();
  const c = colors;
  const isDark = c.bg === '#0F172A' || c.bg === '#0B1222';
  const t = TR[language] || TR.en;

  const open = (url: string) => Linking.openURL(url);

  return (
    <SafeAreaView style={[st.safe, { backgroundColor: c.bg }]}>
      {/* Header */}
      <View style={[st.header, { borderBottomColor: c.divider }]}>
        <TouchableOpacity onPress={() => router.back()} style={st.backBtn}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
          <Ionicons name="arrow-back" size={24} color={c.text} />
        </TouchableOpacity>
        <View style={{ flex: 1, marginLeft: 12 }}>
          <Text style={[st.headerTitle, { color: c.text }]}>{t.title}</Text>
          <Text style={[st.headerSub, { color: c.textMuted }]}>{t.subtitle}</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={st.scroll} showsVerticalScrollIndicator={false}>

        {/* ── YOUTUBE ─────────────────────────────────────────────────────── */}
        <View style={st.section}>
          {/* Branded banner */}
          <LinearGradient
            colors={['#1A0000', '#CC0000', '#FF4444']}
            start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
            style={st.platformBanner}
          >
            <View style={st.bannerInner}>
              <View style={st.platformIconWrap}>
                {/* YouTube play button */}
                <View style={[st.ytPlay, { backgroundColor: '#fff' }]}>
                  <Ionicons name="logo-youtube" size={28} color="#FF0000" />
                </View>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={st.platformName}>YouTube</Text>
                <Text style={st.platformHandle}>Thai2Drive</Text>
              </View>
              <TouchableOpacity
                style={st.followBtn}
                onPress={() => open(YOUTUBE_CHAN)}
              >
                <Text style={[st.followBtnText, { color: '#CC0000' }]}>{t.watchVideos}</Text>
              </TouchableOpacity>
            </View>
          </LinearGradient>

          {/* Description card */}
          <View style={[st.descCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={[st.descText, { color: c.textMuted }]}>{t.ytDesc}</Text>
          </View>

          {/* Embedded player (web only) — wraps in a pressable fallback on native */}
          {Platform.OS === 'web' ? (
            <View style={[st.embedWrap, { backgroundColor: '#000', borderColor: '#333' }]}>
              <WebIframe src={YT_EMBED_SRC} height={200} />
            </View>
          ) : (
            <PlatformCard onPress={() => open(YOUTUBE_CHAN)}>
              <LinearGradient
                colors={['#1a0000', '#300000']}
                style={[st.nativePreview, { borderColor: '#CC0000' }]}
              >
                <Ionicons name="logo-youtube" size={48} color="#FF0000" />
                <Text style={[st.nativePreviewText, { color: '#fff' }]}>{t.tapToOpen}</Text>
              </LinearGradient>
            </PlatformCard>
          )}

          {/* Open button */}
          <TouchableOpacity
            style={[st.openBtn, { backgroundColor: '#FF0000' }]}
            onPress={() => open(YOUTUBE_CHAN)}
          >
            <Ionicons name="logo-youtube" size={18} color="#fff" />
            <Text style={st.openBtnText}>{t.watchVideos}</Text>
            <Ionicons name="open-outline" size={16} color="rgba(255,255,255,0.7)" />
          </TouchableOpacity>
        </View>

        {/* ── FACEBOOK ────────────────────────────────────────────────────── */}
        <View style={st.section}>
          <LinearGradient
            colors={['#001A40', '#0866FF', '#4299FF']}
            start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
            style={st.platformBanner}
          >
            <View style={st.bannerInner}>
              <View style={st.platformIconWrap}>
                <View style={[st.ytPlay, { backgroundColor: '#fff' }]}>
                  <Ionicons name="logo-facebook" size={28} color="#0866FF" />
                </View>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={st.platformName}>Facebook</Text>
                <Text style={st.platformHandle}>Thai2Drive</Text>
              </View>
              <TouchableOpacity
                style={st.followBtn}
                onPress={() => open(FACEBOOK_URL)}
              >
                <Text style={[st.followBtnText, { color: '#0866FF' }]}>{t.follow}</Text>
              </TouchableOpacity>
            </View>
          </LinearGradient>

          <View style={[st.descCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={[st.descText, { color: c.textMuted }]}>{t.fbDesc}</Text>
          </View>

          {/* Facebook Page Plugin — web only */}
          {Platform.OS === 'web' ? (
            <View style={[st.embedWrap, { backgroundColor: isDark ? '#18191A' : '#f0f2f5', borderColor: '#0866FF' }]}>
              <WebIframe src={FB_EMBED_SRC} height={480} />
            </View>
          ) : (
            <PlatformCard onPress={() => open(FACEBOOK_URL)}>
              <LinearGradient
                colors={['#001a40', '#001e4a']}
                style={[st.nativePreview, { borderColor: '#0866FF' }]}
              >
                <Ionicons name="logo-facebook" size={48} color="#0866FF" />
                <Text style={[st.nativePreviewText, { color: '#fff' }]}>{t.tapToOpen}</Text>
              </LinearGradient>
            </PlatformCard>
          )}

          <TouchableOpacity
            style={[st.openBtn, { backgroundColor: '#0866FF' }]}
            onPress={() => open(FACEBOOK_URL)}
          >
            <Ionicons name="logo-facebook" size={18} color="#fff" />
            <Text style={st.openBtnText}>{t.follow} · Thai2Drive</Text>
            <Ionicons name="open-outline" size={16} color="rgba(255,255,255,0.7)" />
          </TouchableOpacity>
        </View>

        {/* ── TIKTOK ──────────────────────────────────────────────────────── */}
        <View style={st.section}>
          <LinearGradient
            colors={['#010101', '#161616', '#2a2a2a']}
            start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
            style={st.platformBanner}
          >
            <View style={st.bannerInner}>
              <View style={st.platformIconWrap}>
                <View style={[st.ytPlay, { backgroundColor: '#000' }]}>
                  {/* TikTok logo: a musical note in brand colors */}
                  <Text style={{ fontSize: 24 }}>♪</Text>
                </View>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={st.platformName}>TikTok</Text>
                <Text style={[st.platformHandle, { color: '#69C9D0' }]}>@thai2drive.no</Text>
              </View>
              <TouchableOpacity
                style={[st.followBtn, { backgroundColor: '#FE2C55' }]}
                onPress={() => open(TIKTOK_URL)}
              >
                <Text style={[st.followBtnText, { color: '#fff' }]}>{t.follow}</Text>
              </TouchableOpacity>
            </View>
          </LinearGradient>

          <View style={[st.descCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={[st.descText, { color: c.textMuted }]}>{t.ttDesc}</Text>
          </View>

          {/* TikTok: no public profile embed API — premium card + link */}
          <PlatformCard onPress={() => open(TIKTOK_URL)}>
            <View style={[st.ttPreview, { borderColor: '#FE2C55' }]}>
              {/* Glowing lines behind */}
              <View style={st.ttGlow1} />
              <View style={st.ttGlow2} />
              <View style={st.ttContent}>
                <View style={st.ttHandleRow}>
                  <View style={st.ttIcon}>
                    <Text style={{ fontSize: 28 }}>♪</Text>
                  </View>
                  <View>
                    <Text style={st.ttHandle}>@thai2drive.no</Text>
                    <Text style={[st.ttSub, { color: '#94A3B8' }]}>TikTok</Text>
                  </View>
                </View>

                <View style={st.ttStatsRow}>
                  <View style={st.ttStat}>
                    <Text style={st.ttStatNum}>🎬</Text>
                    <Text style={st.ttStatLbl}>Reels</Text>
                  </View>
                  <View style={[st.ttStatDivider]} />
                  <View style={st.ttStat}>
                    <Text style={st.ttStatNum}>🚗</Text>
                    <Text style={st.ttStatLbl}>Tips</Text>
                  </View>
                  <View style={st.ttStatDivider} />
                  <View style={st.ttStat}>
                    <Text style={st.ttStatNum}>📖</Text>
                    <Text style={st.ttStatLbl}>Teori</Text>
                  </View>
                </View>

                <View style={[st.ttOpenRow]}>
                  <Text style={st.ttOpenLabel}>{t.tapToOpen}</Text>
                  <Ionicons name="arrow-forward-circle" size={22} color="#FE2C55" />
                </View>
              </View>
            </View>
          </PlatformCard>

          <TouchableOpacity
            style={[st.openBtn, { backgroundColor: '#FE2C55' }]}
            onPress={() => open(TIKTOK_URL)}
          >
            <Text style={{ fontSize: 16 }}>♪</Text>
            <Text style={st.openBtnText}>@thai2drive.no</Text>
            <Ionicons name="open-outline" size={16} color="rgba(255,255,255,0.7)" />
          </TouchableOpacity>
        </View>

        {/* ── All platforms quick-links ────────────────────────────────────── */}
        <View style={[st.allRow, { borderColor: c.divider }]}>
          <Text style={[st.allRowLabel, { color: c.textMuted }]}>
            {language === 'th' ? 'ลิงก์ด่วน' : language === 'en' ? 'Quick links' : 'Hurtiglenker'}
          </Text>
          <View style={st.allBtns}>
            <TouchableOpacity style={[st.allBtn, { backgroundColor: '#FF0000' }]} onPress={() => open(YOUTUBE_CHAN)}>
              <Ionicons name="logo-youtube" size={20} color="#fff" />
            </TouchableOpacity>
            <TouchableOpacity style={[st.allBtn, { backgroundColor: '#0866FF' }]} onPress={() => open(FACEBOOK_URL)}>
              <Ionicons name="logo-facebook" size={20} color="#fff" />
            </TouchableOpacity>
            <TouchableOpacity style={[st.allBtn, { backgroundColor: '#010101', borderWidth: 1, borderColor: '#FE2C55' }]} onPress={() => open(TIKTOK_URL)}>
              <Text style={{ fontSize: 18 }}>♪</Text>
            </TouchableOpacity>
          </View>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const st = StyleSheet.create({
  safe: { flex: 1 },
  header: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 20, paddingVertical: 16, borderBottomWidth: 1,
  },
  backBtn: { padding: 4 },
  headerTitle: { fontSize: 20, fontWeight: '800' },
  headerSub: { fontSize: 12, marginTop: 2 },
  scroll: { padding: 16, paddingBottom: 100 },

  section: { marginBottom: 28 },

  platformBanner: {
    borderRadius: 16, marginBottom: 0,
    overflow: 'hidden',
    borderBottomLeftRadius: 0, borderBottomRightRadius: 0,
  },
  bannerInner: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 16, paddingVertical: 14, gap: 12,
  },
  platformIconWrap: { },
  ytPlay: {
    width: 46, height: 46, borderRadius: 12,
    justifyContent: 'center', alignItems: 'center',
  },
  platformName: { color: '#fff', fontSize: 16, fontWeight: '800' },
  platformHandle: { color: 'rgba(255,255,255,0.7)', fontSize: 13, marginTop: 1 },
  followBtn: {
    backgroundColor: '#fff',
    paddingHorizontal: 14, paddingVertical: 8,
    borderRadius: 20,
  },
  followBtnText: { fontSize: 13, fontWeight: '800' },

  descCard: {
    padding: 14,
    borderLeftWidth: 1, borderRightWidth: 1,
  },
  descText: { fontSize: 13, lineHeight: 20 },

  embedWrap: {
    borderLeftWidth: 1, borderRightWidth: 1,
    overflow: 'hidden',
  },
  nativePreview: {
    height: 120, borderRadius: 0,
    borderLeftWidth: 1, borderRightWidth: 1,
    justifyContent: 'center', alignItems: 'center', gap: 8,
  },
  nativePreviewText: { fontSize: 14, opacity: 0.6 },

  openBtn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: 8, paddingVertical: 13, borderRadius: 12,
    marginTop: 10,
  },
  openBtnText: { color: '#fff', fontSize: 15, fontWeight: '800', flex: 1 },

  // TikTok custom preview
  ttPreview: {
    height: 160,
    backgroundColor: '#0A0A0A',
    borderLeftWidth: 1, borderRightWidth: 1,
    overflow: 'hidden',
    justifyContent: 'center',
  },
  ttGlow1: {
    position: 'absolute', top: -30, right: -30,
    width: 120, height: 120, borderRadius: 60,
    backgroundColor: 'rgba(105,201,208,0.12)',
  },
  ttGlow2: {
    position: 'absolute', bottom: -20, left: 20,
    width: 100, height: 100, borderRadius: 50,
    backgroundColor: 'rgba(254,44,85,0.10)',
  },
  ttContent: { padding: 20, gap: 12 },
  ttHandleRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  ttIcon: {
    width: 44, height: 44, borderRadius: 22,
    backgroundColor: '#1a1a1a',
    justifyContent: 'center', alignItems: 'center',
    borderWidth: 1.5, borderColor: '#FE2C55',
  },
  ttHandle: { color: '#fff', fontSize: 16, fontWeight: '800' },
  ttSub: { fontSize: 12, marginTop: 1 },
  ttStatsRow: {
    flexDirection: 'row', alignItems: 'center', gap: 0,
  },
  ttStat: { flex: 1, alignItems: 'center', gap: 2 },
  ttStatNum: { fontSize: 18 },
  ttStatLbl: { color: '#64748B', fontSize: 11 },
  ttStatDivider: { width: 1, height: 28, backgroundColor: '#1E293B' },
  ttOpenRow: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-end', gap: 8,
  },
  ttOpenLabel: { color: '#64748B', fontSize: 13 },

  // All platforms row
  allRow: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    borderTopWidth: 1, paddingTop: 20, marginTop: 4,
  },
  allRowLabel: { fontSize: 13 },
  allBtns: { flexDirection: 'row', gap: 10 },
  allBtn: {
    width: 44, height: 44, borderRadius: 22,
    justifyContent: 'center', alignItems: 'center',
  },
});
