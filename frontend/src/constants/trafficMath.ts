/**
 * Traffic Math — shared constants
 * ---------------------------------
 * Single source of truth for condition metadata, speed presets, and
 * visual tokens. No logic here — pure data.
 *
 * Used by: useTrafficMath hook, traffic components, traffic-math screen.
 * NOT imported by quiz.tsx or any quiz-related component.
 */

export type Lang = 'no' | 'th' | 'en';
export type ConditionKey = 'dry' | 'wet' | 'snow' | 'ice';

// ─── Timing / performance ─────────────────────────────────────────────────────

/** Debounce before firing the API call (ms). Balances responsiveness vs requests. */
export const DEBOUNCE_MS = 350;

/** How many recent results to keep in the session-scoped cache. */
export const CACHE_MAX_ENTRIES = 60;   // 15 speeds × 4 conditions

/** Speeds to pre-warm on screen mount (common Norwegian speed limits). */
export const PREWARM_SPEEDS = [50, 80, 100];

// ─── Formula constants (mirrors backend) ─────────────────────────────────────

export const DEFAULT_REACTION_TIME_S = 1.0;
export const MAX_SPEED_KMH           = 250;
export const CAR_LENGTH_M            = 4.5;
export const BUS_LENGTH_M            = 12.0;

// ─── UI ───────────────────────────────────────────────────────────────────────

/** Quick-select preset chips on the speed input. */
export const SPEED_PRESETS: number[] = [30, 50, 80, 100, 120];

/** Max pixel width for content — centres layout on wide screens / web. */
export const CONTENT_MAX_W = 600;

/**
 * DangerBar: how many segments to display.
 * Each segment = 1 car length. Stops at 20 regardless of actual value.
 */
export const DANGER_BAR_SEGMENTS = 20;

/**
 * Step colour escalation — green → amber → orange → red.
 * Matches index to step.order - 1.
 */
export const STEP_COLORS: readonly string[] = [
  '#10B981',  // step 1: speed conversion (safe green)
  '#F59E0B',  // step 2: reaction distance (amber)
  '#F97316',  // step 3: braking distance  (orange)
  '#EF4444',  // step 4: total stop        (danger red)
];

// ─── Road condition metadata ──────────────────────────────────────────────────

export interface ConditionMeta {
  key:        ConditionKey;
  iconName:   string;          // Ionicons glyph name
  color:      string;
  multiplier: number;          // mirrors backend ROAD_CONDITIONS
  label:      Record<Lang, string>;
}

export const CONDITIONS: readonly ConditionMeta[] = [
  {
    key: 'dry', iconName: 'sunny', color: '#22C55E', multiplier: 1,
    label: { no: 'Tørr', th: 'แห้ง', en: 'Dry' },
  },
  {
    key: 'wet', iconName: 'rainy', color: '#3B82F6', multiplier: 2,
    label: { no: 'Våt', th: 'เปียก', en: 'Wet' },
  },
  {
    key: 'snow', iconName: 'snow', color: '#A855F7', multiplier: 4,
    label: { no: 'Snø', th: 'หิมะ', en: 'Snow' },
  },
  {
    key: 'ice', iconName: 'thermometer', color: '#EF4444', multiplier: 8,
    label: { no: 'Is', th: 'น้ำแข็ง', en: 'Ice' },
  },
] as const;

/** Resolve condition metadata by key. Falls back to 'dry' if key is unknown. */
export function getConditionMeta(key: string): ConditionMeta {
  return CONDITIONS.find(c => c.key === key) ?? CONDITIONS[0];
}
