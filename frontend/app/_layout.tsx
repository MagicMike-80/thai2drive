import { Stack, useRouter, useSegments } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, StyleSheet, Platform } from 'react-native';
import { useAppStore } from '../src/store/appStore';
import { IS_PREVIEW_BUILD } from '../src/buildFlags';

/**
 * WebAppShell — desktop web only.
 *
 * Wraps the entire app in a centered 430 px phone frame so every screen
 * inherits the mobile layout on wide viewports. On native (iOS / Android)
 * this component is a transparent passthrough — zero runtime cost.
 *
 * Visual layers (outermost → innermost):
 *   1. Ambient background  — very dark slate with a soft radial glow in the
 *      centre so the frame sits in "depth" rather than floating on nothing.
 *   2. Phone frame         — max-width 430 px, full height, clipped overflow.
 *      A 1 px rgba border gives the glass-edge highlight phones have.
 *      A layered box-shadow provides near + far depth.
 *
 * Breakpoints handled automatically:
 *   ≤ 430 px viewport  → frame fills 100 % width, no side gap (phone browser)
 *   430 px – any width → frame is centred with dark ambient on both sides
 */
function WebAppShell({ children }: { children: React.ReactNode }) {
  if (Platform.OS !== 'web') return <>{children}</>;
  return (
    <View style={_webOuter as any}>
      <View style={_webFrame as any}>
        {children}
      </View>
    </View>
  );
}

// Plain JS objects — CSS properties not present in React Native's ViewStyle.
// Rendered ONLY on web (Platform.OS check above), so no native impact.
const _webOuter = {
  flex: 1,
  backgroundColor: '#010B18',
  // Backlit glow centred behind the frame — gives the dark background depth
  // so the frame reads as floating, not pasted onto a flat surface.
  // Colour: deep indigo/navy at the core, fading to near-black at the edges.
  backgroundImage: [
    'radial-gradient(ellipse 110% 70% at 50% 42%,',
    '  rgba(22,40,95,0.55) 0%,',
    '  rgba(12,22,58,0.30) 40%,',
    '  #010B18 72%)',
  ].join(' '),
  alignItems: 'center',
  justifyContent: 'flex-start',
  // Vertical breathing room reveals the top + bottom rounded corners of the
  // frame, completing the "phone in space" silhouette on desktop viewports.
  paddingTop: 32,
  paddingBottom: 48,
};

const _webFrame = {
  flex: 1,
  width: '100%',
  // 390 px = iPhone 14/15 logical width. Narrower than the previous 430 px,
  // which left too much app visible and not enough surrounding dark space.
  maxWidth: 390,
  // Rounded corners mimic a physical phone body.
  borderTopLeftRadius: 40,
  borderTopRightRadius: 40,
  borderBottomLeftRadius: 44,
  borderBottomRightRadius: 44,
  overflow: 'hidden',
  position: 'relative',
  // Five shadow layers (innermost → outermost):
  //   1. Hairline glass-edge highlight  — physical screen boundary
  //   2. Contact shadow                 — 2-4 px, razor-crisp
  //   3. Near shadow                    — 8-24 px, readable depth
  //   4. Mid shadow                     — 40-80 px, spatial presence
  //   5. Ambient scatter                — 100-200 px, environmental depth
  boxShadow: [
    '0 0 0 1px rgba(255,255,255,0.09)',
    '0 2px 6px rgba(0,0,0,0.50)',
    '0 10px 28px rgba(0,0,0,0.65)',
    '0 40px 90px rgba(0,0,0,0.80)',
    '0 90px 200px rgba(0,0,0,0.55)',
  ].join(', '),
};

const AUTH_SCREENS = ['login', 'signup', 'forgot-password'];

/**
 * Preview build: force premium=true once on launch so testers can use the
 * full app without paywall gating, AND skip every RC SDK call. This is the
 * only place isPremium is allowed to flip to true outside of a verified RC
 * purchase (and only because the build flag is explicitly set in eas.json
 * preview profile — never in production).
 */
function usePreviewPremiumOverride() {
  const isPremium = useAppStore((s) => s.isPremium);
  const setPremium = useAppStore((s) => s.setPremium);
  const authLoading = useAppStore((s) => s.authLoading);

  useEffect(() => {
    if (!IS_PREVIEW_BUILD) return;
    if (authLoading) return;
    if (isPremium) return;
    console.log('[PreviewBuild] Forcing isPremium=true (RC disabled)');
    setPremium(true);
  }, [authLoading, isPremium]);
}

/**
 * Premium revalidation guard (PRODUCTION builds only).
 *
 * On every app launch we cross-check the locally cached `isPremium` flag
 * against the source of truth:
 *   1. Server-side premium (set by backend at login: `is_premium` or `is_admin`)
 *   2. RevenueCat active entitlement
 *
 * If the local flag is `true` but neither source confirms it, we revoke it.
 * This closes a class of bugs where premium got persisted through a code
 * path that should have required a confirmed payment.
 *
 * NOTE: when IS_PREVIEW_BUILD is true, this hook returns immediately —
 * the SDK is never imported, never configured. Use `usePreviewPremiumOverride`
 * for preview/test builds.
 */
function usePremiumRevalidation() {
  const isPremium = useAppStore((s) => s.isPremium);
  const user = useAppStore((s) => s.user);
  const setPremium = useAppStore((s) => s.setPremium);
  const authLoading = useAppStore((s) => s.authLoading);

  useEffect(() => {
    if (IS_PREVIEW_BUILD) return; // hard kill-switch
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
  usePreviewPremiumOverride();

  if (!isReady) {
    return (
      <SafeAreaProvider>
        <WebAppShell>
          <View style={[styles.loading, { backgroundColor: colors.bg }]}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        </WebAppShell>
      </SafeAreaProvider>
    );
  }

  return (
    <SafeAreaProvider>
      <StatusBar style={isDark ? 'light' : 'dark'} />
      <WebAppShell>
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
          <Stack.Screen name="book" />
          <Stack.Screen name="stats" />
          <Stack.Screen name="signs" />
          <Stack.Screen name="traffic-math" />
          <Stack.Screen name="teacher" />
          <Stack.Screen name="research" />
          <Stack.Screen name="library" />
          <Stack.Screen name="glossary" />
          <Stack.Screen name="social" />
        </Stack>
      </WebAppShell>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
});
