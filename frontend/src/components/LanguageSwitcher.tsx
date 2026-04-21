import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { useAppStore } from '../store/appStore';
import { Flag, FlagCode } from './Flag';

const LANGS: { code: FlagCode }[] = [
  { code: 'th' },
  { code: 'no' },
  { code: 'en' },
];

type Size = 'sm' | 'md';

interface Props {
  size?: Size;
  align?: 'flex-start' | 'center' | 'flex-end';
}

export function LanguageSwitcher({ size = 'md', align = 'flex-start' }: Props) {
  const { language, setLanguage, colors: c } = useAppStore();
  const dim = size === 'sm' ? 32 : 38;
  const flagSize = size === 'sm' ? 16 : 20;

  return (
    <View style={[styles.row, { justifyContent: align }]}>
      {LANGS.map((l) => {
        const active = language === l.code;
        return (
          <TouchableOpacity
            key={l.code}
            testID={`lang-btn-${l.code}`}
            onPress={() => setLanguage(l.code)}
            activeOpacity={0.7}
            style={[
              styles.btn,
              {
                width: dim,
                height: dim,
                borderRadius: dim / 2,
                backgroundColor: active ? c.accentBg : c.card,
                borderColor: active ? c.accent : 'transparent',
              },
            ]}
          >
            <Flag code={l.code} size={flagSize} />
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', gap: 8, alignItems: 'center' },
  btn: { justifyContent: 'center', alignItems: 'center', borderWidth: 2 },
});
