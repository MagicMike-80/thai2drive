import { Stack, useRouter, useSegments } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useAppStore } from '../src/store/appStore';

const AUTH_SCREENS = ['login', 'signup', 'forgot-password'];

function useAuthRedirect() {
  const segments = useSegments();
  const router = useRouter();
  const isAuthenticated = useAppStore((s) => s.isAuthenticated);
  const authLoading = useAppStore((s) => s.authLoading);

  useEffect(() => {
    if (authLoading) return;

    const currentScreen = segments[0] || '';
    const onAuthScreen = AUTH_SCREENS.includes(currentScreen);

    // Only redirect: if already logged in and stuck on auth screen → go home
    if (isAuthenticated && onAuthScreen) {
      router.replace('/');
    }
    // No forced login redirect — app is freely accessible
  }, [isAuthenticated, authLoading, segments]);
}

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
    // Pre-warm answer-feedback sounds so the first tap has no hitch
    (async () => {
      try {
        const mod = await import('../src/sounds');
        const style = useAppStore.getState().soundStyle;
        await mod.prewarmSounds(style);
      } catch {}
    })();
  }, []);

  useAuthRedirect();

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
        {/* Auth screens */}
        <Stack.Screen name="login" options={{ animation: 'fade' }} />
        <Stack.Screen name="signup" />
        <Stack.Screen name="forgot-password" />
        {/* App screens */}
        <Stack.Screen name="index" options={{ animation: 'fade' }} />
        <Stack.Screen name="categories" />
        <Stack.Screen name="quiz" />
        <Stack.Screen name="results" />
        <Stack.Screen name="history" />
        <Stack.Screen name="bookmarks" />
        <Stack.Screen name="settings" />
        <Stack.Screen name="paywall" options={{ presentation: 'modal', animation: 'slide_from_bottom' }} />
      </Stack>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
});
