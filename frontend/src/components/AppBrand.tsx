import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useAppStore } from '../store/appStore';
import { Flag } from './Flag';

/**
 * Compact brand badge: 🇹🇭 + "T2D"
 * Displayed at the top-left of every main app screen header.
 *
 * The Thai flag is rendered slightly larger than the language-switcher
 * flags (28 vs 26) so the brand stands out without crowding the header.
 *
 * `compact` shrinks the badge for space-constrained headers (e.g. Quiz).
 */
type Size = 'md' | 'compact';

export function AppBrand({ size = 'md' }: { size?: Size }) {
  const { colors: c } = useAppStore();
  const flagSize = size === 'compact' ? 22 : 28;
  const fontSize = size === 'compact' ? 14 : 17;

  return (
    <View style={styles.row} accessibilityLabel="Thai2Drive – T2D" accessible>
      <View style={[styles.flagWrap, size === 'compact' && styles.flagWrapCompact]}>
        <Flag code="th" size={flagSize} />
      </View>
      <Text
        style={[
          styles.brand,
          { color: c.text, fontSize },
        ]}
      >
        T2D
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 7,
  },
  flagWrap: {
    // Subtle shadow ring for the slightly larger flag, keeps it crisp on dark + light themes
    borderRadius: 5,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowRadius: 2,
    shadowOffset: { width: 0, height: 1 },
    elevation: 1.5,
  },
  flagWrapCompact: {
    elevation: 1,
  },
  brand: {
    fontWeight: '900',
    letterSpacing: 0.4,
  },
});
