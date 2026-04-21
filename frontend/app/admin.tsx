import { useEffect } from 'react';
import { View, Text, ActivityIndicator, Linking, Platform } from 'react-native';
import { useRouter } from 'expo-router';

/**
 * Admin redirect page.
 *
 * The actual admin panel is served by the backend at /api/admin-panel.
 * This Expo Router page just redirects there, so the user can reach it
 * via /admin (short URL).
 */
export default function AdminRedirect() {
  const router = useRouter();

  useEffect(() => {
    const target = '/api/admin-panel';
    if (Platform.OS === 'web') {
      // On web, do a full page redirect to the backend-served HTML.
      if (typeof window !== 'undefined') {
        window.location.replace(target);
      }
    } else {
      // On native, open in the device browser.
      const base = (process.env.EXPO_PUBLIC_BACKEND_URL || '').replace(/\/$/, '');
      const fullUrl = base + target;
      Linking.openURL(fullUrl);
      // Also pop back to home so user doesn't get stuck.
      router.replace('/');
    }
  }, [router]);

  return (
    <View
      style={{
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#0f172a',
      }}
    >
      <ActivityIndicator size="large" color="#3b82f6" />
      <Text style={{ color: '#e2e8f0', marginTop: 16, fontSize: 16 }}>
        Åpner admin-panel…
      </Text>
      <Text style={{ color: '#94a3b8', marginTop: 8, fontSize: 13 }}>
        /api/admin-panel
      </Text>
    </View>
  );
}
