/**
 * Build-time feature flags.
 *
 * Read once at module load (Expo bakes EXPO_PUBLIC_* into the JS bundle at
 * build time, so this is a static constant after bundling — no runtime cost).
 *
 * IS_PREVIEW_BUILD = true when:
 *   • eas.json preview profile injects EXPO_PUBLIC_PREVIEW_BUILD="true"
 *
 * Effects when IS_PREVIEW_BUILD is true:
 *   1. RevenueCat SDK is NEVER imported, configured, or called
 *   2. Paywall purchase/restore buttons are no-ops
 *   3. Premium gate is bypassed → isPremium forced to true
 *   4. usePremiumRevalidation in _layout is short-circuited
 *
 * This is a TESTING build flag. Production builds MUST leave
 * EXPO_PUBLIC_PREVIEW_BUILD unset (or false).
 */
export const IS_PREVIEW_BUILD: boolean =
  process.env.EXPO_PUBLIC_PREVIEW_BUILD === 'true';

/**
 * RC SDK is enabled only when:
 *   • not a preview build, AND
 *   • a real platform-specific RC API key is present (goog_... or appl_...)
 */
export function isRevenueCatEnabled(): boolean {
  if (IS_PREVIEW_BUILD) return false;
  const k = process.env.EXPO_PUBLIC_RC_API_KEY;
  if (!k) return false;
  return k.startsWith('goog_') || k.startsWith('appl_');
}
