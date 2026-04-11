import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';

const FREE_LIMIT = 5;

const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Lås opp Thai2Drive',
    subtitle: 'Få ubegrenset tilgang til alle spørsmål',
    freeUsed: 'Du har brukt dine gratis spørsmål',
    freeOf: 'av',
    freeQuestions: 'gratis spørsmål brukt',
    weekly: 'Ukentlig',
    monthly: 'Månedlig',
    special: 'Spesial',
    perWeek: '/ uke',
    perMonth: '/ mnd',
    first50: 'Første 50 brukere',
    popular: 'Populær',
    bestDeal: 'Beste tilbud',
    unlock: 'Lås opp Premium',
    startFree: 'Fortsett gratis',
    freeLeft: 'gratis spørsmål igjen',
    features: 'Premium inkluderer',
    feat1: 'Ubegrenset antall spørsmål',
    feat2: 'Full eksamenssimulering',
    feat3: 'Alle kategorier',
    feat4: 'Bokmerker og historikk',
    feat5: 'Ingen reklame',
    restore: 'Gjenopprett kjøp',
  },
  th: {
    title: 'ปลดล็อค Thai2Drive',
    subtitle: 'เข้าถึงคำถามทั้งหมดอย่างไม่จำกัด',
    freeUsed: 'คุณใช้คำถามฟรีหมดแล้ว',
    freeOf: 'จาก',
    freeQuestions: 'คำถามฟรีที่ใช้แล้ว',
    weekly: 'รายสัปดาห์',
    monthly: 'รายเดือน',
    special: 'พิเศษ',
    perWeek: '/ สัปดาห์',
    perMonth: '/ เดือน',
    first50: '50 คนแรก',
    popular: 'ยอดนิยม',
    bestDeal: 'คุ้มที่สุด',
    unlock: 'ปลดล็อค Premium',
    startFree: 'ใช้ฟรีต่อ',
    freeLeft: 'คำถามฟรีที่เหลือ',
    features: 'Premium รวม',
    feat1: 'คำถามไม่จำกัด',
    feat2: 'จำลองสอบเต็มรูปแบบ',
    feat3: 'ทุกหมวดหมู่',
    feat4: 'บุ๊คมาร์คและประวัติ',
    feat5: 'ไม่มีโฆษณา',
    restore: 'กู้คืนการซื้อ',
  },
  en: {
    title: 'Unlock Thai2Drive',
    subtitle: 'Get unlimited access to all questions',
    freeUsed: 'You\'ve used your free questions',
    freeOf: 'of',
    freeQuestions: 'free questions used',
    weekly: 'Weekly',
    monthly: 'Monthly',
    special: 'Special',
    perWeek: '/ week',
    perMonth: '/ month',
    first50: 'First 50 users',
    popular: 'Popular',
    bestDeal: 'Best deal',
    unlock: 'Unlock Premium',
    startFree: 'Continue Free',
    freeLeft: 'free questions left',
    features: 'Premium includes',
    feat1: 'Unlimited questions',
    feat2: 'Full exam simulation',
    feat3: 'All categories',
    feat4: 'Bookmarks & history',
    feat5: 'No ads',
    restore: 'Restore purchase',
  },
};

type Plan = 'weekly' | 'monthly' | 'special';

export default function PaywallScreen() {
  const router = useRouter();
  const { language, colors, freeQuestionsUsed, freeRemaining, setPremium, canAnswerFree } = useAppStore();
  const t = TR[language] || TR.en;
  const c = colors;
  const [selectedPlan, setSelectedPlan] = useState<Plan>('special');
  const remaining = freeRemaining();
  const canContinueFree = canAnswerFree();

  const handleUnlock = async () => {
    // MOCKED — in production, integrate with App Store / Google Play
    await setPremium(true);
    router.back();
  };

  const FEATURES = [t.feat1, t.feat2, t.feat3, t.feat4, t.feat5];

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <ScrollView contentContainerStyle={st.scroll} showsVerticalScrollIndicator={false}>
        {/* Close */}
        <TouchableOpacity testID="paywall-close-btn" style={[st.closeBtn, { backgroundColor: c.card }]} onPress={() => router.back()}>
          <Ionicons name="close" size={20} color={c.text} />
        </TouchableOpacity>

        {/* Header */}
        <View style={st.headerSection}>
          <View style={[st.crownBg, { backgroundColor: c.accentBg }]}>
            <Ionicons name="diamond" size={40} color={c.accent} />
          </View>
          <Text style={[st.title, { color: c.text }]}>{t.title}</Text>
          <Text style={[st.subtitle, { color: c.textSecondary }]}>{t.subtitle}</Text>
        </View>

        {/* Free usage indicator */}
        <View style={[st.freeBar, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
          <View style={st.freeRow}>
            <Text style={[st.freeLabel, { color: c.textSecondary }]}>
              {freeQuestionsUsed} {t.freeOf} {FREE_LIMIT} {t.freeQuestions}
            </Text>
          </View>
          <View style={[st.freeTrack, { backgroundColor: c.progressBg }]}>
            <View style={[st.freeFill, { width: `${Math.min(100, (freeQuestionsUsed / FREE_LIMIT) * 100)}%`, backgroundColor: freeQuestionsUsed >= FREE_LIMIT ? c.incorrect : c.accent }]} />
          </View>
        </View>

        {/* Plans */}
        <View style={st.plans}>
          {/* Weekly */}
          <TouchableOpacity
            testID="plan-weekly"
            style={[st.planCard, { backgroundColor: c.card, borderColor: selectedPlan === 'weekly' ? c.accent : c.cardBorder }]}
            onPress={() => setSelectedPlan('weekly')}
            activeOpacity={0.8}
          >
            <Text style={[st.planName, { color: c.text }]}>{t.weekly}</Text>
            <View style={st.priceRow}>
              <Text style={[st.price, { color: c.text }]}>99 kr</Text>
              <Text style={[st.pricePer, { color: c.textMuted }]}>{t.perWeek}</Text>
            </View>
          </TouchableOpacity>

          {/* Monthly */}
          <TouchableOpacity
            testID="plan-monthly"
            style={[st.planCard, { backgroundColor: c.card, borderColor: selectedPlan === 'monthly' ? c.accent : c.cardBorder }]}
            onPress={() => setSelectedPlan('monthly')}
            activeOpacity={0.8}
          >
            <View style={[st.badge, { backgroundColor: c.accentBg }]}>
              <Text style={[st.badgeText, { color: c.accent }]}>{t.popular}</Text>
            </View>
            <Text style={[st.planName, { color: c.text }]}>{t.monthly}</Text>
            <View style={st.priceRow}>
              <Text style={[st.price, { color: c.text }]}>199 kr</Text>
              <Text style={[st.pricePer, { color: c.textMuted }]}>{t.perMonth}</Text>
            </View>
          </TouchableOpacity>

          {/* Special */}
          <TouchableOpacity
            testID="plan-special"
            style={[st.planCard, st.planSpecial, { backgroundColor: c.card, borderColor: selectedPlan === 'special' ? c.accent : c.cardBorder }]}
            onPress={() => setSelectedPlan('special')}
            activeOpacity={0.8}
          >
            <View style={[st.badge, { backgroundColor: `${c.correct}18` }]}>
              <Text style={[st.badgeText, { color: c.correct }]}>{t.bestDeal}</Text>
            </View>
            <Text style={[st.planName, { color: c.text }]}>{t.special}</Text>
            <View style={st.priceRow}>
              <Text style={[st.price, { color: c.accent }]}>99 kr</Text>
              <Text style={[st.pricePer, { color: c.textMuted }]}>{t.perMonth}</Text>
            </View>
            <Text style={[st.specialNote, { color: c.textMuted }]}>{t.first50}</Text>
          </TouchableOpacity>
        </View>

        {/* Features */}
        <View style={st.featSection}>
          <Text style={[st.featTitle, { color: c.textMuted }]}>{t.features}</Text>
          {FEATURES.map((f, i) => (
            <View key={i} style={st.featRow}>
              <Ionicons name="checkmark-circle" size={18} color={c.correct} />
              <Text style={[st.featText, { color: c.text }]}>{f}</Text>
            </View>
          ))}
        </View>
      </ScrollView>

      {/* Actions */}
      <View style={[st.actionWrap, { borderTopColor: c.divider }]}>
        <TouchableOpacity testID="paywall-unlock-btn" style={[st.unlockBtn, { backgroundColor: c.accent }]} onPress={handleUnlock} activeOpacity={0.8}>
          <Ionicons name="diamond" size={18} color="#0F172A" />
          <Text style={st.unlockText}>{t.unlock}</Text>
        </TouchableOpacity>

        {canContinueFree && (
          <TouchableOpacity testID="paywall-free-btn" style={st.freeBtn} onPress={() => router.back()} activeOpacity={0.7}>
            <Text style={[st.freeText, { color: c.textSecondary }]}>
              {t.startFree} ({remaining} {t.freeLeft})
            </Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity style={st.restoreBtn} onPress={handleUnlock} activeOpacity={0.7}>
          <Text style={[st.restoreText, { color: c.textMuted }]}>{t.restore}</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  container: { flex: 1 },
  scroll: { paddingHorizontal: 20, paddingTop: 16, paddingBottom: 20 },
  closeBtn: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center', alignSelf: 'flex-end' },
  headerSection: { alignItems: 'center', marginTop: 8, marginBottom: 24 },
  crownBg: { width: 80, height: 80, borderRadius: 40, justifyContent: 'center', alignItems: 'center', marginBottom: 16 },
  title: { fontSize: 26, fontWeight: '800', marginBottom: 6 },
  subtitle: { fontSize: 15, textAlign: 'center', lineHeight: 21 },
  freeBar: { borderRadius: 14, padding: 14, marginBottom: 24, borderWidth: 1 },
  freeRow: { marginBottom: 8 },
  freeLabel: { fontSize: 13, fontWeight: '600' },
  freeTrack: { height: 6, borderRadius: 3 },
  freeFill: { height: '100%', borderRadius: 3 },
  plans: { gap: 10, marginBottom: 24 },
  planCard: { borderRadius: 14, padding: 16, borderWidth: 1.5 },
  planSpecial: {},
  badge: { alignSelf: 'flex-start', paddingHorizontal: 10, paddingVertical: 3, borderRadius: 10, marginBottom: 8 },
  badgeText: { fontSize: 11, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 0.5 },
  planName: { fontSize: 15, fontWeight: '700', marginBottom: 4 },
  priceRow: { flexDirection: 'row', alignItems: 'baseline', gap: 4 },
  price: { fontSize: 24, fontWeight: '800' },
  pricePer: { fontSize: 13 },
  specialNote: { fontSize: 12, marginTop: 4 },
  featSection: { marginBottom: 20 },
  featTitle: { fontSize: 12, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 },
  featRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 10 },
  featText: { fontSize: 14 },
  actionWrap: { paddingHorizontal: 20, paddingTop: 12, paddingBottom: 16, borderTopWidth: 1 },
  unlockBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 15, gap: 8, marginBottom: 10 },
  unlockText: { fontSize: 16, fontWeight: '700', color: '#0F172A' },
  freeBtn: { alignItems: 'center', paddingVertical: 10, marginBottom: 4 },
  freeText: { fontSize: 14, fontWeight: '600' },
  restoreBtn: { alignItems: 'center', paddingVertical: 6 },
  restoreText: { fontSize: 12 },
});
