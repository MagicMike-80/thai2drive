import React, { useRef, useEffect } from 'react';
import { View, StyleSheet, TouchableOpacity, Text, Platform, ScrollView, Animated } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useAppStore } from '../store/appStore';
import { BlurView } from 'expo-blur';

interface BottomNavBarProps {
  activeTab: 'home' | 'categories' | 'teacher' | 'history' | 'signs' | 'book' | 'bookmarks' | 'settings' | 'none';
}

// Neon gradient colors for active tab border — matches web app's conic-gradient (#00F5FF → #FF00E5 → #00F5FF)
const NEON_GRADIENT = ['#00F5FF', '#FF00E5', '#00F5FF'] as const;

const TABS = [
  { id: 'home', route: '/', activeIcon: 'home', inactiveIcon: 'home-outline' },
  { id: 'categories', route: '/categories', activeIcon: 'grid', inactiveIcon: 'grid-outline' },
  { id: 'history', route: '/history', activeIcon: 'time', inactiveIcon: 'time-outline' },
  { id: 'teacher', route: '/teacher', activeIcon: 'chatbubbles', inactiveIcon: 'chatbubbles-outline' },
  { id: 'signs', route: '/signs', activeIcon: 'warning', inactiveIcon: 'warning-outline' },
  { id: 'book', route: '/book', activeIcon: 'book', inactiveIcon: 'book-outline' },
  { id: 'bookmarks', route: '/bookmarks', activeIcon: 'bookmark', inactiveIcon: 'bookmark-outline' },
  { id: 'settings', route: '/settings', activeIcon: 'settings', inactiveIcon: 'settings-outline' },
] as const;

const LABELS: Record<string, Record<string, string>> = {
  no: {
    home: 'Hjem',
    categories: 'Kategorier',
    history: 'Historikk',
    teacher: 'Michael',
    signs: 'Skilt',
    book: 'Studiebok',
    bookmarks: 'Bokmerker',
    settings: 'Innstillinger',
  },
  th: {
    home: 'หน้าหลัก',
    categories: 'หมวดหมู่',
    history: 'ประวัติ',
    teacher: 'ครูสอนขับ',
    signs: 'ป้าย',
    book: 'หนังสือเรียน',
    bookmarks: 'บุ๊กมาร์ก',
    settings: 'การตั้งค่า',
  },
  en: {
    home: 'Home',
    categories: 'Categories',
    history: 'History',
    teacher: 'Teacher',
    signs: 'Signs',
    book: 'Study Book',
    bookmarks: 'Bookmarks',
    settings: 'Settings',
  },
};

function ActiveTabContent({ tab, label, iconColor, labelColor }: {
  tab: typeof TABS[number];
  label: string;
  iconColor: string;
  labelColor: string;
}) {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Subtle pulse on mount for active tab
    Animated.sequence([
      Animated.timing(scaleAnim, { toValue: 1.15, duration: 150, useNativeDriver: true }),
      Animated.spring(scaleAnim, { toValue: 1.2, useNativeDriver: true, speed: 8, bounciness: 4 }),
    ]).start();
  }, []);

  return (
    <LinearGradient
      colors={NEON_GRADIENT}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.gradientBorder}
    >
      <View style={[styles.tabInner, { backgroundColor: 'rgba(11,18,38,0.90)' }]}>
        <Animated.View style={{ transform: [{ scale: scaleAnim }, { translateY: -1 }] }}>
          <Ionicons
            name={tab.activeIcon}
            size={24}
            color={iconColor}
          />
        </Animated.View>
        <Text style={[styles.label, { color: labelColor }]}>
          {label}
        </Text>
      </View>
    </LinearGradient>
  );
}

function InactiveTabContent({ tab, label, iconColor, labelColor }: {
  tab: typeof TABS[number];
  label: string;
  iconColor: string;
  labelColor: string;
}) {
  return (
    <View style={[styles.tabInner, styles.inactiveTabInner, { backgroundColor: 'rgba(255,255,255,0.02)', borderColor: 'rgba(255,255,255,0.04)' }]}>
      <Ionicons
        name={tab.inactiveIcon}
        size={22}
        color={iconColor}
      />
      <Text style={[styles.label, { color: labelColor }]}>
        {label}
      </Text>
    </View>
  );
}

export function BottomNavBar({ activeTab }: BottomNavBarProps) {
  const router = useRouter();
  const { language, colors: c } = useAppStore();
  const scrollRef = useRef<ScrollView>(null);

  const labels = LABELS[language] || {};

  const navigateTo = (route: string) => {
    router.replace(route as any);
  };

  const renderContent = () => (
    <ScrollView
      ref={scrollRef}
      horizontal
      showsHorizontalScrollIndicator={false}
      snapToInterval={undefined}
      scrollEventThrottle={16}
      contentContainerStyle={styles.scrollContent}
      style={styles.scroll}
    >
      {TABS.map((tab) => {
        const active = activeTab === tab.id;
        const iconColor = active ? '#00F5FF' : c.textMuted;
        const labelColor = active ? '#00F5FF' : c.textMuted;
        const label = labels[tab.id] || tab.id;

        return (
          <TouchableOpacity
            key={tab.id}
            testID={`nav-${tab.id}`}
            onPress={() => navigateTo(tab.route)}
            activeOpacity={0.7}
            style={[
              styles.tabWrap,
              active && styles.activeTabWrap,
            ]}
          >
            {active ? (
              <ActiveTabContent tab={tab} label={label} iconColor={iconColor} labelColor={labelColor} />
            ) : (
              <InactiveTabContent tab={tab} label={label} iconColor={iconColor} labelColor={labelColor} />
            )}
          </TouchableOpacity>
        );
      })}
    </ScrollView>
  );

  // iOS: BlurView for glassmorphic effect
  // Android/Web: solid dark background using theme card color
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
      <View style={[styles.blur, { backgroundColor: 'rgba(7,12,26,0.92)', borderColor: 'rgba(255,255,255,0.06)' }]}>
        {renderContent()}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.35,
    shadowRadius: 12,
  },
  blur: {
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.06)',
    paddingVertical: 6,
    paddingBottom: Platform.OS === 'ios' ? 24 : 10,
  },
  scroll: {
    overflow: 'visible',
  },
  scrollContent: {
    paddingHorizontal: 8,
    gap: 8,
    alignItems: 'center',
  },
  tabWrap: {
    width: 80,
    alignItems: 'center',
  },
  activeTabWrap: {
    // Matches web: translateY(-2px) on active tab
    transform: [{ translateY: -2 }],
  },
  gradientBorder: {
    padding: 1.5,
    borderRadius: 14,
    // Match web glow: box-shadow: 0 0 14px rgba(0,245,255,0.22)
    shadowColor: '#00F5FF',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.22,
    shadowRadius: 14,
    elevation: 6,
  },
  tabInner: {
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 6,
    paddingHorizontal: 6,
    borderRadius: 13,
    gap: 3,
    minHeight: 50,
    minWidth: 70,
  },
  inactiveTabInner: {
    borderWidth: 1,
    borderRadius: 14,
    // Match web inactive shadow: inset 0 1px 1px rgba(255,255,255,0.03), 0 2px 4px rgba(0,0,0,0.15)
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 3,
  },
  label: {
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.2,
    textAlign: 'center',
  },
});
