/**
 * Traffic Math Service — Thai2Drive
 * -----------------------------------
 * TypeScript types and fetch helpers for the /api/math/* endpoints.
 *
 * All functions return null on network/server error — never throw.
 * Callers decide how to handle null (show error state, fallback UI, etc.)
 */

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';
const BASE = `${BACKEND_URL}/api/math`;

// ─── Types ────────────────────────────────────────────────────────────────────

export type Lang = 'no' | 'th' | 'en';

/** Trilingual label object returned by the backend. */
export interface MultiLang {
  no: string;
  th: string;
  en: string;
}

/** One road condition entry from /math/conditions. */
export interface RoadCondition {
  key:        string;   // 'dry' | 'wet' | 'snow' | 'ice'
  multiplier: number;   // 1.0 | 2.0 | 4.0 | 8.0
  label:      MultiLang;
  note:       MultiLang;
}

/** One calculation step from stopping_distance_full. */
export interface CalcStep {
  order:   number;
  concept: string;   // 'speed_conversion' | 'reaction_distance' | 'braking_distance' | 'stopping_distance'
  label:   MultiLang;
  formula: string;   // e.g. "50 ÷ 3.6"
  result:  number;
  unit:    string;   // 'm/s' | 'm'
  note:    MultiLang;
}

/** Danger context — translates metres into tangible comparisons. */
export interface DangerContext {
  car_lengths:  number;
  bus_lengths:  number;
  description:  MultiLang;
}

/** Full stopping distance response from /math/stopping-distance. */
export interface StoppingDistanceResult {
  input: {
    speed_kmh:       number;
    condition:       string;
    reaction_time_s: number;
  };
  results: {
    speed_ms:              number;
    reaction_distance_m:   number;
    braking_distance_m:    number;
    stopping_distance_m:   number;
  };
  condition_info: RoadCondition;
  steps:          CalcStep[];
  danger_context: DangerContext;
}

/** Comparison insight block. */
export interface ComparisonInsight {
  energy_ratio:      number;
  brake_ratio:       number;
  extra_stopping_m:  number;
  insight:           MultiLang;
}

/** Full speed comparison response from /math/compare. */
export interface SpeedComparisonResult {
  condition: string;
  speed_a:   StoppingDistanceResult;
  speed_b:   StoppingDistanceResult;
  comparison: ComparisonInsight;
}

/** Following distance response from /math/following-distance. */
export interface FollowingDistanceResult {
  input: {
    speed_kmh: number;
    seconds:   number;
  };
  results: {
    speed_ms:              number;
    following_distance_m:  number;
    car_lengths:           number;
  };
  formula:   string;
  rule_note: MultiLang;
}

/** Road conditions list from /math/conditions. */
export interface ConditionsResult {
  conditions: RoadCondition[];
  default:    string;
}

// ─── Fetch helper ─────────────────────────────────────────────────────────────

/**
 * Fetch with automatic timeout. Returns null on error, timeout, or non-2xx.
 * Traffic math calculations are pure Python — 5 s is generous; typical < 50 ms.
 */
async function safeFetch<T>(url: string, timeoutMs = 5_000): Promise<T | null> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { signal: controller.signal });
    clearTimeout(timer);
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    clearTimeout(timer);
    return null;
  }
}

// ─── Public API ───────────────────────────────────────────────────────────────

export const trafficMathApi = {
  /**
   * Full stopping distance breakdown with step-by-step formulas.
   * @param speedKmh  Speed in km/h (positive, max 250)
   * @param condition Road condition key: 'dry' | 'wet' | 'snow' | 'ice'
   * @param reaction  Reaction time in seconds (default 1.0)
   */
  getStoppingDistance(
    speedKmh:  number,
    condition: string = 'dry',
    reaction:  number = 1.0,
  ): Promise<StoppingDistanceResult | null> {
    const url = `${BASE}/stopping-distance?speed=${speedKmh}&condition=${condition}&reaction=${reaction}`;
    return safeFetch<StoppingDistanceResult>(url);
  },

  /**
   * Side-by-side speed comparison (energy ratio + extra stopping distance).
   */
  comparespeeds(
    speed1Kmh: number,
    speed2Kmh: number,
    condition: string = 'dry',
  ): Promise<SpeedComparisonResult | null> {
    const url = `${BASE}/compare?speed1=${speed1Kmh}&speed2=${speed2Kmh}&condition=${condition}`;
    return safeFetch<SpeedComparisonResult>(url);
  },

  /**
   * Following distance based on time-gap rule.
   * @param speedKmh Speed in km/h
   * @param seconds  Time gap (2 = minimum, 3 = recommended)
   */
  getFollowingDistance(
    speedKmh: number,
    seconds:  number = 2.0,
  ): Promise<FollowingDistanceResult | null> {
    const url = `${BASE}/following-distance?speed=${speedKmh}&seconds=${seconds}`;
    return safeFetch<FollowingDistanceResult>(url);
  },

  /**
   * List all road conditions with multilingual labels and multipliers.
   * Use this to populate condition pickers in the UI.
   */
  getConditions(): Promise<ConditionsResult | null> {
    return safeFetch<ConditionsResult>(`${BASE}/conditions`);
  },
} as const;
