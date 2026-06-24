import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Platform, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { useRevenueCat, PRODUCT_IDS } from '../src/hooks/useRevenueCat';
import { api, PremiumPricingPlan } from '../src/services/api';
import { IS_PREVIEW_BUILD } from '../src/buildFlags';
import { LanguageSwitcher } from '../src/components/LanguageSwitcher';
import { AppBrand } from '../src/components/AppBrand';

const T2D_ICON = require('../assets/images/t2d-icon.png');

type Plan = 'monthly' | 'threemonth' | 'lifetime';

const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Lås opp full tilgang',
    subtitle: 'Øv ubegrenset og bestå teoriprøven raskere',
    monthly: 'Månedlig', monthlyPrice: '99 kr', monthlyPer: '/ mnd',
    threemonth: '3 måneder', threemonthPrice: '249 kr', threemonthPer: '/ 3 mnd', threemonthSub: 'Best verdi',
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
    paymentNotEnabled: 'Betaling er ikke aktivert ennå',
    paymentNotEnabledBody: 'Pakker kan vises, men kan ikke kjøpes ennå. Premium kan ikke aktiveres uten en bekreftet betaling.',
    limitTitle: 'Du har brukt gratisprøven',
    limitSubtitle: 'Lås opp Premium for ubegrenset tilgang',
  },
  th: {
    title: 'ปลดล็อคการเข้าถึงทั้งหมด',
    subtitle: 'ฝึกไม่จำกัดและสอบใบขับขี่ผ่านเร็วขึ้น',
    monthly: 'รายเดือน', monthlyPrice: '99 kr', monthlyPer: '/ เดือน',
    threemonth: '3 เดือน', threemonthPrice: '249 kr', threemonthPer: '/ 3 เดือน', threemonthSub: 'คุ้มที่สุด',
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
    paymentNotEnabled: 'ระบบชำระเงินยังไม่เปิดใช้งาน',
    paymentNotEnabledBody: 'ดูแพ็กเกจได้ แต่ยังซื้อไม่ได้ ไม่สามารถเปิดใช้งาน Premium ได้หากไม่มีการชำระเงินที่ยืนยันแล้ว',
    limitTitle: 'คุณใช้คำถามฟรีหมดแล้ว',
    limitSubtitle: 'ปลดล็อค Premium เพื่อใช้งานไม่จำกัด',
  },
  en: {
    title: 'Unlock full access',
    subtitle: 'Practice unlimited and pass the theory test faster',
    monthly: 'Monthly', monthlyPrice: '99 NOK', monthlyPer: '/ month',
    threemonth: '3 months', threemonthPrice: '249 NOK', threemonthPer: '/ 3 months', threemonthSub: 'Best value',
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
    paymentNotEnabled: 'Payments are not enabled yet',
    paymentNotEnabledBody: 'Packages can be shown but cannot be purchased yet. Premium cannot be activated without a confirmed payment.',
    limitTitle: 'You have used your free trial',
    limitSubtitle: 'Unlock Premium for unlimited access',
  },
};

export default function PaywallScreen() {
  const router = useRouter();
  const { language, colors, setPremium, isAuthenticated, freeRemaining, authToken, deviceId, refreshAccessStatus } = useAppStore();
  const t = TR[language] || {};
  const c = colors;
  // Default selection = Best Value (3 months)
  const [plan, setPlan] = useState<Plan>('threemonth');
  const [success, setSuccess] = useState(false);
  const [publicPricing, setPublicPricing] = useState<Record<string, PremiumPricingPlan>>({});
  const [stripePurchasing, setStripePurchasing] = useState(false);
  const [stripeError, setStripeError] = useState<string | null>(null);
  const isWeb = Platform.OS === 'web';
  const limitReached = freeRemaining() <= 0;

  const rc = useRevenueCat();

  useEffect(() => {
    let mounted = true;
    api.getPricing()
      .then((data) => {
        if (!mounted) return;
        const byId: Record<string, PremiumPricingPlan> = {};
        for (const p of data.plans || []) byId[p.id] = p;
        setPublicPricing(byId);
      })
      .catch(() => {});
    return () => { mounted = false; };
  }, []);

  // Use real prices from RevenueCat when available; then the public backend/Stripe pricing; then static fallback.
  const monthlyPkg = rc.packages.find(p => p.productId === PRODUCT_IDS.MONTHLY);
  const threePkg = rc.packages.find(p => p.productId === PRODUCT_IDS.THREE_MONTH);
  const lifePkg = rc.packages.find(p => p.productId === PRODUCT_IDS.LIFETIME);

  const monthlyPrice = monthlyPkg?.priceString || publicPricing.monthly?.display || t.monthlyPrice;
  const threePrice = threePkg?.priceString || publicPricing.three_months?.display || t.threemonthPrice;
  const lifePrice = lifePkg?.priceString || publicPricing.lifetime?.display || t.lifetimePrice;

  useEffect(() => { rc.clearError(); }, [plan]);

  useEffect(() => {
    if (!isWeb || !authToken || typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    const sessionId = params.get('session_id');
    if (params.get('checkout') !== 'success' || !sessionId) return;
    let mounted = true;
    setStripePurchasing(true);
    api.checkCheckoutStatus(sessionId, authToken)
      .then(async (res) => {
        if (!mounted) return;
        await refreshAccessStatus();
        if (res.is_premium) {
          await setPremium(true);
          setSuccess(true);
          window.history.replaceState({}, '', window.location.pathname);
          setTimeout(() => router.replace('/'), 1200);
        } else {
          setStripeError(t.paymentNotEnabledBody);
        }
      })
      .catch((e) => mounted && setStripeError(e.message || t.paymentNotEnabledBody))
      .finally(() => mounted && setStripePurchasing(false));
    return () => { mounted = false; };
  }, [isWeb, authToken, refreshAccessStatus, router, setPremium, t.paymentNotEnabledBody]);

  // ── Hard guard: payments only enabled when RevenueCat is fully initialized
  // AND we have at least one product loaded from the dashboard. Anything else
  // (preview build, web preview, missing/invalid API key, no offerings configured,
  // init crashed) means the store cannot verify a real purchase, and we MUST NOT
  // unlock premium without a confirmed payment.
  const paymentsEnabled =
    isWeb
      ? !IS_PREVIEW_BUILD
      : (!IS_PREVIEW_BUILD && rc.isAvailable && rc.packages.length > 0);

  const stripePlanId =
    plan === 'monthly' ? 'monthly' :
    plan === 'threemonth' ? 'three_months' :
    'lifetime';

  const onPurchase = async () => {
    // Preview build → buttons are dead. No SDK call, no setPremium, no router push.
    if (IS_PREVIEW_BUILD) return;

    if (!isAuthenticated) {
      router.push({ pathname: '/login', params: { redirect: 'paywall' } });
      return;
    }

    // Hard fail-closed: do not even attempt purchase if payments aren't ready.
    // This is the security gate that prevents the "auto-unlock without paying"
    // bug we hit when the RC API key was a test/placeholder.
    if (!paymentsEnabled) {
      // The UI already shows the "Betaling er ikke aktivert ennå" banner,
      // so we just ignore the tap silently rather than route anywhere.
      return;
    }

    if (isWeb) {
      if (!authToken || typeof window === 'undefined') return;
      setStripePurchasing(true);
      setStripeError(null);
      try {
        const base = window.location.origin + window.location.pathname;
        const session = await api.createCheckoutSession(stripePlanId, authToken, {
          deviceId,
          successUrl: `${base}?checkout=success&session_id={CHECKOUT_SESSION_ID}`,
          cancelUrl: `${base}?checkout=cancel`,
        });
        if (session.livemode && session.url) {
          window.location.href = session.url;
        } else {
          setStripeError(t.paymentNotEnabledBody);
        }
      } catch (e: any) {
        setStripeError(e.message || t.paymentNotEnabledBody);
      } finally {
        setStripePurchasing(false);
      }
      return;
    }

    const productId =
      plan === 'monthly' ? PRODUCT_IDS.MONTHLY :
      plan === 'threemonth' ? PRODUCT_IDS.THREE_MONTH :
      PRODUCT_IDS.LIFETIME;

    const ok = await rc.purchase(productId);
    // rc.purchase ONLY returns true when RevenueCat reports the entitlement
    // is active in customerInfo — i.e. the platform store confirmed the sale.
    // No other code path may set premium=true.
    if (ok) {
      await setPremium(true);
      setSuccess(true);
      setTimeout(() => router.replace('/'), 1200);
    }
    // If !ok the rc hook already populated rc.error with the reason
    // (cancelled / network / not active) and we stay on the paywall.
  };

  const onRestore = async () => {
    // Preview build → restore is dead. No SDK call.
    if (IS_PREVIEW_BUILD) return;
    // Restore is also gated — it must verify with the store. The rc hook
    // already returns false unless an active entitlement comes back from
    // Purchases.restorePurchases(), so this branch is safe.
    if (!paymentsEnabled) return;
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
    id, name, subLabel, price, per, ribbon, highlight,
  }: { id: Plan; name: string; subLabel?: string; price: string; per: string; ribbon?: string; highlight?: boolean }) => {
    const active = plan === id;
    return (
      <TouchableOpacity
        testID={`plan-${id}`}
        disabled={rc.purchasing}
        activeOpacity={0.85}
        onPress={() => setPlan(id)}
        style={[
          s.planCard,
          highlight && s.planCardHighlight,
          {
            backgroundColor: active ? c.accentBg : c.card,
            borderColor: active ? c.accent : (highlight ? `${c.accent}55` : c.cardBorder),
            borderWidth: highlight ? 2 : 1.5,
          },
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
            <Text style={[s.planName, { color: c.text, fontSize: highlight ? 17 : 15 }]}>{name}</Text>
            {subLabel ? (
              <Text style={[s.planSub, { color: active ? c.accent : c.textSecondary }]}>{subLabel}</Text>
            ) : null}
          </View>
          <View style={s.priceWrap}>
            <Text style={[s.planPrice, { color: active ? c.accent : c.text, fontSize: highlight ? 22 : 19 }]}>{price}</Text>
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
        {/* Brand + language switcher + close */}
        <View style={s.topRow}>
          <AppBrand size="md" />
          <View style={s.topRowRight}>
            <LanguageSwitcher size="sm" />
            <TouchableOpacity testID="paywall-close-btn" style={[s.closeBtn, { backgroundColor: c.card }]} onPress={() => router.back()} activeOpacity={0.7}>
              <Ionicons name="close" size={20} color={c.textSecondary} />
            </TouchableOpacity>
          </View>
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
          <PlanCard id="threemonth" name={t.threemonth} subLabel={t.threemonthSub} price={threePrice} per={t.threemonthPer} ribbon={t.bestValue} highlight />
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
        {(rc.error || stripeError) ? (
          <View style={[s.errorBox, { backgroundColor: c.incorrectBg }]}>
            <Ionicons name="alert-circle" size={16} color={c.incorrect} />
            <Text style={[s.errorText, { color: c.incorrect }]}>{rc.error || stripeError}</Text>
          </View>
        ) : null}

        {/* Payment-not-enabled banner — shown whenever payments are gated.
            This is the visible counterpart of the security guard in
            onPurchase: the user CANNOT activate premium without a confirmed
            payment, so we say so up-front to avoid confusion. */}
        {!paymentsEnabled && (
          <View style={[s.warnBox, { backgroundColor: c.incorrectBg, borderColor: c.incorrect }]}>
            <Ionicons name="lock-closed" size={16} color={c.incorrect} />
            <View style={{ flex: 1 }}>
              <Text style={[s.warnTitle, { color: c.incorrect }]}>{t.paymentNotEnabled}</Text>
              <Text style={[s.warnBody, { color: c.textSecondary }]}>{t.paymentNotEnabledBody}</Text>
            </View>
          </View>
        )}
      </ScrollView>

      {/* ─── Bottom CTA ─── */}
      <View style={[s.bottomWrap, { borderTopColor: c.divider, backgroundColor: c.bg }]}>
        <TouchableOpacity
          testID="paywall-cta-btn"
          disabled={rc.purchasing || stripePurchasing || !paymentsEnabled}
          style={[s.ctaBtn, { backgroundColor: (rc.purchasing || stripePurchasing || !paymentsEnabled) ? c.letterBg : c.accent }]}
          onPress={onPurchase}
          activeOpacity={0.85}
        >
          {rc.purchasing || stripePurchasing ? (
            <><ActivityIndicator size="small" color="#0F172A" /><Text style={s.ctaText}>{t.purchasing}</Text></>
          ) : !paymentsEnabled ? (
            <><Ionicons name="lock-closed" size={18} color={c.textMuted} /><Text style={[s.ctaText, { color: c.textMuted }]}>{t.paymentNotEnabled}</Text></>
          ) : (
            <><Ionicons name="flash" size={20} color="#0F172A" /><Text style={s.ctaText}>{t.cta}</Text></>
          )}
        </TouchableOpacity>

        {!isWeb && (
          <TouchableOpacity testID="restore-btn" style={s.restoreBtn} onPress={onRestore} disabled={rc.purchasing || !paymentsEnabled} activeOpacity={0.7}>
            <Text style={[s.restoreText, { color: paymentsEnabled ? c.textMuted : c.letterBg }]}>{t.restore}</Text>
          </TouchableOpacity>
        )}

        <Text style={[s.cancelText, { color: c.textMuted }]}>{t.cancel}</Text>
      </View>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1 },
  scroll: { paddingHorizontal: 22, paddingTop: 12, paddingBottom: 28 },
  closeBtn: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  topRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  topRowRight: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  header: { alignItems: 'center', marginTop: 8, marginBottom: 32 },
  brandIcon: { width: 68, height: 68, borderRadius: 16, marginBottom: 16 },
  limitBadge: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, marginBottom: 12 },
  limitBadgeText: { fontSize: 12, fontWeight: '700' },
  title: { fontSize: 26, fontWeight: '800', textAlign: 'center', lineHeight: 32, marginBottom: 8, letterSpacing: -0.4 },
  subtitle: { fontSize: 14, textAlign: 'center', lineHeight: 21, paddingHorizontal: 12 },

  plans: { gap: 14, marginBottom: 30 },
  planCard: { borderRadius: 16, paddingHorizontal: 18, paddingVertical: 16, position: 'relative' },
  planCardHighlight: { paddingVertical: 20, paddingHorizontal: 20, marginVertical: 2 },
  planRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  radio: { width: 20, height: 20, borderRadius: 10, borderWidth: 2, justifyContent: 'center', alignItems: 'center' },
  radioFill: { width: 10, height: 10, borderRadius: 5 },
  planInfo: { flex: 1 },
  planName: { fontSize: 16, fontWeight: '700' },
  planSub: { fontSize: 12, fontWeight: '600', marginTop: 2 },
  priceWrap: { alignItems: 'flex-end' },
  planPrice: { fontSize: 19, fontWeight: '800' },
  planPer: { fontSize: 11, marginTop: 1 },
  ribbon: { position: 'absolute', top: -10, right: 16, paddingHorizontal: 10, paddingVertical: 3, borderRadius: 8 },
  ribbonText: { fontSize: 10, fontWeight: '800', color: '#0F172A', textTransform: 'uppercase', letterSpacing: 0.5 },

  features: { gap: 14, marginBottom: 24 },
  featRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  featIconWrap: { width: 22, height: 22, borderRadius: 11, justifyContent: 'center', alignItems: 'center' },
  featText: { fontSize: 14, fontWeight: '500', flex: 1 },

  errorBox: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 14, paddingVertical: 10, borderRadius: 10, marginBottom: 8 },
  errorText: { fontSize: 13, flex: 1 },
  warnBox: { flexDirection: 'row', alignItems: 'flex-start', gap: 10, paddingHorizontal: 14, paddingVertical: 12, borderRadius: 12, marginTop: 4, borderWidth: 1.5 },
  warnTitle: { fontSize: 14, fontWeight: '800', marginBottom: 3 },
  warnBody: { fontSize: 12, fontWeight: '500', lineHeight: 17 },

  bottomWrap: { paddingHorizontal: 22, paddingTop: 14, paddingBottom: 20, borderTopWidth: 1 },
  ctaBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 16, paddingVertical: 19, gap: 8, marginBottom: 10 },
  ctaText: { fontSize: 17, fontWeight: '800', color: '#0F172A', letterSpacing: 0.2 },
  restoreBtn: { alignItems: 'center', paddingVertical: 6, marginBottom: 2 },
  restoreText: { fontSize: 13, fontWeight: '600' },
  cancelText: { fontSize: 11, textAlign: 'center' },

  successWrap: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 20 },
  successIcon: { width: 100, height: 100, borderRadius: 50, justifyContent: 'center', alignItems: 'center' },
  successText: { fontSize: 22, fontWeight: '800' },
});
