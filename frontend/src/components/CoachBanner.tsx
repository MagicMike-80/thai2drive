/**
 * CoachBanner — personalized AI coaching message for the home screen.
 *
 * Shows a rotating coaching message + SRS badge.
 * Tapping the banner navigates to the AI Dashboard.
 * Dismissed by pressing ×, re-shows next session.
 *
 * Session cache: coaching data is cached for 5 minutes per deviceId+lang.
 * Navigating home → quiz → home reuses the cached message instead of
 * firing a new API call on every mount.
 */
import React, { useEffect, useState, useRef } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, Animated,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { aiLearningApi } from '../services/aiLearning';
import type { ThemeColors } from '../theme';

// ─── Session-scoped coaching cache ───────────────────────────────────────────
// Lives outside the component — persists across mounts within the same app session.
// Key: `${deviceId}:${lang}` — intentionally excludes `streak` to avoid
// invalidating the cache on every small change.

interface _CacheEntry { messages: string[]; srs_due_count: number; fetchedAt: number }
const _coachCache  = new Map<string, _CacheEntry>();
const _CACHE_TTL   = 5 * 60 * 1000; // 5 minutes

const _CACHE_MAX   = 20;   // max entries — prevents unbounded growth across device IDs

function _getCached(key: string): _CacheEntry | null {
  const entry = _coachCache.get(key);
  if (!entry) return null;
  if (Date.now() - entry.fetchedAt > _CACHE_TTL) { _coachCache.delete(key); return null; }
  return entry;
}

function _setCached(key: string, value: Omit<_CacheEntry, 'fetchedAt'>): void {
  if (_coachCache.size >= _CACHE_MAX) {
    // Evict oldest entry (Map preserves insertion order)
    const firstKey = _coachCache.keys().next().value;
    if (firstKey !== undefined) _coachCache.delete(firstKey);
  }
  _coachCache.set(key, { ...value, fetchedAt: Date.now() });
}
// ─────────────────────────────────────────────────────────────────────────────

interface CoachBannerProps {
  deviceId: string;
  lang:     string;
  streak:   number;
  colors:   ThemeColors;
}

const TR: Record<string, { title: string; srs: string; go: string }> = {
  no: { title: 'AI Lærer',  srs: 'til repetisjon', go: 'Se analyse →' },
  th: { title: 'AI ครู',    srs: 'รอทบทวน',       go: 'ดูการวิเคราะห์ →' },
  en: { title: 'AI Coach',  srs: 'due for review', go: 'View insights →' },
};

export function CoachBanner({ deviceId, lang, streak, colors: c }: CoachBannerProps) {
  const router = useRouter();
  const t = TR[lang] || TR.en;

  // Dev-only render counter. More than ~5 renders on a stable home screen
  // indicates a rerender loop. Stripped in production builds (__DEV__ === false).
  const _renderCount = useRef(0);
  if (__DEV__) {
    _renderCount.current += 1;
    if (_renderCount.current > 6) {
      console.warn(`[CoachBanner] render #${_renderCount.current} — possible loop`);
    }
  }

  const [message, setMessage]   = useState<string | null>(null);
  const [srsCount, setSrsCount] = useState(0);
  const [dismissed, setDismissed] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    let mounted = true;
    const key = `${deviceId}:${lang}`;

    // Cache hit — instant, no API call
    const cached = _getCached(key);
    if (cached && cached.messages.length > 0) {
      setMessage(cached.messages[0]);
      setSrsCount(cached.srs_due_count);
      Animated.timing(fadeAnim, { toValue: 1, duration: 350, useNativeDriver: true }).start();
      return;
    }

    // Cache miss — fetch and store
    (async () => {
      const data = await aiLearningApi.getCoaching(deviceId, lang, streak);
      if (!mounted) return;
      if (data && data.messages.length > 0) {
        _coachCache.set(key, {
          messages:      data.messages,
          srs_due_count: data.srs_due_count,
          fetchedAt:     Date.now(),
        });
        setMessage(data.messages[0]);
        setSrsCount(data.srs_due_count);
        Animated.timing(fadeAnim, { toValue: 1, duration: 350, useNativeDriver: true }).start();
      }
    })();
    return () => { mounted = false; };
  }, [deviceId, lang]); // streak intentionally omitted — not worth invalidating cache on every change

  if (dismissed || !message) return null;

  return (
    <Animated.View style={{ opacity: fadeAnim }}>
      <TouchableOpacity
        style={[styles.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}
        onPress={() => router.push('/ai-dashboard')}
        activeOpacity={0.85}
      >
        {/* Left accent stripe */}
        <View style={[styles.stripe, { backgroundColor: c.accent }]} />

        {/* Body */}
        <View style={styles.body}>
          <View style={styles.titleRow}>
            <Ionicons name="sparkles" size={14} color={c.accent} />
            <Text style={[styles.title, { color: c.accent }]}>{t.title}</Text>
            {srsCount > 0 && (
              <View style={[styles.srsBadge, { backgroundColor: `${c.accent}20` }]}>
                <Text style={[styles.srsTxt, { color: c.accent }]}>
                  {srsCount} {t.srs}
                </Text>
              </View>
            )}
          </View>
          <Text style={[styles.msg, { color: c.textSecondary }]} numberOfLines={2}>
            {message}
          </Text>
          <Text style={[styles.goLink, { color: `${c.accent}CC` }]}>{t.go}</Text>
        </View>

        {/* Dismiss */}
        <TouchableOpacity
          style={styles.dismiss}
          onPress={() => setDismissed(true)}
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        >
          <Ionicons name="close" size={16} color={c.textMuted} />
        </TouchableOpacity>
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection:  'row',
    alignItems:     'stretch',
    borderRadius:   14,
    borderWidth:    1,
    overflow:       'hidden',
    marginBottom:   0,
  },
  stripe: {
    width:          4,
    flexShrink:     0,
  },
  body: {
    flex:           1,
    paddingVertical: 12,
    paddingLeft:    12,
    paddingRight:   4,
    gap:            4,
  },
  titleRow: {
    flexDirection:  'row',
    alignItems:     'center',
    gap:            5,
    flexWrap:       'wrap',
  },
  title: {
    fontSize:       12,
    fontWeight:     '800',
    letterSpacing:  0.5,
    textTransform:  'uppercase',
  },
  srsBadge: {
    borderRadius:   8,
    paddingHorizontal: 7,
    paddingVertical: 2,
  },
  srsTxt: {
    fontSize:   11,
    fontWeight: '700',
  },
  msg: {
    fontSize:   13,
    lineHeight: 19,
  },
  goLink: {
    fontSize:   12,
    fontWeight: '700',
    marginTop:  2,
  },
  dismiss: {
    paddingHorizontal: 10,
    justifyContent:    'center',
  },
});
