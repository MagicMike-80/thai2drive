import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';
import { api } from '../src/services/api';

const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Glemt passord',
    subtitle: 'Skriv inn e-posten din for \u00e5 f\u00e5 tilbakestillingskode',
    email: 'E-post',
    send: 'Send tilbakestillingskode',
    back: 'Tilbake til innlogging',
    emailError: 'Ugyldig e-postformat',
    codeSent: 'Tilbakestillingskode sendt! Sjekk e-posten din.',
    code: 'Tilbakestillingskode',
    newPass: 'Nytt passord',
    reset: 'Tilbakestill passord',
    passError: 'Passord m\u00e5 v\u00e6re minst 6 tegn',
    codeError: 'Skriv inn 6-sifret kode',
    success: 'Passord tilbakestilt! Logg inn med nytt passord.',
  },
  th: {
    title: '\u0e25\u0e37\u0e21\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19',
    subtitle: '\u0e01\u0e23\u0e2d\u0e01\u0e2d\u0e35\u0e40\u0e21\u0e25\u0e40\u0e1e\u0e37\u0e48\u0e2d\u0e23\u0e31\u0e1a\u0e23\u0e2b\u0e31\u0e2a\u0e23\u0e35\u0e40\u0e0b\u0e47\u0e15',
    email: '\u0e2d\u0e35\u0e40\u0e21\u0e25',
    send: '\u0e2a\u0e48\u0e07\u0e23\u0e2b\u0e31\u0e2a\u0e23\u0e35\u0e40\u0e0b\u0e47\u0e15',
    back: '\u0e01\u0e25\u0e31\u0e1a\u0e2a\u0e39\u0e48\u0e2b\u0e19\u0e49\u0e32\u0e40\u0e02\u0e49\u0e32\u0e2a\u0e39\u0e48\u0e23\u0e30\u0e1a\u0e1a',
    emailError: '\u0e23\u0e39\u0e1b\u0e41\u0e1a\u0e1a\u0e2d\u0e35\u0e40\u0e21\u0e25\u0e44\u0e21\u0e48\u0e16\u0e39\u0e01\u0e15\u0e49\u0e2d\u0e07',
    codeSent: '\u0e2a\u0e48\u0e07\u0e23\u0e2b\u0e31\u0e2a\u0e23\u0e35\u0e40\u0e0b\u0e47\u0e15\u0e41\u0e25\u0e49\u0e27! \u0e15\u0e23\u0e27\u0e08\u0e2a\u0e2d\u0e1a\u0e2d\u0e35\u0e40\u0e21\u0e25',
    code: '\u0e23\u0e2b\u0e31\u0e2a\u0e23\u0e35\u0e40\u0e0b\u0e47\u0e15',
    newPass: '\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19\u0e43\u0e2b\u0e21\u0e48',
    reset: '\u0e23\u0e35\u0e40\u0e0b\u0e47\u0e15\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19',
    passError: '\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19\u0e15\u0e49\u0e2d\u0e07\u0e21\u0e35\u0e2d\u0e22\u0e48\u0e32\u0e07\u0e19\u0e49\u0e2d\u0e22 6 \u0e15\u0e31\u0e27\u0e2d\u0e31\u0e01\u0e29\u0e23',
    codeError: '\u0e01\u0e23\u0e38\u0e13\u0e32\u0e01\u0e23\u0e2d\u0e01\u0e23\u0e2b\u0e31\u0e2a 6 \u0e2b\u0e25\u0e31\u0e01',
    success: '\u0e23\u0e35\u0e40\u0e0b\u0e47\u0e15\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19\u0e2a\u0e33\u0e40\u0e23\u0e47\u0e08! \u0e40\u0e02\u0e49\u0e32\u0e2a\u0e39\u0e48\u0e23\u0e30\u0e1a\u0e1a\u0e14\u0e49\u0e27\u0e22\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19\u0e43\u0e2b\u0e21\u0e48',
  },
  en: {
    title: 'Forgot Password',
    subtitle: 'Enter your email to receive a reset code',
    email: 'Email',
    send: 'Send Reset Code',
    back: 'Back to Login',
    emailError: 'Invalid email format',
    codeSent: 'Reset code sent! Check your email.',
    code: 'Reset Code',
    newPass: 'New Password',
    reset: 'Reset Password',
    passError: 'Password must be at least 6 characters',
    codeError: 'Enter 6-digit code',
    success: 'Password reset! Log in with your new password.',
  },
};

type Step = 'email' | 'code' | 'done';

export default function ForgotPasswordScreen() {
  const router = useRouter();
  const { language, colors } = useAppStore();
  const t = TR[language] || TR.en;
  const c = colors;

  const [step, setStep] = useState<Step>('email');
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPass, setShowPass] = useState(false);

  const validateEmail = (e: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.trim());

  const handleSendCode = async () => {
    setError('');
    const trimmedEmail = email.trim().toLowerCase();
    if (!validateEmail(trimmedEmail)) { setError(t.emailError); return; }

    setLoading(true);
    try {
      await api.forgotPassword(trimmedEmail);
      setStep('code');
    } catch (e: any) {
      setError(e.message || 'Failed to send code');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setError('');
    if (code.length !== 6) { setError(t.codeError); return; }
    if (newPassword.length < 6) { setError(t.passError); return; }

    setLoading(true);
    try {
      await api.resetPassword(email.trim().toLowerCase(), code, newPassword);
      setStep('done');
    } catch (e: any) {
      setError(e.message || 'Reset failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1 }}>
        <ScrollView contentContainerStyle={st.scroll} keyboardShouldPersistTaps="handled">
          {/* Back */}
          <TouchableOpacity testID="forgot-back-btn" style={[st.backBtn, { backgroundColor: c.card }]} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={22} color={c.text} />
          </TouchableOpacity>

          {/* Header */}
          <View style={st.headerSection}>
            <View style={[st.iconBg, { backgroundColor: c.accentBg }]}>
              <Ionicons name="key" size={32} color={c.accent} />
            </View>
            <Text style={[st.title, { color: c.text }]}>{t.title}</Text>
            <Text style={[st.subtitle, { color: c.textSecondary }]}>{step === 'done' ? t.success : t.subtitle}</Text>
          </View>

          {step === 'done' ? (
            <View style={st.form}>
              <View style={[st.successBox, { backgroundColor: c.correctBg }]}>
                <Ionicons name="checkmark-circle" size={20} color={c.correct} />
                <Text style={[st.successText, { color: c.correct }]}>{t.success}</Text>
              </View>
              <TouchableOpacity testID="back-to-login" style={[st.btn, { backgroundColor: c.accent }]} onPress={() => router.replace('/login')} activeOpacity={0.8}>
                <Ionicons name="log-in-outline" size={20} color="#0F172A" />
                <Text style={st.btnText}>{t.back}</Text>
              </TouchableOpacity>
            </View>
          ) : step === 'email' ? (
            <View style={st.form}>
              <View style={[st.inputWrap, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
                <Ionicons name="mail-outline" size={18} color={c.textMuted} />
                <TextInput
                  testID="forgot-email"
                  style={[st.input, { color: c.text }]}
                  placeholder={t.email}
                  placeholderTextColor={c.textMuted}
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>

              {error ? (
                <View style={[st.errorBox, { backgroundColor: c.incorrectBg }]}>
                  <Ionicons name="alert-circle" size={16} color={c.incorrect} />
                  <Text style={[st.errorText, { color: c.incorrect }]}>{error}</Text>
                </View>
              ) : null}

              <TouchableOpacity testID="send-code-btn" style={[st.btn, { backgroundColor: c.accent }]} onPress={handleSendCode} disabled={loading} activeOpacity={0.8}>
                {loading ? <ActivityIndicator color="#0F172A" /> : (
                  <>
                    <Ionicons name="send-outline" size={18} color="#0F172A" />
                    <Text style={st.btnText}>{t.send}</Text>
                  </>
                )}
              </TouchableOpacity>

              <TouchableOpacity testID="back-link" style={st.backLink} onPress={() => router.back()}>
                <Text style={[st.backLinkText, { color: c.textSecondary }]}>{t.back}</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={st.form}>
              <View style={[st.codeSentBox, { backgroundColor: c.accentBg }]}>
                <Ionicons name="mail-open-outline" size={18} color={c.accent} />
                <Text style={[st.codeSentText, { color: c.accent }]}>{t.codeSent}</Text>
              </View>

              <View style={[st.inputWrap, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
                <Ionicons name="keypad-outline" size={18} color={c.textMuted} />
                <TextInput
                  testID="reset-code"
                  style={[st.input, { color: c.text }]}
                  placeholder={t.code}
                  placeholderTextColor={c.textMuted}
                  value={code}
                  onChangeText={setCode}
                  keyboardType="number-pad"
                  maxLength={6}
                />
              </View>

              <View style={[st.inputWrap, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
                <Ionicons name="lock-closed-outline" size={18} color={c.textMuted} />
                <TextInput
                  testID="reset-new-pass"
                  style={[st.input, { color: c.text }]}
                  placeholder={t.newPass}
                  placeholderTextColor={c.textMuted}
                  value={newPassword}
                  onChangeText={setNewPassword}
                  secureTextEntry={!showPass}
                  autoCapitalize="none"
                />
                <TouchableOpacity onPress={() => setShowPass(!showPass)} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
                  <Ionicons name={showPass ? 'eye-off-outline' : 'eye-outline'} size={18} color={c.textMuted} />
                </TouchableOpacity>
              </View>

              {error ? (
                <View style={[st.errorBox, { backgroundColor: c.incorrectBg }]}>
                  <Ionicons name="alert-circle" size={16} color={c.incorrect} />
                  <Text style={[st.errorText, { color: c.incorrect }]}>{error}</Text>
                </View>
              ) : null}

              <TouchableOpacity testID="reset-btn" style={[st.btn, { backgroundColor: c.accent }]} onPress={handleReset} disabled={loading} activeOpacity={0.8}>
                {loading ? <ActivityIndicator color="#0F172A" /> : (
                  <>
                    <Ionicons name="refresh-outline" size={18} color="#0F172A" />
                    <Text style={st.btnText}>{t.reset}</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          )}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  container: { flex: 1 },
  scroll: { flexGrow: 1, padding: 24, paddingTop: 16 },
  backBtn: { width: 40, height: 40, borderRadius: 12, justifyContent: 'center', alignItems: 'center', alignSelf: 'flex-start', marginBottom: 12 },
  headerSection: { alignItems: 'center', marginBottom: 32 },
  iconBg: { width: 72, height: 72, borderRadius: 36, justifyContent: 'center', alignItems: 'center', marginBottom: 14 },
  title: { fontSize: 26, fontWeight: '800', marginBottom: 6 },
  subtitle: { fontSize: 14, textAlign: 'center', lineHeight: 20 },
  form: { gap: 14 },
  inputWrap: { flexDirection: 'row', alignItems: 'center', borderRadius: 14, borderWidth: 1, paddingHorizontal: 14, height: 52, gap: 10 },
  input: { flex: 1, fontSize: 15, height: '100%' },
  errorBox: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 14, paddingVertical: 10, borderRadius: 10 },
  errorText: { fontSize: 13, flex: 1 },
  successBox: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingHorizontal: 16, paddingVertical: 14, borderRadius: 12 },
  successText: { fontSize: 14, fontWeight: '600', flex: 1 },
  codeSentBox: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingHorizontal: 16, paddingVertical: 14, borderRadius: 12 },
  codeSentText: { fontSize: 13, fontWeight: '600', flex: 1 },
  btn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 15, gap: 8, marginTop: 4 },
  btnText: { fontSize: 16, fontWeight: '700', color: '#0F172A' },
  backLink: { alignItems: 'center', paddingVertical: 10 },
  backLinkText: { fontSize: 14, fontWeight: '600' },
});
