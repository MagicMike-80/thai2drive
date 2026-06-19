import React from 'react';
import { View, StyleSheet, TouchableOpacity, Text, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../store/appStore';
import { BlurView } from 'expo-blur';

interface BottomNavBarProps {
  activeTab: 'home' | 'research';
}

const LABELS: Record<string, { home: string; research: string }> = {
  no: { home: 'Hjem', research: 'The Research' },
  th: { home: 'หน้าหลัก', research: 'The Research' },
  en: { home: 'Home', research: 'The Research' },
};

export function BottomNavBar({ activeTab }: BottomNavBarProps) {
  const router = useRouter();
  const { language, colors: c } = useAppStore();

  const labels = LABELS[language] || LABELS.en;

  const navigateTo = (route: string) => {
    router.replace(route as any);
  };

  const renderContent = () => (
    <View style={styles.container}>
      <TouchableOpacity
        testID="nav-home"
        style={styles.tab}
        onPress={() => navigateTo('/')}
        activeOpacity={0.7}
      >
        <Ionicons
          name={activeTab === 'home' ? 'home' : 'home-outline'}
          size={22}
          color={activeTab === 'home' ? c.accent : c.textMuted}
        />
        <Text style={[styles.label, { color: activeTab === 'home' ? c.accent : c.textMuted }]}>
          {labels.home}
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        testID="nav-research"
        style={styles.tab}
        onPress={() => navigateTo('/research')}
        activeOpacity={0.7}
      >
        <Ionicons
          name={activeTab === 'research' ? 'headset' : 'headset-outline'}
          size={22}
          color={activeTab === 'research' ? c.accent : c.textMuted}
        />
        <Text style={[styles.label, { color: activeTab === 'research' ? c.accent : c.textMuted }]}>
          {labels.research}
        </Text>
      </TouchableOpacity>
    </View>
  );

  // Modern dark glassmorphic styling:
  // Using BlurView on iOS for native blurring, falling back to styled transparent views.
  if (Platform.OS === 'ios') {
    return (
      <View style={styles.wrapper}>
        <BlurView intensity={80} tint="dark" style={[styles.blur, { borderColor: 'rgba(255, 255, 255, 0.15)' }]}>
          {renderContent()}
        </BlurView>
      </View>
    );
  }

  return (
    <View style={styles.wrapper}>
      <View style={[styles.blur, { backgroundColor: 'rgba(15, 23, 42, 0.85)', borderColor: 'rgba(255, 255, 255, 0.12)' }]}>
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
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.4,
    shadowRadius: 15,
  },
  blur: {
    borderRadius: 24,
    borderWidth: 1,
    overflow: 'hidden',
  },
  container: {
    flexDirection: 'row',
    height: 64,
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingHorizontal: 12,
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    gap: 4,
  },
  label: {
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.2,
  },
});
