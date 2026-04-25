import { Stack, useRouter, useSegments } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, StyleSheet, Platform } from 'react-native';
import { useAppStore } from '../src/store/appStore';

const AUTH_SCREENS = ['login', 'signup', 'forgot-password'];

/**
 * Premium revalidation guard.
 *
 * On every app launch we cross-check the locally cached `isPremium` flag
 * against the source of truth:
 *   1. Server-side premium (set by backend at login: `is_premium` or `is_admin`)
 *   2. RevenueCat active entitlement
 *
 * If the local flag is `true` but neither source confirms it, we revoke it.
 * This closes a class of bugs where premium got persisted through a code
 * path that should have required a confirmed payment (e.g. the previous
 * "RC unavailable → auto-unlock" bug). After this guard, premium can ONLY
 * become true via:
 *   - successful RC purchase / restore (validated entitlement), or
 *   - login with a server-side premium/admin account.
 */
function usePremiumRevalidation() {
  const isPremium = useAppStore((s) => s.isPremium);
  const user = useAppStore((s) => s.user);
  const setPremium = useAppStore((s) => s.setPremium);
  const authLoading = useAppStore((s) => s.authLoading);

  useEffect(() => {
    if (authLoading) return;
    if (!isPremium) return; // nothing to revalidate
    if (Platform.OS === 'web') return; // RC not available on web preview, leave flag alone here — paywall already gates purchases

    // Server-side premium / admin grants take precedence and never expire client-side
    if (user?.is_admin || user?.is_premium) return;

    // Otherwise verify with RevenueCat. If the entitlement is NOT active,
    // revoke the cached premium flag — it was set by some unverified path.
    (async () => {
      try {
        const apiKey = process.env.EXPO_PUBLIC_RC_API_KEY;
        // Only valid prod keys can confirm entitlement. For test/missing keys
        // we cannot prove premium, so we revoke to fail-closed.
        const isValidKey = !!apiKey && (apiKey.startsWith('goog_') || apiKey.startsWith('appl_'));
        if (!isValidKey) {
          console.log('[PremiumGuard] No valid RC key — revoking cached premium');
          await setPremium(false);
          return;
        }
        const mod = await import('react-native-purchases');
        const Purchases: any = mod.default;
        // Configure if needed (idempotent for already-configured)
        try { Purchases.configure({ apiKey }); } catch {}
        const info = await Purchases.getCustomerInfo();
        const active = !!info?.entitlements?.active?.['pro']?.isActive;
        if (!active) {
          console.log('[PremiumGuard] RC entitlement not active — revoking cached premium');
          await setPremium(false);
        }
      } catch (e) {
        // If RC SDK fails to load or check, fail closed (revoke premium).
        console.warn('[PremiumGuard] RC check failed — revoking cached premium for safety', e);
        await setPremium(false);
      }
    })();
  }, [authLoading, isPremium, user]);
}

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
  usePremiumRevalidation();

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
