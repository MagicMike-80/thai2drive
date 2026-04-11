import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useAppStore } from '../src/store/appStore';

export default function RootLayout() {
  const [isReady, setIsReady] = useState(false);
  const initDeviceId = useAppStore((s) => s.initDeviceId);
  const colors = useAppStore((s) => s.colors);
  const isDark = useAppStore((s) => s.isDark);

  useEffect(() => {
    (async () => {
      try { await initDeviceId(); } catch (e) { console.error(e); }
      finally { setIsReady(true); }
    })();
  }, []);

  if (!isReady) {
    return (
      <SafeAreaProvider>
        <View style={[styles.loading, { backgroundColor: colors.bg }]}>
          <ActivityIndicator size="large" color={colors.accent} />
        </View>
      </SafeAreaProvider>
    );
  }

  return (
    <SafeAreaProvider>
      <StatusBar style={isDark ? 'light' : 'dark'} />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: colors.bg },
          animation: 'slide_from_right',
        }}
      >
        <Stack.Screen name="index" />
        <Stack.Screen name="categories" />
        <Stack.Screen name="quiz" />
        <Stack.Screen name="results" />
        <Stack.Screen name="history" />
        <Stack.Screen name="bookmarks" />
        <Stack.Screen name="settings" />
      </Stack>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
});
