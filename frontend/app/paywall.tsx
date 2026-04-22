import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Platform, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { useRevenueCat, PRODUCT_IDS } from '../src/hooks/useRevenueCat';
import { LanguageSwitcher } from '../src/components/LanguageSwitcher';

const T2D_ICON = require('../assets/images/t2d-icon.png');

type Plan = 'monthly' | 'threemonth' | 'lifetime';

const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Lås opp full tilgang',
    subtitle: 'Øv ubegrenset og bestå teoriprøven raskere',
    monthly: 'Månedlig', monthlyPrice: '199 kr', monthlyPer: '/ mnd',
    threemonth: '3 måneder', threemonthPrice: '399 kr', threemonthPer: '/ 3 mnd', threemonthSub: 'Best verdi – spar 34%',
    lifetime: 'Livstid', lifetimePrice: '699 kr', lifetimePer: 'engangsbetaling', lifetimeSub: 'Betal én gang – bruk for alltid',
    popular: 'Populær',
    bestValue: 'Beste verdi',
    feat1: 'Ubegrensede spørsmål hver dag',
    feat2: 'Norsk + Thai + Engelsk',
    feat3: 'Full eksamensmodus og repetisjon',
    feat4: 'Forklaringer på alle spørsmål',
    feat5: 'Ingen annonser',
    cta: 'Start nå',
    cancel: 'Avslutt når som helst',
    restore: 'Gjenopprett kjøp',
    purchasing: 'Behandler...',
    success: 'Premium aktivert!',
    webNote: 'Betaling krever mobilappen',
    limitTitle: 'Du har brukt dagens 10 gratis spørsmål',
    limitSubtitle: 'Lås opp Premium for ubegrenset tilgang',
  },
  th: {
    title: 'ปลดล็อคการเข้าถึงทั้งหมด',
    subtitle: 'ฝึกไม่จำกัดและสอบใบขับขี่ผ่านเร็วขึ้น',
    monthly: 'รายเดือน', monthlyPrice: '199 kr', monthlyPer: '/ เดือน',
    threemonth: '3 เดือน', threemonthPrice: '399 kr', threemonthPer: '/ 3 เดือน', threemonthSub: 'คุ้มที่สุด – ประหยัด 34%',
    lifetime: 'ตลอดชีพ', lifetimePrice: '699 kr', lifetimePer: 'จ่ายครั้งเดียว', lifetimeSub: 'จ่ายครั้งเดียว – ใช้ได้ตลอดไป',
    popular: 'ยอดนิยม',
    bestValue: 'คุ้มที่สุด',
    feat1: 'คำถามไม่จำกัดทุกวัน',
    feat2: 'นอร์เวย์ + ไทย + อังกฤษ',
    feat3: 'โหมดสอบและทบทวนเต็มรูปแบบ',
    feat4: 'คำอธิบายทุกข้อ',
    feat5: 'ไม่มีโฆษณา',
    cta: 'เริ่มเลย',
    cancel: 'ยกเลิกได้ทุกเมื่อ',
    restore: 'กู้คืนการซื้อ',
    purchasing: 'กำลังดำเนินการ...',
    success: 'เปิดใช้งาน Premium แล้ว!',
    webNote: 'การชำระเงินต้องใช้แอปมือถือ',
    limitTitle: 'คุณใช้ 10 ข้อฟรีของวันนี้ครบแล้ว',
    limitSubtitle: 'ปลดล็อค Premium เพื่อใช้งานไม่จำกัด',
  },
  en: {
    title: 'Unlock full access',
    subtitle: 'Practice unlimited and pass the theory test faster',
    monthly: 'Monthly', monthlyPrice: '199 NOK', monthlyPer: '/ month',
    threemonth: '3 months', threemonthPrice: '399 NOK', threemonthPer: '/ 3 months', threemonthSub: 'Best value – save 34%',
    lifetime: 'Lifetime', lifetimePrice: '699 NOK', lifetimePer: 'one-time payment', lifetimeSub: 'Pay once – use forever',
    popular: 'Popular',
    bestValue: 'Best Value',
    feat1: 'Unlimited questions every day',
    feat2: 'Norwegian + Thai + English',
    feat3: 'Full exam mode and review',
    feat4: 'Explanations on all questions',
    feat5: 'No ads',
    cta: 'Start now',
    cancel: 'Cancel anytime',
    restore: 'Restore purchase',
    purchasing: 'Processing...',
    success: 'Premium activated!',
    webNote: 'Payment requires the mobile app',
    limitTitle: 'You have used today\'s 10 free questions',
    limitSubtitle: 'Unlock Premium for unlimited access',
  },
};

export default function PaywallScreen() {
  const router = useRouter();
  const { language, colors, setPremium, isAuthenticated, freeRemaining } = useAppStore();
  const t = TR[language] || TR.en;
  const c = colors;
  // Default selection = Best Value (3 months)
  const [plan, setPlan] = useState<Plan>('threemonth');
  const [success, setSuccess] = useState(false);
  const isWeb = Platform.OS === 'web';
  const limitReached = freeRemaining() <= 0;

  const rc = useRevenueCat();

  // Use real prices from RevenueCat when available; fallback to the hard-coded UI prices.
  const monthlyPkg = rc.packages.find(p => p.productId === PRODUCT_IDS.MONTHLY);
  const threePkg = rc.packages.find(p => p.productId === PRODUCT_IDS.THREE_MONTH);
  const lifePkg = rc.packages.find(p => p.productId === PRODUCT_IDS.LIFETIME);

  const monthlyPrice = monthlyPkg?.priceString || t.monthlyPrice;
  const threePrice = threePkg?.priceString || t.threemonthPrice;
  const lifePrice = lifePkg?.priceString || t.lifetimePrice;

  useEffect(() => { rc.clearError(); }, [plan]);

  const onPurchase = async () => {
    if (!isAuthenticated) {
      router.push({ pathname: '/login', params: { redirect: 'paywall' } });
      return;
    }

    const productId =
      plan === 'monthly' ? PRODUCT_IDS.MONTHLY :
      plan === 'threemonth' ? PRODUCT_IDS.THREE_MONTH :
      PRODUCT_IDS.LIFETIME;

    if (rc.isAvailable) {
      const ok = await rc.purchase(productId);
      if (ok) {
        await setPremium(true);
        setSuccess(true);
        setTimeout(() => router.replace('/'), 1200);
      }
    } else {
      // Web preview fallback (MOCKED for now — real RC runs in native build)
      await setPremium(true);
      setSuccess(true);
      setTimeout(() => router.replace('/'), 1200);
    }
  };

  const onRestore = async () => {
    if (!rc.isAvailable) return;
    const ok = await rc.restore();
    if (ok) {
      await setPremium(true);
      setSuccess(true);
      setTimeout(() => router.replace('/'), 1200);
    }
  };

  // ─── Success screen ───
  if (success) {
    return (
      <SafeAreaView style={[s.container, { backgroundColor: c.bg }]}>
        <View style={s.successWrap}>
          <View style={[s.successIcon, { backgroundColor: `${c.correct}18` }]}>
            <Ionicons name="checkmark-circle" size={56} color={c.correct} />
          </View>
          <Text style={[s.successText, { color: c.text }]}>{t.success}</Text>
        </View>
      </SafeAreaView>
    );
  }

  const PlanCard = ({
    id, name, subLabel, price, per, ribbon,
  }: { id: Plan; name: string; subLabel?: string; price: string; per: string; ribbon?: string }) => {
    const active = plan === id;
    return (
      <TouchableOpacity
        testID={`plan-${id}`}
        disabled={rc.purchasing}
        activeOpacity={0.85}
        onPress={() => setPlan(id)}
        style={[
          s.planCard,
          { backgroundColor: active ? c.accentBg : c.card, borderColor: active ? c.accent : c.cardBorder },
        ]}
      >
        {ribbon && (
          <View style={[s.ribbon, { backgroundColor: c.accent }]}>
            <Text style={s.ribbonText}>{ribbon}</Text>
          </View>
        )}
        <View style={s.planRow}>
          <View style={[s.radio, { borderColor: active ? c.accent : c.textMuted }]}>
            {active && <View style={[s.radioFill, { backgroundColor: c.accent }]} />}
          </View>
          <View style={s.planInfo}>
            <Text style={[s.planName, { color: c.text }]}>{name}</Text>
            {subLabel ? (
              <Text style={[s.planSub, { color: active ? c.accent : c.textSecondary }]}>{subLabel}</Text>
            ) : null}
          </View>
          <View style={s.priceWrap}>
            <Text style={[s.planPrice, { color: active ? c.accent : c.text }]}>{price}</Text>
            <Text style={[s.planPer, { color: c.textMuted }]}>{per}</Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  // ─── Main paywall ───
  return (
    <SafeAreaView style={[s.container, { backgroundColor: c.bg }]}>
      <ScrollView contentContainerStyle={s.scroll} showsVerticalScrollIndicator={false}>
        {/* Close + language switcher */}
        <View style={s.topRow}>
          <LanguageSwitcher size="sm" />
          <TouchableOpacity testID="paywall-close-btn" style={[s.closeBtn, { backgroundColor: c.card }]} onPress={() => router.back()} activeOpacity={0.7}>
            <Ionicons name="close" size={20} color={c.textSecondary} />
          </TouchableOpacity>
        </View>

        {/* Header */}
        <View style={s.header}>
          <Image source={T2D_ICON} style={s.brandIcon} />
          {limitReached ? (
            <>
              <View style={[s.limitBadge, { backgroundColor: `${c.incorrect}18` }]}>
                <Ionicons name="lock-closed" size={16} color={c.incorrect} />
                <Text style={[s.limitBadgeText, { color: c.incorrect }]}>{t.limitTitle}</Text>
              </View>
              <Text style={[s.title, { color: c.text }]}>{t.title}</Text>
              <Text style={[s.subtitle, { color: c.textSecondary }]}>{t.limitSubtitle}</Text>
            </>
          ) : (
            <>
              <Text style={[s.title, { color: c.text }]}>{t.title}</Text>
              <Text style={[s.subtitle, { color: c.textSecondary }]}>{t.subtitle}</Text>
            </>
          )}
        </View>

        {/* ─── Plans ─── */}
        <View style={s.plans}>
          <PlanCard id="monthly" name={t.monthly} price={monthlyPrice} per={t.monthlyPer} />
          <PlanCard id="threemonth" name={t.threemonth} subLabel={t.threemonthSub} price={threePrice} per={t.threemonthPer} ribbon={t.bestValue} />
          <PlanCard id="lifetime" name={t.lifetime} subLabel={t.lifetimeSub} price={lifePrice} per={t.lifetimePer} ribbon={t.popular} />
        </View>

        {/* Features */}
        <View style={s.features}>
          {[t.feat1, t.feat2, t.feat3, t.feat4, t.feat5].map((f, i) => (
            <View key={i} style={s.featRow}>
              <View style={[s.featIconWrap, { backgroundColor: `${c.correct}18` }]}>
                <Ionicons name="checkmark" size={14} color={c.correct} />
              </View>
              <Text style={[s.featText, { color: c.text }]}>{f}</Text>
            </View>
          ))}
        </View>

        {/* Error */}
        {rc.error ? (
          <View style={[s.errorBox, { backgroundColor: c.incorrectBg }]}>
            <Ionicons name="alert-circle" size={16} color={c.incorrect} />
            <Text style={[s.errorText, { color: c.incorrect }]}>{rc.error}</Text>
          </View>
        ) : null}

        {/* Web notice */}
        {isWeb && (
          <View style={[s.webNote, { backgroundColor: c.accentBg }]}>
            <Ionicons name="phone-portrait-outline" size={16} color={c.accent} />
            <Text style={[s.webNoteText, { color: c.accent }]}>{t.webNote}</Text>
          </View>
        )}
      </ScrollView>

      {/* ─── Bottom CTA ─── */}
      <View style={[s.bottomWrap, { borderTopColor: c.divider, backgroundColor: c.bg }]}>
        <TouchableOpacity
          testID="paywall-cta-btn"
          disabled={rc.purchasing}
          style={[s.ctaBtn, { backgroundColor: rc.purchasing ? c.letterBg : c.accent }]}
          onPress={onPurchase}
          activeOpacity={0.85}
        >
          {rc.purchasing ? (
            <><ActivityIndicator size="small" color="#0F172A" /><Text style={s.ctaText}>{t.purchasing}</Text></>
          ) : (
            <><Ionicons name="flash" size={20} color="#0F172A" /><Text style={s.ctaText}>{t.cta}</Text></>
          )}
        </TouchableOpacity>

        {!isWeb && (
          <TouchableOpacity testID="restore-btn" style={s.restoreBtn} onPress={onRestore} disabled={rc.purchasing} activeOpacity={0.7}>
            <Text style={[s.restoreText, { color: c.textMuted }]}>{t.restore}</Text>
          </TouchableOpacity>
        )}

        <Text style={[s.cancelText, { color: c.textMuted }]}>{t.cancel}</Text>
      </View>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1 },
  scroll: { paddingHorizontal: 20, paddingTop: 12, paddingBottom: 24 },
  closeBtn: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  topRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  header: { alignItems: 'center', marginTop: 4, marginBottom: 24 },
  brandIcon: { width: 64, height: 64, borderRadius: 14, marginBottom: 14 },
  limitBadge: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, marginBottom: 10 },
  limitBadgeText: { fontSize: 12, fontWeight: '700' },
  title: { fontSize: 24, fontWeight: '800', textAlign: 'center', lineHeight: 30, marginBottom: 6 },
  subtitle: { fontSize: 14, textAlign: 'center', lineHeight: 20, paddingHorizontal: 12 },

  plans: { gap: 10, marginBottom: 22 },
  planCard: { borderRadius: 14, borderWidth: 1.5, paddingHorizontal: 16, paddingVertical: 14, position: 'relative' },
  planRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  radio: { width: 20, height: 20, borderRadius: 10, borderWidth: 2, justifyContent: 'center', alignItems: 'center' },
  radioFill: { width: 10, height: 10, borderRadius: 5 },
  planInfo: { flex: 1 },
  planName: { fontSize: 16, fontWeight: '700' },
  planSub: { fontSize: 12, fontWeight: '600', marginTop: 2 },
  priceWrap: { alignItems: 'flex-end' },
  planPrice: { fontSize: 17, fontWeight: '800' },
  planPer: { fontSize: 11, marginTop: 1 },
  ribbon: { position: 'absolute', top: -9, right: 14, paddingHorizontal: 10, paddingVertical: 3, borderRadius: 8 },
  ribbonText: { fontSize: 10, fontWeight: '800', color: '#0F172A', textTransform: 'uppercase', letterSpacing: 0.5 },

  features: { gap: 12, marginBottom: 18 },
  featRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  featIconWrap: { width: 22, height: 22, borderRadius: 11, justifyContent: 'center', alignItems: 'center' },
  featText: { fontSize: 14, fontWeight: '500', flex: 1 },

  errorBox: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 14, paddingVertical: 10, borderRadius: 10, marginBottom: 8 },
  errorText: { fontSize: 13, flex: 1 },
  webNote: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 14, paddingVertical: 10, borderRadius: 10, marginTop: 4 },
  webNoteText: { fontSize: 12, fontWeight: '600' },

  bottomWrap: { paddingHorizontal: 20, paddingTop: 12, paddingBottom: 18, borderTopWidth: 1 },
  ctaBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 16, gap: 8, marginBottom: 8 },
  ctaText: { fontSize: 16, fontWeight: '800', color: '#0F172A' },
  restoreBtn: { alignItems: 'center', paddingVertical: 6, marginBottom: 2 },
  restoreText: { fontSize: 13, fontWeight: '600' },
  cancelText: { fontSize: 11, textAlign: 'center' },

  successWrap: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 20 },
  successIcon: { width: 100, height: 100, borderRadius: 50, justifyContent: 'center', alignItems: 'center' },
  successText: { fontSize: 22, fontWeight: '800' },
});
