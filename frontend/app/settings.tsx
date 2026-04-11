import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Switch } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { ThemeMode } from '../src/theme';

const TRANSLATIONS: Record<string, Record<string, string>> = {
  no: { title: 'Innstillinger', sound: 'Lyd', theme: 'Tema', light: 'Lys', dark: 'Mørk', system: 'System', back: 'Tilbake', soundOn: 'Lydeffekter på', soundOff: 'Lydeffekter av' },
  th: { title: 'ตั้งค่า', sound: 'เสียง', theme: 'ธีม', light: 'สว่าง', dark: 'มืด', system: 'ระบบ', back: 'กลับ', soundOn: 'เปิดเสียง', soundOff: 'ปิดเสียง' },
  en: { title: 'Settings', sound: 'Sound', theme: 'Theme', light: 'Light', dark: 'Dark', system: 'System', back: 'Back', soundOn: 'Sound effects on', soundOff: 'Sound effects off' },
};

const THEME_OPTIONS: { mode: ThemeMode; icon: keyof typeof Ionicons.glyphMap }[] = [
  { mode: 'light', icon: 'sunny-outline' },
  { mode: 'dark', icon: 'moon-outline' },
  { mode: 'system', icon: 'phone-portrait-outline' },
];

export default function SettingsScreen() {
  const router = useRouter();
  const { language, colors, themeMode, setThemeMode, soundEnabled, setSoundEnabled } = useAppStore();
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

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

      <View style={styles.content}>
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
      </View>
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
});
