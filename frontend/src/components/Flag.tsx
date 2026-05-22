import React from 'react';
import { View, StyleSheet } from 'react-native';

export type FlagCode = 'no' | 'th' | 'en';

/**
 * Lightweight View-based flag component.
 * Emoji flags (🇳🇴 🇬🇧 🇹🇭) do not render on Android / React-Native-Web —
 * they fall back to letter codes ("NO", "GB", "TH"). This component
 * renders simple, always-visible vector flags using plain Views.
 */
export function Flag({ code, size = 22, rounded = true }: { code: FlagCode; size?: number; rounded?: boolean }) {
  const height = size;
  const width = Math.round(size * 1.5);
  const radius = rounded ? Math.max(2, Math.round(size * 0.15)) : 0;

  const baseStyle = {
    width,
    height,
    borderRadius: radius,
    overflow: 'hidden' as const,
  };

  if (code === 'th') {
    const u = height / 6; // stripes 1-1-2-1-1
    return (
      <View style={baseStyle}>
        <View style={{ height: u, backgroundColor: '#C1192C' }} />
        <View style={{ height: u, backgroundColor: '#F8F9FA' }} />
        <View style={{ height: u * 2, backgroundColor: '#1B1C6E' }} />
        <View style={{ height: u, backgroundColor: '#F8F9FA' }} />
        <View style={{ height: u, backgroundColor: '#C1192C' }} />
      </View>
    );
  }

  if (code === 'no') {
    // Nordic cross: red bg, white cross, blue cross on top
    const whiteW = Math.max(3, Math.round(size * 0.28));
    const blueW = Math.max(1, Math.round(size * 0.14));
    const vLeft = Math.round(width * 0.31); // cross vertical center
    const hTop = Math.round(height * 0.5);  // cross horizontal center
    return (
      <View style={[baseStyle, { backgroundColor: '#BA0C2F' }]}>
        {/* white horizontal */}
        <View style={{ position: 'absolute', left: 0, right: 0, top: hTop - whiteW / 2, height: whiteW, backgroundColor: '#FFFFFF' }} />
        {/* white vertical */}
        <View style={{ position: 'absolute', top: 0, bottom: 0, left: vLeft - whiteW / 2, width: whiteW, backgroundColor: '#FFFFFF' }} />
        {/* blue horizontal */}
        <View style={{ position: 'absolute', left: 0, right: 0, top: hTop - blueW / 2, height: blueW, backgroundColor: '#00205B' }} />
        {/* blue vertical */}
        <View style={{ position: 'absolute', top: 0, bottom: 0, left: vLeft - blueW / 2, width: blueW, backgroundColor: '#00205B' }} />
      </View>
    );
  }

  // en / GB — Union Jack simplified (blue bg, white saltire, red saltire, white + red cross)
  const diagThickW = Math.max(2, Math.round(size * 0.18)); // white diagonal thickness
  const diagThickR = Math.max(1, Math.round(size * 0.08)); // red diagonal thickness
  const crossW = Math.max(3, Math.round(size * 0.26));     // white straight cross thickness
  const crossR = Math.max(1, Math.round(size * 0.14));     // red straight cross thickness
  const diagLen = Math.round(width * 1.3);

  return (
    <View style={[baseStyle, { backgroundColor: '#012169', justifyContent: 'center', alignItems: 'center' }]}>
      {/* white diagonals (saltire) */}
      <View style={{ position: 'absolute', width: diagLen, height: diagThickW, backgroundColor: '#FFFFFF', transform: [{ rotate: '30deg' }] }} />
      <View style={{ position: 'absolute', width: diagLen, height: diagThickW, backgroundColor: '#FFFFFF', transform: [{ rotate: '-30deg' }] }} />
      {/* red diagonals (St Patrick) */}
      <View style={{ position: 'absolute', width: diagLen, height: diagThickR, backgroundColor: '#C8102E', transform: [{ rotate: '30deg' }] }} />
      <View style={{ position: 'absolute', width: diagLen, height: diagThickR, backgroundColor: '#C8102E', transform: [{ rotate: '-30deg' }] }} />
      {/* white cross */}
      <View style={{ position: 'absolute', width: '100%', height: crossW, backgroundColor: '#FFFFFF' }} />
      <View style={{ position: 'absolute', height: '100%', width: crossW, backgroundColor: '#FFFFFF' }} />
      {/* red cross */}
      <View style={{ position: 'absolute', width: '100%', height: crossR, backgroundColor: '#C8102E' }} />
      <View style={{ position: 'absolute', height: '100%', width: crossR, backgroundColor: '#C8102E' }} />
    </View>
  );
}

// Convenience styles for consumers
export const flagStyles = StyleSheet.create({
  shadow: {
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 2,
    shadowOffset: { width: 0, height: 1 },
    elevation: 1,
  },
});
