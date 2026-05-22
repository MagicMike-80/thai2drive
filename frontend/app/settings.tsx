import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Switch, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { ThemeMode } from '../src/theme';
import { LanguageSwitcher } from '../src/components/LanguageSwitcher';
import { AppBrand } from '../src/components/AppBrand';

const TRANSLATIONS: Record<string, Record<string, string>> = {
  no: { title: 'Innstillinger', sound: 'Lyd og vibrasjon', theme: 'Tema', language: 'Språk', light: 'Lys', dark: 'Mørk', system: 'System', back: 'Tilbake', soundOn: 'Lydeffekter', soundOff: 'Lydeffekter', account: 'Konto', logout: 'Logg ut', login: 'Logg inn', premium: 'Premium', admin: 'Admin', library: 'Bibliotek', history: 'Historikk', bookmarks: 'Bokmerker', feedbackStyle: 'Tilbakemeldingsstil', styleSoft: 'Myk', styleSoftHint: 'Rask og diskret', styleStrong: 'Sterk', styleStrongHint: 'Klar "kliiing"-effekt', haptics: 'Vibrasjon', hapticsOn: 'På' },
  th: { title: 'ตั้งค่า', sound: 'เสียงและการสั่น', theme: 'ธีม', language: 'ภาษา', light: 'สว่าง', dark: 'มืด', system: 'ระบบ', back: 'กลับ', soundOn: 'เสียงเอฟเฟกต์', soundOff: 'เสียงเอฟเฟกต์', account: 'บัญชี', logout: 'ออกจากระบบ', login: 'เข้าสู่ระบบ', premium: 'พรีเมียม', admin: 'แอดมิน', library: 'คลัง', history: 'ประวัติ', bookmarks: 'บุ๊คมาร์ค', feedbackStyle: 'สไตล์เสียงตอบรับ', styleSoft: 'เบา', styleSoftHint: 'สั้น ไม่รบกวน', styleStrong: 'เข้ม', styleStrongHint: 'เสียงกริ๊งชัด', haptics: 'การสั่น', hapticsOn: 'เปิด' },
  en: { title: 'Settings', sound: 'Sound & Haptics', theme: 'Theme', language: 'Language', light: 'Light', dark: 'Dark', system: 'System', back: 'Back', soundOn: 'Sound effects', soundOff: 'Sound effects', account: 'Account', logout: 'Log Out', login: 'Log In', premium: 'Premium', admin: 'Admin', library: 'Library', history: 'History', bookmarks: 'Bookmarks', feedbackStyle: 'Feedback style', styleSoft: 'Soft', styleSoftHint: 'Quick & subtle', styleStrong: 'Strong', styleStrongHint: 'Bright "kliiing"', haptics: 'Haptic vibration', hapticsOn: 'On' },
};

const THEME_OPTIONS: { mode: ThemeMode; icon: keyof typeof Ionicons.glyphMap }[] = [
  { mode: 'light', icon: 'sunny-outline' },
  { mode: 'dark', icon: 'moon-outline' },
  { mode: 'system', icon: 'phone-portrait-outline' },
];

export default function SettingsScreen() {
  const router = useRouter();
  const { language, colors, themeMode, setThemeMode, soundEnabled, setSoundEnabled, soundStyle, setSoundStyle, hapticsEnabled, setHapticsEnabled, user, isPremium, logout, isAuthenticated } = useAppStore();
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;
  const isDark = colors.bg === '#0F172A' || colors.bg === '#0B1222';

  // Preview the selected sound style when user taps a chip
  const previewSound = async (style: 'default' | 'strong') => {
    try {
      const mod = await import('../src/sounds');
      mod.playCorrectSound({ soundEnabled: true, hapticsEnabled, style });
    } catch {}
  };

  const handleLogout = async () => {
    await logout();
    router.replace('/');
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.bg }]}>
      {/* Subtle gradient background — matches categories screen */}
      <LinearGradient
        colors={isDark ? ['#0B1222', '#0F172A', '#0B1222'] : ['#F4F8FD', '#FFFFFF', '#EEF5FB']}
        locations={[0, 0.5, 1]}
        style={StyleSheet.absoluteFill}
      />
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: colors.divider }]}>
        <View style={styles.headerLeft}>
          <TouchableOpacity testID="settings-back-btn" style={[styles.backBtn, { backgroundColor: colors.card }]} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={22} color={colors.text} />
          </TouchableOpacity>
          <AppBrand size="md" />
        </View>
        <Text style={[styles.title, { color: colors.text }]}>{t.title}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Account Section */}
        <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.cardBorder }]}>
          <View style={styles.sectionHeader}>
            <Ionicons name="person-circle-outline" size={20} color={colors.accent} />
            <Text style={[styles.sectionTitle, { color: colors.text }]}>{t.account}</Text>
          </View>
          {user ? (
            <View style={styles.accountInfo}>
              <View style={[styles.emailRow, { backgroundColor: colors.bg }]}>
                <Ionicons name="mail-outline" size={16} color={colors.textMuted} />
                <Text style={[styles.emailText, { color: colors.text }]}>{user.email}</Text>
              </View>
              <View style={styles.badgeRow}>
                {isPremium && (
                  <View style={[styles.badge, { backgroundColor: colors.accentBg }]}>
                    <Ionicons name="diamond" size={12} color={colors.accent} />
                    <Text style={[styles.badgeText, { color: colors.accent }]}>{t.premium}</Text>
                  </View>
                )}
                {user.is_admin && (
                  <View style={[styles.badge, { backgroundColor: `${colors.correct}15` }]}>
                    <Ionicons name="shield-checkmark" size={12} color={colors.correct} />
                    <Text style={[styles.badgeText, { color: colors.correct }]}>{t.admin}</Text>
                  </View>
                )}
              </View>
            </View>
          ) : (
            <TouchableOpacity
              testID="settings-login-btn"
              style={[styles.loginBtn, { backgroundColor: colors.accentBg, borderColor: colors.accent }]}
              onPress={() => router.push('/login')}
              activeOpacity={0.8}
            >
              <Ionicons name="log-in-outline" size={18} color={colors.accent} />
              <Text style={[styles.loginBtnText, { color: colors.accent }]}>{t.login}</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* BUILD INFO — shows which backend URL the APK is hitting. Helps diagnose stale builds. */}
        <TouchableOpacity
          activeOpacity={0.9}
          onLongPress={async () => {
            const url = process.env.EXPO_PUBLIC_BACKEND_URL || '(not set)';
            try {
              const r = await fetch(url + '/api/_whoami', { method: 'GET' });
              const txt = await r.text();
              alert(`Backend URL baked in:\n${url}\n\n/api/_whoami → HTTP ${r.status}\n${txt.slice(0, 300)}`);
            } catch (e: any) {
              alert(`Backend URL baked in:\n${url}\n\nCannot reach: ${e.message || e}`);
            }
          }}
          style={[styles.section, { backgroundColor: colors.card, borderColor: colors.cardBorder }]}
        >
          <View style={styles.sectionHeader}>
            <Ionicons name="server-outline" size={18} color={colors.textMuted} />
            <Text style={[styles.sectionTitle, { color: colors.textMuted, fontSize: 12 }]}>BUILD INFO</Text>
          </View>
          <Text style={{ color: colors.text, fontSize: 11, fontFamily: 'monospace', marginTop: 4 }} selectable>
            API: {process.env.EXPO_PUBLIC_BACKEND_URL || '(not set)'}
          </Text>
          <Text style={{ color: colors.textMuted, fontSize: 10, marginTop: 6 }}>
            Long-press to test connectivity
          </Text>
        </TouchableOpacity>

        {/* Library (History + Bookmarks) */}
        <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.cardBorder }]}>
          <View style={styles.sectionHeader}>
            <Ionicons name="library-outline" size={20} color={colors.accent} />
            <Text style={[styles.sectionTitle, { color: colors.text }]}>{t.library}</Text>
          </View>
          <TouchableOpacity testID="settings-history-btn" style={styles.linkRow} onPress={() => router.push('/history')} activeOpacity={0.7}>
            <Ionicons name="time-outline" size={18} color={colors.textSecondary} />
            <Text style={[styles.linkLabel, { color: colors.text }]}>{t.history}</Text>
            <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
          </TouchableOpacity>
          <View style={[styles.innerDivider, { backgroundColor: colors.divider }]} />
          <TouchableOpacity testID="settings-bookmarks-btn" style={styles.linkRow} onPress={() => router.push('/bookmarks')} activeOpacity={0.7}>
            <Ionicons name="bookmark-outline" size={18} color={colors.textSecondary} />
            <Text style={[styles.linkLabel, { color: colors.text }]}>{t.bookmarks}</Text>
            <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
          </TouchableOpacity>
        </View>

        {/* Language Selection */}
        <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.cardBorder }]}>
          <View style={styles.sectionHeader}>
            <Ionicons name="language-outline" size={20} color={colors.accent} />
            <Text style={[styles.sectionTitle, { color: colors.text }]}>{t.language}</Text>
          </View>
          <View style={styles.languageRow}>
            <LanguageSwitcher size="md" align="flex-start" />
          </View>
        </View>

        {/* Sound + Haptics */}
        <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.cardBorder }]}>
          <View style={styles.sectionHeader}>
            <Ionicons name="volume-medium-outline" size={20} color={colors.accent} />
            <Text style={[styles.sectionTitle, { color: colors.text }]}>{t.sound}</Text>
          </View>

          {/* Sound master toggle */}
          <View style={styles.row}>
            <Text style={[styles.rowLabel, { color: colors.textSecondary }]}>
              {t.soundOn}
            </Text>
            <Switch
              testID="sound-toggle"
              value={soundEnabled}
              onValueChange={setSoundEnabled}
              trackColor={{ false: colors.letterBg, true: colors.accent }}
              thumbColor="#FFFFFF"
            />
          </View>

          {/* Style selector — only matters if sound is on */}
          <View style={[styles.innerDivider, { backgroundColor: colors.divider }]} />
          <Text style={[styles.groupLabel, { color: colors.textMuted }]}>{t.feedbackStyle}</Text>
          <View style={styles.styleRow}>
            {(['default', 'strong'] as const).map((style) => {
              const active = soundStyle === style;
              const label = style === 'default' ? t.styleSoft : t.styleStrong;
              const hint  = style === 'default' ? t.styleSoftHint : t.styleStrongHint;
              const icon  = style === 'default' ? 'musical-note-outline' : 'flash-outline';
              return (
                <TouchableOpacity
                  key={style}
                  testID={`sound-style-${style}`}
                  activeOpacity={0.75}
                  disabled={!soundEnabled && !hapticsEnabled}
                  style={[
                    styles.styleChip,
                    {
                      borderColor: active ? colors.accent : colors.cardBorder,
                      backgroundColor: active ? colors.accentBg : 'transparent',
                      opacity: (soundEnabled || hapticsEnabled) ? 1 : 0.4,
                    },
                  ]}
                  onPress={() => { setSoundStyle(style); if (soundEnabled) previewSound(style); }}
                >
                  <Ionicons name={icon as any} size={18} color={active ? colors.accent : colors.textMuted} />
                  <Text style={[styles.styleLabel, { color: active ? colors.accent : colors.text }]}>{label}</Text>
                  <Text style={[styles.styleHint, { color: colors.textMuted }]}>{hint}</Text>
                </TouchableOpacity>
              );
            })}
          </View>

          {/* Haptics toggle */}
          <View style={[styles.innerDivider, { backgroundColor: colors.divider }]} />
          <View style={styles.row}>
            <View style={{ flex: 1 }}>
              <Text style={[styles.rowLabel, { color: colors.textSecondary }]}>{t.haptics}</Text>
            </View>
            <Switch
              testID="haptics-toggle"
              value={hapticsEnabled}
              onValueChange={setHapticsEnabled}
              trackColor={{ false: colors.letterBg, true: colors.accent }}
              thumbColor="#FFFFFF"
            />
          </View>
        </View>

        {/* Theme Selection */}
        <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.cardBorder }]}>
          <View style={styles.sectionHeader}>
            <Ionicons name="color-palette-outline" size={20} color={colors.accent} />
            <Text style={[styles.sectionTitle, { color: colors.text }]}>{t.theme}</Text>
          </View>
          <View style={styles.themeRow}>
            {THEME_OPTIONS.map((opt) => {
              const active = themeMode === opt.mode;
              const label = t[opt.mode] || opt.mode;
              return (
                <TouchableOpacity
                  key={opt.mode}
                  testID={`theme-btn-${opt.mode}`}
                  style={[
                    styles.themeOption,
                    { borderColor: active ? colors.accent : colors.cardBorder, backgroundColor: active ? colors.accentBg : 'transparent' },
                  ]}
                  onPress={() => setThemeMode(opt.mode)}
                  activeOpacity={0.7}
                >
                  <Ionicons name={opt.icon} size={20} color={active ? colors.accent : colors.textMuted} />
                  <Text style={[styles.themeLabel, { color: active ? colors.accent : colors.textSecondary }]}>
                    {label}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>

        {/* Logout - only shown when logged in */}
        {isAuthenticated && (
          <TouchableOpacity testID="logout-btn" style={[styles.logoutBtn, { borderColor: colors.incorrect }]} onPress={handleLogout} activeOpacity={0.7}>
            <Ionicons name="log-out-outline" size={20} color={colors.incorrect} />
            <Text style={[styles.logoutText, { color: colors.incorrect }]}>{t.logout}</Text>
          </TouchableOpacity>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1 },
  headerLeft: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  backBtn: { width: 40, height: 40, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 18, fontWeight: '700' },
  content: { padding: 16, gap: 12 },
  section: { borderRadius: 16, padding: 16, borderWidth: 1 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 14 },
  sectionTitle: { fontSize: 15, fontWeight: '700' },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  rowLabel: { fontSize: 14 },
  themeRow: { flexDirection: 'row', gap: 10 },
  themeOption: { flex: 1, alignItems: 'center', paddingVertical: 14, borderRadius: 12, borderWidth: 1.5, gap: 6 },
  themeLabel: { fontSize: 13, fontWeight: '600' },
  accountInfo: { gap: 10 },
  emailRow: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 12, paddingVertical: 10, borderRadius: 10 },
  emailText: { fontSize: 14, fontWeight: '500' },
  badgeRow: { flexDirection: 'row', gap: 8 },
  badge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  badgeText: { fontSize: 12, fontWeight: '700' },
  logoutBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 8, borderRadius: 14, borderWidth: 1.5, paddingVertical: 14, marginTop: 8 },
  logoutText: { fontSize: 15, fontWeight: '700' },
  loginBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 8, borderRadius: 12, borderWidth: 1.5, paddingVertical: 12 },
  loginBtnText: { fontSize: 14, fontWeight: '700' },
  languageRow: { alignItems: 'flex-start' },
  linkRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10, gap: 12 },
  linkLabel: { flex: 1, fontSize: 15, fontWeight: '500' },
  innerDivider: { height: 1, opacity: 0.35, marginVertical: 10 },
  groupLabel: { fontSize: 11, fontWeight: '700', letterSpacing: 1, textTransform: 'uppercase', marginBottom: 10, marginTop: 2 },
  styleRow: { flexDirection: 'row', gap: 10 },
  styleChip: { flex: 1, paddingVertical: 12, paddingHorizontal: 12, borderWidth: 1.5, borderRadius: 12, alignItems: 'flex-start', gap: 2 },
  styleLabel: { fontSize: 14, fontWeight: '700', marginTop: 4 },
  styleHint: { fontSize: 11, marginTop: 1 },
});
