import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Switch, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { ThemeMode } from '../src/theme';
import { LanguageSwitcher } from '../src/components/LanguageSwitcher';

const TRANSLATIONS: Record<string, Record<string, string>> = {
  no: { title: 'Innstillinger', sound: 'Lyd', theme: 'Tema', language: 'Språk', light: 'Lys', dark: 'Mørk', system: 'System', back: 'Tilbake', soundOn: 'Lydeffekter på', soundOff: 'Lydeffekter av', account: 'Konto', logout: 'Logg ut', login: 'Logg inn', premium: 'Premium', admin: 'Admin' },
  th: { title: 'ตั้งค่า', sound: 'เสียง', theme: 'ธีม', language: 'ภาษา', light: 'สว่าง', dark: 'มืด', system: 'ระบบ', back: 'กลับ', soundOn: 'เปิดเสียง', soundOff: 'ปิดเสียง', account: 'บัญชี', logout: 'ออกจากระบบ', login: 'เข้าสู่ระบบ', premium: 'พรีเมียม', admin: 'แอดมิน' },
  en: { title: 'Settings', sound: 'Sound', theme: 'Theme', language: 'Language', light: 'Light', dark: 'Dark', system: 'System', back: 'Back', soundOn: 'Sound effects on', soundOff: 'Sound effects off', account: 'Account', logout: 'Log Out', login: 'Log In', premium: 'Premium', admin: 'Admin' },
};

const THEME_OPTIONS: { mode: ThemeMode; icon: keyof typeof Ionicons.glyphMap }[] = [
  { mode: 'light', icon: 'sunny-outline' },
  { mode: 'dark', icon: 'moon-outline' },
  { mode: 'system', icon: 'phone-portrait-outline' },
];

export default function SettingsScreen() {
  const router = useRouter();
  const { language, colors, themeMode, setThemeMode, soundEnabled, setSoundEnabled, user, isPremium, logout, isAuthenticated } = useAppStore();
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

  const handleLogout = async () => {
    await logout();
    router.replace('/');
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.bg }]}>
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: colors.divider }]}>
        <TouchableOpacity testID="settings-back-btn" style={[styles.backBtn, { backgroundColor: colors.card }]} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={22} color={colors.text} />
        </TouchableOpacity>
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

        {/* Sound Toggle */}
        <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.cardBorder }]}>
          <View style={styles.sectionHeader}>
            <Ionicons name="volume-medium-outline" size={20} color={colors.accent} />
            <Text style={[styles.sectionTitle, { color: colors.text }]}>{t.sound}</Text>
          </View>
          <View style={styles.row}>
            <Text style={[styles.rowLabel, { color: colors.textSecondary }]}>
              {soundEnabled ? t.soundOn : t.soundOff}
            </Text>
            <Switch
              testID="sound-toggle"
              value={soundEnabled}
              onValueChange={setSoundEnabled}
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
});
