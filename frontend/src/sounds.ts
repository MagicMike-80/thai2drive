// Sound utility using expo-audio (SDK 54+)
// Generates short tones programmatically for correct/incorrect feedback
import { useAudioPlayer } from 'expo-audio';

// We use a simple approach: generate WAV data URIs and play them
// For web compatibility, we use the Audio element directly

let initialized = false;

function generateWav(samples: Int16Array, sampleRate: number): string {
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
  return 'data:audio/wav;base64,' + btoa(binary);
}

function makeTone(freqs: number[], durations: number[], volume: number): string {
  const rate = 22050;
  let totalSamples = 0;
  for (const d of durations) totalSamples += Math.floor(rate * d);
  const samples = new Int16Array(totalSamples);
  let offset = 0;
  for (let seg = 0; seg < freqs.length; seg++) {
    const n = Math.floor(rate * durations[seg]);
    const atk = Math.floor(n * 0.06);
    const rel = Math.floor(n * 0.3);
    for (let i = 0; i < n; i++) {
      let env = 1;
      if (i < atk) env = i / atk;
      else if (i > n - rel) env = (n - i) / rel;
      const s = Math.sin(2 * Math.PI * freqs[seg] * (offset + i) / rate) * volume * env;
      samples[offset + i] = Math.max(-32768, Math.min(32767, Math.floor(s * 32767)));
    }
    offset += n;
  }
  return generateWav(samples, rate);
}

const correctUri = makeTone([523, 659], [0.12, 0.12], 0.3);  // C5 → E5 (ascending, positive)
const incorrectUri = makeTone([330, 262], [0.1, 0.14], 0.25); // E4 → C4 (descending, negative)

// Simple playback using HTML Audio for web compatibility
function playUri(uri: string) {
  try {
    if (typeof Audio !== 'undefined') {
      const audio = new (globalThis as any).Audio(uri);
      audio.volume = 0.5;
      audio.play().catch(() => {});
    }
  } catch (e) {
    // Silent fail
  }
}

export function playCorrectSound() {
  playUri(correctUri);
}

export function playIncorrectSound() {
  playUri(incorrectUri);
}

export function cleanupSounds() {
  // No cleanup needed for HTML Audio
}
