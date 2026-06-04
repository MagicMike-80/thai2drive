import React from 'react';
import { useWindowDimensions } from 'react-native';
import RenderHtml from 'react-native-render-html';

interface Props {
  html: string;
  textColor: string;
  accentColor: string;
  isDark: boolean;
}

export function BookHtml({ html, textColor, accentColor, isDark }: Props) {
  const { width } = useWindowDimensions();

  // Guard: wrap plain text in <p> so RenderHtml always gets valid HTML
  const source = {
    html: html.trimStart().startsWith('<') ? html : `<p>${html}</p>`,
  };

  return (
    <RenderHtml
      contentWidth={width - 48}
      source={source}
      baseStyle={{
        color: textColor,
        fontSize: 16,
        lineHeight: 28,
        letterSpacing: 0.1,
      }}
      tagsStyles={{
        p:      { marginBottom: 12, marginTop: 0 },
        strong: { fontWeight: '700', color: textColor },
        b:      { fontWeight: '700', color: textColor },
        em:     { fontStyle: 'italic' },
        ol:     { paddingLeft: 20, marginBottom: 12 },
        ul:     { paddingLeft: 20, marginBottom: 12 },
        li:     { marginBottom: 8 },
        h2:     { fontSize: 18, fontWeight: '700', color: accentColor, marginBottom: 10, marginTop: 16 },
        h3:     { fontSize: 16, fontWeight: '700', color: accentColor, marginBottom: 8, marginTop: 12 },
      }}
      classesStyles={{
        'study-law': {
          borderLeftWidth: 3,
          borderLeftColor: accentColor,
          paddingLeft: 14,
          paddingTop: 12,
          paddingBottom: 12,
          marginTop: 14,
          marginBottom: 14,
          backgroundColor: isDark ? 'rgba(245,158,11,0.08)' : 'rgba(245,158,11,0.06)',
        },
        'study-tip': {
          borderLeftWidth: 3,
          borderLeftColor: '#10B981',
          paddingLeft: 14,
          paddingTop: 12,
          paddingBottom: 12,
          marginTop: 14,
          marginBottom: 14,
          backgroundColor: isDark ? 'rgba(16,185,129,0.08)' : 'rgba(16,185,129,0.06)',
        },
      }}
      enableExperimentalBRCollapsing
      enableExperimentalGhostLinesPrevention
    />
  );
}
