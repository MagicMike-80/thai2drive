import { Stack, useRouter, useSegments } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useAppStore } from '../src/store/appStore';

const AUTH_SCREENS = ['login', 'signup', 'forgot-password'];

function useProtectedRoute() {
  const segments = useSegments();
  const router = useRouter();
  const isAuthenticated = useAppStore((s) => s.isAuthenticated);
  const authLoading = useAppStore((s) => s.authLoading);

  useEffect(() => {
    if (authLoading) return; // Wait until we know auth state

    const currentScreen = segments[0] || '';
    const onAuthScreen = AUTH_SCREENS.includes(currentScreen);

    if (!isAuthenticated && !onAuthScreen) {
      // Not logged in → go to login
      router.replace('/login');
    } else if (isAuthenticated && onAuthScreen) {
      // Already logged in → go to home
      router.replace('/');
    }
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
  }, []);

  useProtectedRoute();

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
