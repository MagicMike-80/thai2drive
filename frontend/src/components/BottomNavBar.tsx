import React from 'react';
import { View, StyleSheet, TouchableOpacity, Text, Platform, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../store/appStore';
import { BlurView } from 'expo-blur';

interface BottomNavBarProps {
  activeTab: 'home' | 'categories' | 'teacher' | 'stats' | 'history' | 'research';
}

const TABS = [
  { id: 'home', route: '/', activeIcon: 'home', inactiveIcon: 'home-outline' },
  { id: 'categories', route: '/categories', activeIcon: 'grid', inactiveIcon: 'grid-outline' },
  { id: 'teacher', route: '/teacher', activeIcon: 'chatbubbles', inactiveIcon: 'chatbubbles-outline' },
  { id: 'stats', route: '/stats', activeIcon: 'bar-chart', inactiveIcon: 'bar-chart-outline' },
  { id: 'history', route: '/history', activeIcon: 'time', inactiveIcon: 'time-outline' },
  { id: 'research', route: '/research', activeIcon: 'headset', inactiveIcon: 'headset-outline' },
] as const;

const LABELS: Record<string, Record<string, string>> = {
  no: {
    home: 'Hjem',
    categories: 'Kategorier',
    teacher: 'Lærer',
    stats: 'Statistikk',
    history: 'Historikk',
    research: 'Research',
  },
  th: {
    home: 'หน้าหลัก',
    categories: 'หมวดหมู่',
    teacher: 'ครูสอนขับ',
    stats: 'สถิติ',
    history: 'ประวัติ',
    research: 'ข้อมูลวิจัย',
  },
  en: {
    home: 'Home',
    categories: 'Categories',
    teacher: 'Teacher',
    stats: 'Stats',
    history: 'History',
    research: 'Research',
  },
};

export function BottomNavBar({ activeTab }: BottomNavBarProps) {
  const router = useRouter();
  const { language, colors: c } = useAppStore();

  const labels = LABELS[language] || LABELS.en;

  const navigateTo = (route: string) => {
    router.replace(route as any);
  };

  const renderContent = () => (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      style={styles.scrollView}
      contentContainerStyle={styles.container}
    >
      {TABS.map((tab) => {
        const active = activeTab === tab.id;
        return (
          <TouchableOpacity
            key={tab.id}
            testID={`nav-${tab.id}`}
            style={[
              styles.tab,
              active && {
                backgroundColor: c.accentBg,
                borderColor: c.accent,
                borderWidth: 1.5,
              },
            ]}
            onPress={() => navigateTo(tab.route)}
            activeOpacity={0.7}
          >
            <Ionicons
              name={active ? tab.activeIcon : tab.inactiveIcon}
              size={18}
              color={active ? c.accent : c.textMuted}
            />
            <Text style={[styles.label, { color: active ? c.accent : c.textMuted }]}>
              {labels[tab.id] || tab.id}
            </Text>
          </TouchableOpacity>
        );
      })}
    </ScrollView>
  );

  // Modern dark glassmorphic styling:
  // Using BlurView on iOS for native blurring, falling back to styled transparent views.
  if (Platform.OS === 'ios') {
    return (
      <View style={styles.wrapper}>
        <BlurView intensity={80} tint="dark" style={[styles.blur, { borderColor: c.cardBorder }]}>
          {renderContent()}
        </BlurView>
      </View>
    );
  }

  return (
    <View style={styles.wrapper}>
      <View style={[styles.blur, { backgroundColor: 'rgba(11, 18, 34, 0.92)', borderColor: c.cardBorder }]}>
        {renderContent()}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    zIndex: 1000,
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
  },
  blur: {
    borderRadius: 24,
    borderWidth: 1.5,
    overflow: 'hidden',
  },
  scrollView: {
    flexGrow: 0,
  },
  container: {
    flexDirection: 'row',
    height: 64,
    alignItems: 'center',
    paddingHorizontal: 12,
    gap: 8,
  },
  tab: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 40,
    paddingHorizontal: 14,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'transparent',
    gap: 6,
  },
  label: {
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 0.2,
  },
});
