/**
 * useTrafficMath — core data hook for the traffic math subsystem
 * ---------------------------------------------------------------
 * Responsibilities:
 *   - Debounce speed/condition changes before firing the API
 *   - Session-scoped in-memory cache (no persistence needed)
 *   - Return stale result while new one loads (no layout shift)
 *   - Validate data shape before accepting API response
 *   - Clean up timers + prevent setState after unmount
 *
 * NOT responsible for:
 *   - UI rendering
 *   - Quiz state
 *   - Error messaging (returns error flag; UI decides what to show)
 */
import { useEffect, useRef, useState } from 'react';

import { trafficMathApi, StoppingDistanceResult } from '../services/trafficMath';
import {
  DEBOUNCE_MS,
  DEFAULT_CONDITION,
  DEFAULT_REACTION_TIME_S,
  MAX_SPEED_KMH,
  CACHE_MAX_ENTRIES,
  PREWARM_SPEEDS,
} from '../constants/trafficMath';

// ─── Session cache ─────────────────────────────────────────────────────────────
// Lives outside the hook so it persists across mounts and is shared between
// all consumers (traffic-math screen + MathContextCard).
// Max entries: 15 speeds × 4 conditions = 60 — tiny footprint.

const _cache = new Map<string, StoppingDistanceResult>();

function cacheKey(speed: number, condition: string): string {
  return `${speed}_${condition}`;
}

function cacheSet(key: string, value: StoppingDistanceResult): void {
  if (_cache.size >= CACHE_MAX_ENTRIES) {
    // Evict the oldest entry
    const firstKey = _cache.keys().next().value;
    if (firstKey !== undefined) _cache.delete(firstKey);
  }
  _cache.set(key, value);
}

/** Validate that the API response has the expected shape. */
function isValidResult(data: unknown): data is StoppingDistanceResult {
  if (!data || typeof data !== 'object') return false;
  const d = data as any;
  return (
    Array.isArray(d.steps) &&
    d.steps.length === 4 &&
    typeof d.results?.stopping_distance_m === 'number'
  );
}

// ─── Hook types ───────────────────────────────────────────────────────────────

export interface TrafficMathState {
  result:  StoppingDistanceResult | null;
  loading: boolean;
  error:   boolean;
  /** True while a new result is loading but the previous one is still displayed. */
  isStale: boolean;
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useTrafficMath(
  speedKmh:       number | null,
  condition:      string = DEFAULT_CONDITION,
  reactionTimeS:  number = DEFAULT_REACTION_TIME_S,
): TrafficMathState {
  const [state, setState] = useState<TrafficMathState>({
    result: null, loading: false, error: false, isStale: false,
  });

  // Stable refs — no re-render side effects
  const timerRef   = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  useEffect(() => {
    // Cancel any in-flight debounce from previous render
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }

    const speed = speedKmh ?? 0;

    // Invalid input — clear result immediately, no API call
    if (!speed || speed <= 0 || speed > MAX_SPEED_KMH) {
      setState({ result: null, loading: false, error: false, isStale: false });
      return;
    }

    const key = cacheKey(Math.round(speed), condition);

    // Cache hit — instant, zero loading state
    const cached = _cache.get(key);
    if (cached) {
      if (__DEV__) console.log(`[TrafficMath] cache HIT  ${key}`);
      setState({ result: cached, loading: false, error: false, isStale: false });
      return;
    }

    // Cache miss — keep stale result visible while loading
    if (__DEV__) console.log(`[TrafficMath] cache MISS ${key} — fetching`);
    setState(prev => ({
      ...prev,
      loading: true,
      error:   false,
      isStale: prev.result !== null,
    }));

    timerRef.current = setTimeout(async () => {
      try {
        const data = await trafficMathApi.getStoppingDistance(speed, condition, reactionTimeS);

        if (!mountedRef.current) return;

        if (isValidResult(data)) {
          cacheSet(key, data);
          setState({ result: data, loading: false, error: false, isStale: false });
        } else {
          // API returned something unexpected — silent error, keep stale result
          setState(prev => ({ ...prev, loading: false, error: true, isStale: false }));
        }
      } catch {
        if (!mountedRef.current) return;
        setState(prev => ({ ...prev, loading: false, error: true, isStale: false }));
      }
    }, DEBOUNCE_MS);

    // Cleanup: cancel the timer if deps change before it fires
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [speedKmh, condition, reactionTimeS]);

  return state;
}

// ─── Pre-warm utility ─────────────────────────────────────────────────────────

/**
 * Fire-and-forget: fetch common speeds in the background on screen mount.
 * Results go directly into the shared cache so subsequent user interactions
 * hit the cache instantly.
 *
 * Safe to call multiple times — skips already-cached entries.
 */
export function prewarmTrafficMath(
  condition: string = DEFAULT_CONDITION,
  speeds:    number[] = PREWARM_SPEEDS,
): void {
  for (const speed of speeds) {
    const key = cacheKey(speed, condition);
    if (_cache.has(key)) continue;

    trafficMathApi.getStoppingDistance(speed, condition).then(data => {
      if (isValidResult(data)) cacheSet(key, data);
    }).catch(() => { /* silent — pre-warm is best-effort */ });
  }
}
