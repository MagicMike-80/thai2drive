// Sound + haptic feedback utility for quiz answers.
// Uses expo-av (cross-platform: iOS, Android, web) and expo-haptics.
// Supports two styles:
//   • default — short, soft chime (~0.22s)
//   • strong  — longer, bright "kliiiing" bell (~0.6s)
// Prevents rapid stacking when the user taps fast.
import { Audio } from 'expo-av';
import * as Haptics from 'expo-haptics';
import { Platform, Vibration } from 'react-native';

export type SoundStyle = 'default' | 'strong';

// ─── WAV tone generator (data-URI, works on all platforms) ───
function generateWavDataUri(samples: Int16Array, sampleRate: number): string {
  const numSamples = samples.length;
  const dataSize = numSamples * 2;
  const buffer = new ArrayBuffer(44 + dataSize);
  const v = new DataView(buffer);
  const w = (o: number, s: string) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); };
  w(0, 'RIFF'); v.setUint32(4, 36 + dataSize, true); w(8, 'WAVE');
  w(12, 'fmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, sampleRate, true); v.setUint32(28, sampleRate * 2, true);
  v.setUint16(32, 2, true); v.setUint16(34, 16, true); w(36, 'data'); v.setUint32(40, dataSize, true);
  for (let i = 0; i < numSamples; i++) v.setInt16(44 + i * 2, samples[i], true);
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  // btoa is available on web and in Hermes (Expo SDK 49+).
  const g: any = globalThis;
  const enc = (g.btoa ?? ((b: string) => Buffer.from(b, 'binary').toString('base64')))(binary);
  return 'data:audio/wav;base64,' + enc;
}

/**
 * Build a tone composed of N segments.
 *  - freqs[i]       fundamental frequency (Hz)
 *  - durations[i]   seconds
 *  - harmonics       how many harmonics to blend in (bell-like = 3, pure sine = 1)
 *  - volume         0..1
 *  - releaseRatio   how much of each segment to use as exponential decay tail
 */
function makeTone(
  freqs: number[],
  durations: number[],
  {
    harmonics = 1,
    volume = 0.35,
    releaseRatio = 0.5,
  }: { harmonics?: number; volume?: number; releaseRatio?: number } = {},
): string {
  const rate = 22050;
  let total = 0;
  for (const d of durations) total += Math.floor(rate * d);
  const samples = new Int16Array(total);

  let offset = 0;
  for (let seg = 0; seg < freqs.length; seg++) {
    const n = Math.floor(rate * durations[seg]);
    const attackN = Math.min(Math.floor(n * 0.04), Math.floor(rate * 0.006));
    const releaseN = Math.floor(n * releaseRatio);

    for (let i = 0; i < n; i++) {
      // Envelope: quick attack, exponential release for that "bell" tail
      let env: number;
      if (i < attackN) env = i / attackN;
      else if (i > n - releaseN) {
        const t = (i - (n - releaseN)) / releaseN;
        env = Math.exp(-3.5 * t); // natural decay
      } else env = 1;

      // Sum harmonics with decreasing amplitude (1/h for a softer bell)
      let s = 0;
      for (let h = 1; h <= harmonics; h++) {
        s += Math.sin(2 * Math.PI * freqs[seg] * h * (offset + i) / rate) / h;
      }
      s = (s / harmonics) * volume * env;
      samples[offset + i] = Math.max(-32768, Math.min(32767, Math.floor(s * 32767)));
    }
    offset += n;
  }
  return generateWavDataUri(samples, rate);
}

// ─── Pre-generated sounds ───
// "default" style — rewarding but not intrusive.
// Correct: C5 → E5 → A5 ascending arpeggio with 2 harmonics + long release tail
// (that "kliiing" feel) at moderate volume. ~0.44s total.
const sndCorrectDefault   = makeTone([523.25, 659.25, 880.00], [0.08, 0.10, 0.26], { harmonics: 2, volume: 0.42, releaseRatio: 0.75 });
// Wrong: short F4 → D4 fall. Kept subtle so users don't feel punished.
const sndIncorrectDefault = makeTone([349.23, 293.66],          [0.10, 0.14],      { volume: 0.30, releaseRatio: 0.50 });

// "strong" style — bright kliiiing (bell-like with more harmonics + longer tail)
const sndCorrectStrong    = makeTone([783.99, 987.77, 1318.5], [0.10, 0.12, 0.44], { harmonics: 3, volume: 0.48, releaseRatio: 0.90 }); // G5 B5 E6
const sndIncorrectStrong  = makeTone([196.00, 164.81],          [0.12, 0.52],      { harmonics: 2, volume: 0.34, releaseRatio: 0.85 }); // G3 E3

// ─── Player cache ───
// We keep a single Sound instance per (kind, style) so we don't re-decode.
type Kind = 'correct' | 'incorrect';
const players: Partial<Record<`${Kind}-${SoundStyle}`, Audio.Sound>> = {};
let audioModeSet = false;
const lastPlayedAt: Record<Kind, number> = { correct: 0, incorrect: 0 };
const MIN_INTERVAL_MS = 120; // anti-stacking: drop plays closer than this

function uriFor(kind: Kind, style: SoundStyle): string {
  if (style === 'strong') return kind === 'correct' ? sndCorrectStrong : sndIncorrectStrong;
  return kind === 'correct' ? sndCorrectDefault : sndIncorrectDefault;
}

async function ensureAudioMode() {
  if (audioModeSet) return;
  try {
    // Play even when the iOS ringer is on silent; don't duck music too much.
    await Audio.setAudioModeAsync({
      playsInSilentModeIOS: true,
      shouldDuckAndroid: true,
      staysActiveInBackground: false,
    });
    audioModeSet = true;
  } catch {
    // non-fatal
  }
}

async function getPlayer(kind: Kind, style: SoundStyle): Promise<Audio.Sound | null> {
  const key = `${kind}-${style}` as const;
  if (players[key]) return players[key]!;
  try {
    await ensureAudioMode();
    const { sound } = await Audio.Sound.createAsync(
      { uri: uriFor(kind, style) },
      { volume: 0.9, shouldPlay: false }
    );
    players[key] = sound;
    return sound;
  } catch (e) {
    // On some web browsers, creating Sound from a data URI before user
    // interaction fails. We'll silently skip in that case.
    return null;
  }
}

async function playKind(kind: Kind, style: SoundStyle) {
  const now = Date.now();
  if (now - lastPlayedAt[kind] < MIN_INTERVAL_MS) return; // stack guard
  lastPlayedAt[kind] = now;

  const player = await getPlayer(kind, style);
  if (!player) return;
  try {
    // Rewind + play — cheaper than re-creating the Sound each time.
    await player.setPositionAsync(0);
    await player.playAsync();
  } catch {
    // Retry once by recreating the player (some devices drop the buffer after sleep)
    try {
      await player.unloadAsync();
    } catch {}
    players[`${kind}-${style}`] = undefined;
    const fresh = await getPlayer(kind, style);
    try { await fresh?.playAsync(); } catch {}
  }
}

// ─── Haptics ───
// Haptics are cheap; we don't need anti-stacking beyond what the OS already does.
async function hapticCorrect(style: SoundStyle) {
  if (Platform.OS === 'web') return;
  try {
    if (style === 'strong') {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } else {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
  } catch {}
}

async function hapticIncorrect(style: SoundStyle) {
  if (Platform.OS === 'web') return;
  try {
    if (style === 'strong') {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    } else {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
  } catch {}
}

// ─── Public API ───
export function playCorrectSound(opts: { soundEnabled: boolean; hapticsEnabled: boolean; style: SoundStyle } = { soundEnabled: true, hapticsEnabled: true, style: 'default' }) {
  if (opts.soundEnabled) { void playKind('correct', opts.style); }
  if (opts.hapticsEnabled) { void hapticCorrect(opts.style); }
}

export function playIncorrectSound(opts: { soundEnabled: boolean; hapticsEnabled: boolean; style: SoundStyle } = { soundEnabled: true, hapticsEnabled: true, style: 'default' }) {
  if (opts.soundEnabled) { void playKind('incorrect', opts.style); }
  if (opts.hapticsEnabled) { void hapticIncorrect(opts.style); }
}

export async function cleanupSounds() {
  for (const key of Object.keys(players)) {
    try { await players[key as keyof typeof players]?.unloadAsync(); } catch {}
  }
}

// Optional: call this once at app start to pre-warm players and avoid
// a ~100ms hitch on the first answer.
export async function prewarmSounds(style: SoundStyle = 'default') {
  await Promise.all([
    getPlayer('correct', style),
    getPlayer('incorrect', style),
  ]);
}
