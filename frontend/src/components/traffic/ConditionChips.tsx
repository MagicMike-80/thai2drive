/**
 * ConditionChips — road condition selector
 * -----------------------------------------
 * Four chips: Dry · Wet · Snow · Ice.
 * Instant color swap on press — no animation (mobile readability first).
 *
 * Props are explicit so this component can be used outside the
 * traffic-math screen if needed, with no dependency on appStore.
 *
 * React.memo: only re-renders when value or lang changes.
 */
import React, { memo } from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import {
  CONDITIONS,
  type ConditionKey,
  type Lang,
} from '../../constants/trafficMath';

interface ConditionChipsProps {
  value:    ConditionKey;
  onChange: (key: ConditionKey) => void;
  lang:     Lang;
  /** Theme colors — accept any to avoid tight coupling. */
  textMuted: string;
  textSecondary: string;
}

function ConditionChipsInner({ value, onChange, lang, textMuted, textSecondary }: ConditionChipsProps) {
  return (
    <View style={st.row}>
      {CONDITIONS.map(cond => {
        const active = cond.key === value;
        const label  = cond.label[lang];
        return (
          <Pressable
            key={cond.key}
            style={({ pressed }) => [
              st.chip,
              {
                flex: 1,
                backgroundColor: active ? `${cond.color}20` : 'transparent',
                borderColor:     active ? cond.color : `${textMuted}30`,
                opacity: pressed ? 0.75 : 1,
              },
            ]}
            onPress={() => onChange(cond.key)}
            accessible
            accessibilityRole="button"
            accessibilityState={{ selected: active }}
            accessibilityLabel={label}
          >
            <Ionicons
              name={cond.iconName as any}
              size={18}
              color={active ? cond.color : textMuted}
            />
            <Text style={[st.label, { color: active ? cond.color : textSecondary }]}>
              {label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

export const ConditionChips = memo(ConditionChipsInner);

const st = StyleSheet.create({
  row:   { flexDirection: 'row', gap: 6 },
  chip:  {
    alignItems: 'center',
    gap: 4,
    paddingVertical: 10,
    paddingHorizontal: 4,
    borderRadius: 10,
    borderWidth: 1,
  },
  label: { fontSize: 11, fontWeight: '600' },
});
