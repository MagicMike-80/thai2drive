import React from 'react';
import { View, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { useAppStore } from '../store/appStore';
import { Flag, FlagCode } from './Flag';

// Order: Thai (hovedspråk / default) → Norsk → Engelsk
const LANGS: { code: FlagCode }[] = [
  { code: 'th' },
  { code: 'no' },
  { code: 'en' },
];

// Static require so Metro bundles the asset
const T2D_ICON = require('../../assets/images/t2d-icon.png');

type Size = 'sm' | 'md';

interface Props {
  size?: Size;
  align?: 'flex-start' | 'center' | 'flex-end';
}

export function LanguageSwitcher({ size = 'md', align = 'flex-start' }: Props) {
  const { language, setLanguage, colors: c } = useAppStore();
  const dim = size === 'sm' ? 40 : 46; // every button same size
  const flagSize = size === 'sm' ? 22 : 26;

  return (
    <View style={[styles.row, { justifyContent: align }]}>
      {LANGS.map((l) => {
        const active = language === l.code;
        const isThai = l.code === 'th';

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
                backgroundColor: active ? c.accentBg : 'transparent',
                borderColor: active ? c.accent : c.cardBorder,
                borderWidth: active ? 2.5 : 1,
              },
            ]}
          >
            {isThai ? (
              <Image
                source={T2D_ICON}
                style={{ width: dim - 6, height: dim - 6, borderRadius: (dim - 6) / 2 }}
                resizeMode="cover"
              />
            ) : (
              <Flag code={l.code} size={flagSize} />
            )}
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', gap: 10, alignItems: 'center' },
  btn: { justifyContent: 'center', alignItems: 'center', overflow: 'hidden' },
});
