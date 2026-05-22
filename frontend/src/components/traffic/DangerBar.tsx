/**
 * DangerBar — animated segment bar showing car-length danger context
 * ------------------------------------------------------------------
 * Design decisions:
 *
 *   WHY SEGMENTS, NOT A CONTINUOUS BAR:
 *   A continuous bar requires animating `width`, which cannot use
 *   useNativeDriver on React Native. Width animation runs on the JS
 *   thread and causes frame drops on weak Android devices.
 *
 *   Segments (one pill per car length) use only `opacity` for the
 *   entrance animation — fully native driver. Each segment is also
 *   immediately readable: the user can count the filled pills.
 *
 *   PERFORMANCE:
 *   React.memo + stable key = no re-renders on scroll.
 *   The entrance animation runs exactly once per result change.
 *
 * Used by: traffic-math.tsx
 * NOT used by: MathContextCard (quiz context uses SpeedSummary instead)
 */
import React, { memo, useEffect, useRef } from 'react';
import { View, Animated, StyleSheet } from 'react-native';

import { DANGER_BAR_SEGMENTS } from '../../constants/trafficMath';

interface DangerBarProps {
  carLengths: number;
  color:      string;
  /** Muted background for unfilled segments (from theme). */
  trackColor?: string;
}

function DangerBarInner({ carLengths, color, trackColor = 'rgba(128,128,128,0.18)' }: DangerBarProps) {
  const opacity = useRef(new Animated.Value(0)).current;
  const filled  = Math.min(Math.round(carLengths), DANGER_BAR_SEGMENTS);

  // Fade the entire bar in whenever the result changes.
  // useNativeDriver: true — runs on the UI thread, zero JS overhead.
  useEffect(() => {
    opacity.setValue(0);
    Animated.timing(opacity, {
      toValue:         1,
      duration:        400,
      useNativeDriver: true,
    }).start();
  }, [carLengths]);

  return (
    <Animated.View style={[st.row, { opacity }]}>
      {Array.from({ length: DANGER_BAR_SEGMENTS }, (_, i) => (
        <View
          key={i}
          style={[
            st.segment,
            { backgroundColor: i < filled ? color : trackColor },
          ]}
        />
      ))}
    </Animated.View>
  );
}

export const DangerBar = memo(DangerBarInner);

const st = StyleSheet.create({
  row:     { flexDirection: 'row', gap: 3 },
  segment: { flex: 1, height: 8, borderRadius: 4 },
});
