/**
 * GateModal — shown when a user has used up their free question quota.
 * Calm, non-punishing tone. Slides up from the bottom.
 *
 * Props:
 *   visible      — whether the modal is shown
 *   isGuest      — true = not logged in → show signup/login buttons
 *   onSignup     — navigate to signup
 *   onLogin      — navigate to login
 *   onPremium    — navigate to paywall (authenticated users)
 *   onDismiss    — close the modal without action
 *   language     — 'no' | 'th' | 'en'
 *   colors       — theme colors
 */
import React from 'react';
import {
  Modal, View, Text, StyleSheet, TouchableOpacity,
  TouchableWithoutFeedback,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { ThemeColors } from '../theme';

const TR: Record<string, Record<string, string>> = {
  no: {
    title:   'Dagens gratis spørsmål er brukt opp',
    body:    'Du har svart på alle gratispørsmålene for i dag. Opprett en gratis konto for 10 spørsmål per dag — eller oppgrader til Premium for ubegrenset tilgang.',
    bodyAuth:'Du har brukt opp dagens gratis spørsmål. Oppgrader til Premium for ubegrenset øving.',
    signup:  'Opprett gratis konto',
    login:   'Logg inn',
    premium: '⭐ Se Premium',
    dismiss: 'Lukk',
  },
  th: {
    title:   'คำถามฟรีวันนี้หมดแล้ว',
    body:    'คุณตอบคำถามฟรีครบแล้ว สร้างบัญชีฟรีเพื่อรับ 10 คำถามต่อวัน หรืออัพเกรดเป็น Premium เพื่อใช้ไม่จำกัด',
    bodyAuth:'คุณใช้คำถามฟรีวันนี้หมดแล้ว อัพเกรดเป็น Premium เพื่อฝึกได้ไม่จำกัด',
    signup:  'สร้างบัญชีฟรี',
    login:   'เข้าสู่ระบบ',
    premium: '⭐ ดู Premium',
    dismiss: 'ปิด',
  },
  en: {
    title:   "You've used today's free questions",
    body:    "You've answered all the free questions for today. Create a free account for 10 questions per day — or upgrade to Premium for unlimited access.",
    bodyAuth:"You've used up today's free questions. Upgrade to Premium for unlimited practice.",
    signup:  'Create free account',
    login:   'Log in',
    premium: '⭐ See Premium',
    dismiss: 'Close',
  },
};

interface GateModalProps {
  visible: boolean;
  isGuest: boolean;
  onSignup: () => void;
  onLogin: () => void;
  onPremium: () => void;
  onDismiss: () => void;
  language: string;
  colors: ThemeColors;
}

export function GateModal({
  visible, isGuest,
  onSignup, onLogin, onPremium, onDismiss,
  language, colors: c,
}: GateModalProps) {
  const t = TR[language] || {};

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onDismiss}
      statusBarTranslucent
    >
      <TouchableWithoutFeedback onPress={onDismiss}>
        <View style={st.backdrop} />
      </TouchableWithoutFeedback>

      <View style={[st.sheet, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
        {/* Handle */}
        <View style={[st.handle, { backgroundColor: c.divider }]} />

        {/* Icon */}
        <View style={[st.iconWrap, { backgroundColor: c.accentBg }]}>
          <Ionicons name="lock-closed" size={28} color={c.accent} />
        </View>

        {/* Title */}
        <Text style={[st.title, { color: c.text }]}>{t.title}</Text>

        {/* Body */}
        <Text style={[st.body, { color: c.textSecondary }]}>
          {isGuest ? t.body : t.bodyAuth}
        </Text>

        {/* Buttons */}
        <View style={st.btns}>
          {isGuest ? (
            <>
              <TouchableOpacity
                style={[st.primaryBtn, { backgroundColor: c.accent }]}
                onPress={onSignup}
                activeOpacity={0.85}
              >
                <Ionicons name="person-add-outline" size={18} color="#0F172A" />
                <Text style={st.primaryBtnText}>{t.signup}</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[st.secondaryBtn, { borderColor: c.cardBorder }]}
                onPress={onLogin}
                activeOpacity={0.8}
              >
                <Text style={[st.secondaryBtnText, { color: c.textSecondary }]}>{t.login}</Text>
              </TouchableOpacity>
            </>
          ) : (
            <TouchableOpacity
              style={[st.primaryBtn, { backgroundColor: c.accent }]}
              onPress={onPremium}
              activeOpacity={0.85}
            >
              <Text style={st.primaryBtnText}>{t.premium}</Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity
            style={st.dismissBtn}
            onPress={onDismiss}
            activeOpacity={0.7}
          >
            <Text style={[st.dismissText, { color: c.textMuted }]}>{t.dismiss}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const st = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  sheet: {
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    borderWidth: 1,
    borderBottomWidth: 0,
    padding: 28,
    paddingBottom: 40,
    alignItems: 'center',
  },
  handle: {
    width: 40, height: 4, borderRadius: 2,
    marginBottom: 24,
  },
  iconWrap: {
    width: 60, height: 60, borderRadius: 18,
    justifyContent: 'center', alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 18, fontWeight: '800',
    textAlign: 'center', marginBottom: 10,
    letterSpacing: -0.3,
  },
  body: {
    fontSize: 14, lineHeight: 21,
    textAlign: 'center', marginBottom: 28,
  },
  btns: {
    width: '100%', gap: 10,
  },
  primaryBtn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    borderRadius: 14, paddingVertical: 15, gap: 8,
  },
  primaryBtnText: {
    fontSize: 15, fontWeight: '800', color: '#0F172A',
  },
  secondaryBtn: {
    borderWidth: 1, borderRadius: 14,
    paddingVertical: 14, alignItems: 'center',
  },
  secondaryBtnText: {
    fontSize: 14, fontWeight: '600',
  },
  dismissBtn: {
    paddingVertical: 10, alignItems: 'center',
  },
  dismissText: {
    fontSize: 13, fontWeight: '600',
  },
});
