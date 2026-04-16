import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';

type Plan = 'weekly' | 'fourweek';

const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Best\u00e5 teoripr\u00f8ven raskere',
    subtitle: 'L\u00e6r norsk teori p\u00e5 Thai, Norsk og Engelsk',
    weekly: 'Ukentlig',
    weeklyPrice: '99 kr / uke',
    fourweek: '4 uker',
    fourweekSub: 'Best verdi',
    fourweekPrice: '199 kr',
    popular: 'Popul\u00e6r',
    earlyAccess: 'Early Access \u2013 Kun for de f\u00f8rste 50 brukerne',
    feat1: 'Ubegrenset sp\u00f8rsm\u00e5l',
    feat2: 'Norsk + Thai + Engelsk',
    feat3: 'Forklaringer p\u00e5 alle sp\u00f8rsm\u00e5l',
    cta: 'Start n\u00e5',
    cancel: 'Avslutt n\u00e5r som helst',
    close: 'Lukk',
  },
  th: {
    title: '\u0e2a\u0e2d\u0e1a\u0e1c\u0e48\u0e32\u0e19\u0e17\u0e24\u0e29\u0e0e\u0e35\u0e40\u0e23\u0e47\u0e27\u0e02\u0e36\u0e49\u0e19',
    subtitle: '\u0e40\u0e23\u0e35\u0e22\u0e19\u0e17\u0e24\u0e29\u0e0e\u0e35\u0e19\u0e2d\u0e23\u0e4c\u0e40\u0e27\u0e22\u0e4c\u0e40\u0e1b\u0e47\u0e19\u0e20\u0e32\u0e29\u0e32\u0e44\u0e17\u0e22 \u0e19\u0e2d\u0e23\u0e4c\u0e40\u0e27\u0e22\u0e4c \u0e41\u0e25\u0e30\u0e2d\u0e31\u0e07\u0e01\u0e24\u0e29',
    weekly: '\u0e23\u0e32\u0e22\u0e2a\u0e31\u0e1b\u0e14\u0e32\u0e2b\u0e4c',
    weeklyPrice: '99 kr / \u0e2a\u0e31\u0e1b\u0e14\u0e32\u0e2b\u0e4c',
    fourweek: '4 \u0e2a\u0e31\u0e1b\u0e14\u0e32\u0e2b\u0e4c',
    fourweekSub: '\u0e04\u0e38\u0e49\u0e21\u0e04\u0e48\u0e32\u0e17\u0e35\u0e48\u0e2a\u0e38\u0e14',
    fourweekPrice: '199 kr',
    popular: '\u0e22\u0e2d\u0e14\u0e19\u0e34\u0e22\u0e21',
    earlyAccess: 'Early Access \u2013 \u0e2a\u0e33\u0e2b\u0e23\u0e31\u0e1a 50 \u0e04\u0e19\u0e41\u0e23\u0e01',
    feat1: '\u0e04\u0e33\u0e16\u0e32\u0e21\u0e44\u0e21\u0e48\u0e08\u0e33\u0e01\u0e31\u0e14',
    feat2: '\u0e19\u0e2d\u0e23\u0e4c\u0e40\u0e27\u0e22\u0e4c + \u0e44\u0e17\u0e22 + \u0e2d\u0e31\u0e07\u0e01\u0e24\u0e29',
    feat3: '\u0e04\u0e33\u0e2d\u0e18\u0e34\u0e1a\u0e32\u0e22\u0e17\u0e38\u0e01\u0e02\u0e49\u0e2d',
    cta: '\u0e40\u0e23\u0e34\u0e48\u0e21\u0e40\u0e25\u0e22',
    cancel: '\u0e22\u0e01\u0e40\u0e25\u0e34\u0e01\u0e44\u0e14\u0e49\u0e17\u0e38\u0e01\u0e40\u0e21\u0e37\u0e48\u0e2d',
    close: '\u0e1b\u0e34\u0e14',
  },
  en: {
    title: 'Pass the theory test faster',
    subtitle: 'Learn Norwegian theory in Thai, Norwegian and English',
    weekly: 'Weekly',
    weeklyPrice: '99 kr / week',
    fourweek: '4 weeks',
    fourweekSub: 'Best value',
    fourweekPrice: '199 kr',
    popular: 'Popular',
    earlyAccess: 'Early Access \u2013 Only for the first 50 users',
    feat1: 'Unlimited questions',
    feat2: 'Norwegian + Thai + English',
    feat3: 'Explanations on all questions',
    cta: 'Start now',
    cancel: 'Cancel anytime',
    close: 'Close',
  },
};

export default function PaywallScreen() {
  const router = useRouter();
  const { language, colors, setPremium } = useAppStore();
  const t = TR[language] || TR.no;
  const c = colors;
  const [selectedPlan, setSelectedPlan] = useState<Plan>('fourweek');

  const handleUnlock = async () => {
    // MOCKED — in production, integrate with App Store / Google Play
    await setPremium(true);
    router.back();
  };

  const isWeekly = selectedPlan === 'weekly';
  const isFour = selectedPlan === 'fourweek';

  return (
    <SafeAreaView style={[s.container, { backgroundColor: c.bg }]}>
      <ScrollView contentContainerStyle={s.scroll} showsVerticalScrollIndicator={false}>
        {/* Close button */}
        <TouchableOpacity
          testID="paywall-close-btn"
          style={[s.closeBtn, { backgroundColor: c.card }]}
          onPress={() => router.back()}
          activeOpacity={0.7}
        >
          <Ionicons name="close" size={20} color={c.textSecondary} />
        </TouchableOpacity>

        {/* Header */}
        <View style={s.header}>
          <Text style={s.flag}>{"🇹🇭"}</Text>
          <Text style={[s.title, { color: c.text }]}>{t.title}</Text>
          <Text style={[s.subtitle, { color: c.textSecondary }]}>{t.subtitle}</Text>
        </View>

        {/* Pricing cards */}
        <View style={s.plans}>
          {/* Weekly */}
          <TouchableOpacity
            testID="plan-weekly"
            style={[
              s.planCard,
              {
                backgroundColor: isWeekly ? c.accentBg : c.card,
                borderColor: isWeekly ? c.accent : c.cardBorder,
              },
            ]}
            onPress={() => setSelectedPlan('weekly')}
            activeOpacity={0.8}
          >
            <View style={s.planRadioRow}>
              <View style={[s.radio, { borderColor: isWeekly ? c.accent : c.textMuted }]}>
                {isWeekly && <View style={[s.radioFill, { backgroundColor: c.accent }]} />}
              </View>
              <View style={s.planInfo}>
                <Text style={[s.planName, { color: c.text }]}>{t.weekly}</Text>
                <Text style={[s.planPrice, { color: isWeekly ? c.accent : c.textSecondary }]}>{t.weeklyPrice}</Text>
              </View>
            </View>
          </TouchableOpacity>

          {/* 4 Weeks — highlighted */}
          <TouchableOpacity
            testID="plan-fourweek"
            style={[
              s.planCard,
              s.planHighlight,
              {
                backgroundColor: isFour ? c.accentBg : c.card,
                borderColor: isFour ? c.accent : c.cardBorder,
              },
            ]}
            onPress={() => setSelectedPlan('fourweek')}
            activeOpacity={0.8}
          >
            {/* Popular badge */}
            <View style={[s.badge, { backgroundColor: c.accent }]}>
              <Text style={s.badgeText}>{t.popular}</Text>
            </View>
            <View style={s.planRadioRow}>
              <View style={[s.radio, { borderColor: isFour ? c.accent : c.textMuted }]}>
                {isFour && <View style={[s.radioFill, { backgroundColor: c.accent }]} />}
              </View>
              <View style={s.planInfo}>
                <Text style={[s.planName, { color: c.text }]}>
                  {t.fourweek}
                  <Text style={[s.planSub, { color: c.textSecondary }]}>  ({t.fourweekSub})</Text>
                </Text>
                <Text style={[s.planPrice, s.planPriceHighlight, { color: isFour ? c.accent : c.textSecondary }]}>{t.fourweekPrice}</Text>
              </View>
            </View>
          </TouchableOpacity>
        </View>

        {/* Early access */}
        <View style={s.earlyRow}>
          <Text style={[s.earlyText, { color: c.accent }]}>
            {"🔥"} {t.earlyAccess}
          </Text>
        </View>

        {/* Features */}
        <View style={s.features}>
          {[t.feat1, t.feat2, t.feat3].map((feat, i) => (
            <View key={i} style={s.featRow}>
              <Ionicons name="checkmark-circle" size={20} color={c.correct} />
              <Text style={[s.featText, { color: c.text }]}>{feat}</Text>
            </View>
          ))}
        </View>
      </ScrollView>

      {/* Bottom CTA */}
      <View style={[s.bottomWrap, { borderTopColor: c.divider }]}>
        <TouchableOpacity
          testID="paywall-cta-btn"
          style={[s.ctaBtn, { backgroundColor: c.accent }]}
          onPress={handleUnlock}
          activeOpacity={0.85}
        >
          <Ionicons name="flash" size={20} color="#0F172A" />
          <Text style={s.ctaText}>{t.cta}</Text>
        </TouchableOpacity>
        <Text style={[s.cancelText, { color: c.textMuted }]}>{t.cancel}</Text>
      </View>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1 },
  scroll: { paddingHorizontal: 24, paddingTop: 16, paddingBottom: 24 },

  // Close
  closeBtn: {
    width: 36, height: 36, borderRadius: 18,
    justifyContent: 'center', alignItems: 'center',
    alignSelf: 'flex-end',
  },

  // Header
  header: { alignItems: 'center', marginTop: 8, marginBottom: 32 },
  flag: { fontSize: 40, marginBottom: 16 },
  title: { fontSize: 24, fontWeight: '800', textAlign: 'center', lineHeight: 30, marginBottom: 8 },
  subtitle: { fontSize: 15, textAlign: 'center', lineHeight: 21 },

  // Plans
  plans: { gap: 12, marginBottom: 20 },
  planCard: {
    borderRadius: 16, borderWidth: 1.5,
    paddingHorizontal: 18, paddingVertical: 18,
    position: 'relative',
  },
  planHighlight: {},
  planRadioRow: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  radio: {
    width: 22, height: 22, borderRadius: 11,
    borderWidth: 2, justifyContent: 'center', alignItems: 'center',
  },
  radioFill: { width: 12, height: 12, borderRadius: 6 },
  planInfo: { flex: 1 },
  planName: { fontSize: 16, fontWeight: '700', marginBottom: 2 },
  planSub: { fontSize: 13, fontWeight: '500' },
  planPrice: { fontSize: 15, fontWeight: '600' },
  planPriceHighlight: { fontSize: 18, fontWeight: '800' },

  // Badge
  badge: {
    position: 'absolute', top: -10, right: 16,
    paddingHorizontal: 12, paddingVertical: 4,
    borderRadius: 10,
  },
  badgeText: { fontSize: 11, fontWeight: '800', color: '#0F172A', textTransform: 'uppercase', letterSpacing: 0.5 },

  // Early access
  earlyRow: { alignItems: 'center', marginBottom: 24 },
  earlyText: { fontSize: 13, fontWeight: '600', textAlign: 'center' },

  // Features
  features: { gap: 14, marginBottom: 20 },
  featRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  featText: { fontSize: 15, fontWeight: '500' },

  // Bottom CTA
  bottomWrap: {
    paddingHorizontal: 24, paddingTop: 14, paddingBottom: 20,
    borderTopWidth: 1,
  },
  ctaBtn: {
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center',
    borderRadius: 16, paddingVertical: 17, gap: 8,
    marginBottom: 10,
  },
  ctaText: { fontSize: 17, fontWeight: '800', color: '#0F172A' },
  cancelText: { fontSize: 12, textAlign: 'center' },
});
