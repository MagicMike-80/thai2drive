import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';

const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Opprett konto',
    subtitle: 'Begynn \u00e5 \u00f8ve p\u00e5 f\u00f8rerpr\u00f8ven',
    email: 'E-post',
    password: 'Passord',
    confirm: 'Bekreft passord',
    signUp: 'Registrer deg',
    hasAccount: 'Har du allerede konto?',
    login: 'Logg inn',
    emailError: 'Ugyldig e-postformat',
    passError: 'Passord m\u00e5 v\u00e6re minst 6 tegn',
    matchError: 'Passordene samsvarer ikke',
  },
  th: {
    title: '\u0e2a\u0e23\u0e49\u0e32\u0e07\u0e1a\u0e31\u0e0d\u0e0a\u0e35',
    subtitle: '\u0e40\u0e23\u0e34\u0e48\u0e21\u0e1d\u0e36\u0e01\u0e2a\u0e2d\u0e1a\u0e43\u0e1a\u0e02\u0e31\u0e1a\u0e02\u0e35\u0e48',
    email: '\u0e2d\u0e35\u0e40\u0e21\u0e25',
    password: '\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19',
    confirm: '\u0e22\u0e37\u0e19\u0e22\u0e31\u0e19\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19',
    signUp: '\u0e2a\u0e21\u0e31\u0e04\u0e23\u0e2a\u0e21\u0e32\u0e0a\u0e34\u0e01',
    hasAccount: '\u0e21\u0e35\u0e1a\u0e31\u0e0d\u0e0a\u0e35\u0e41\u0e25\u0e49\u0e27?',
    login: '\u0e40\u0e02\u0e49\u0e32\u0e2a\u0e39\u0e48\u0e23\u0e30\u0e1a\u0e1a',
    emailError: '\u0e23\u0e39\u0e1b\u0e41\u0e1a\u0e1a\u0e2d\u0e35\u0e40\u0e21\u0e25\u0e44\u0e21\u0e48\u0e16\u0e39\u0e01\u0e15\u0e49\u0e2d\u0e07',
    passError: '\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19\u0e15\u0e49\u0e2d\u0e07\u0e21\u0e35\u0e2d\u0e22\u0e48\u0e32\u0e07\u0e19\u0e49\u0e2d\u0e22 6 \u0e15\u0e31\u0e27\u0e2d\u0e31\u0e01\u0e29\u0e23',
    matchError: '\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19\u0e44\u0e21\u0e48\u0e15\u0e23\u0e07\u0e01\u0e31\u0e19',
  },
  en: {
    title: 'Create Account',
    subtitle: 'Start practicing for your driving test',
    email: 'Email',
    password: 'Password',
    confirm: 'Confirm Password',
    signUp: 'Sign Up',
    hasAccount: 'Already have an account?',
    login: 'Log In',
    emailError: 'Invalid email format',
    passError: 'Password must be at least 6 characters',
    matchError: 'Passwords do not match',
  },
};

export default function SignupScreen() {
  const router = useRouter();
  const { redirect } = useLocalSearchParams<{ redirect?: string }>();
  const { language, colors, signup: doSignup } = useAppStore();
  const t = TR[language] || TR.en;
  const c = colors;

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPass, setConfirmPass] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const validateEmail = (e: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.trim());

  const handleSignup = async () => {
    setError('');
    const trimmedEmail = email.trim().toLowerCase();
    if (!validateEmail(trimmedEmail)) { setError(t.emailError); return; }
    if (password.length < 6) { setError(t.passError); return; }
    if (password !== confirmPass) { setError(t.matchError); return; }

    setLoading(true);
    try {
      await doSignup(trimmedEmail, password);
      if (redirect === 'paywall') {
        router.replace('/paywall');
      } else {
        router.replace('/');
      }
    } catch (e: any) {
      setError(e.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1 }}>
        <ScrollView contentContainerStyle={st.scroll} keyboardShouldPersistTaps="handled">
          {/* Back */}
          <TouchableOpacity testID="signup-back-btn" style={[st.backBtn, { backgroundColor: c.card }]} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={22} color={c.text} />
          </TouchableOpacity>

          {/* Header */}
          <View style={st.headerSection}>
            <View style={[st.iconBg, { backgroundColor: c.accentBg }]}>
              <Ionicons name="person-add" size={32} color={c.accent} />
            </View>
            <Text style={[st.title, { color: c.text }]}>{t.title}</Text>
            <Text style={[st.subtitle, { color: c.textSecondary }]}>{t.subtitle}</Text>
          </View>

          {/* Form */}
          <View style={st.form}>
            {/* Email */}
            <View style={[st.inputWrap, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
              <Ionicons name="mail-outline" size={18} color={c.textMuted} />
              <TextInput
                testID="signup-email"
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

            {/* Password */}
            <View style={[st.inputWrap, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
              <Ionicons name="lock-closed-outline" size={18} color={c.textMuted} />
              <TextInput
                testID="signup-password"
                style={[st.input, { color: c.text }]}
                placeholder={t.password}
                placeholderTextColor={c.textMuted}
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPass}
                autoCapitalize="none"
              />
              <TouchableOpacity onPress={() => setShowPass(!showPass)} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
                <Ionicons name={showPass ? 'eye-off-outline' : 'eye-outline'} size={18} color={c.textMuted} />
              </TouchableOpacity>
            </View>

            {/* Confirm Password */}
            <View style={[st.inputWrap, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
              <Ionicons name="lock-closed-outline" size={18} color={c.textMuted} />
              <TextInput
                testID="signup-confirm"
                style={[st.input, { color: c.text }]}
                placeholder={t.confirm}
                placeholderTextColor={c.textMuted}
                value={confirmPass}
                onChangeText={setConfirmPass}
                secureTextEntry={!showPass}
                autoCapitalize="none"
              />
            </View>

            {/* Error */}
            {error ? (
              <View style={[st.errorBox, { backgroundColor: c.incorrectBg }]}>
                <Ionicons name="alert-circle" size={16} color={c.incorrect} />
                <Text style={[st.errorText, { color: c.incorrect }]}>{error}</Text>
              </View>
            ) : null}

            {/* Signup Button */}
            <TouchableOpacity testID="signup-btn" style={[st.btn, { backgroundColor: c.accent }]} onPress={handleSignup} disabled={loading} activeOpacity={0.8}>
              {loading ? <ActivityIndicator color="#0F172A" /> : (
                <>
                  <Ionicons name="person-add-outline" size={20} color="#0F172A" />
                  <Text style={st.btnText}>{t.signUp}</Text>
                </>
              )}
            </TouchableOpacity>

            {/* Login link */}
            <View style={st.bottomRow}>
              <Text style={[st.bottomText, { color: c.textSecondary }]}>{t.hasAccount} </Text>
              <TouchableOpacity testID="goto-login" onPress={() => router.back()}>
                <Text style={[st.bottomLink, { color: c.accent }]}>{t.login}</Text>
              </TouchableOpacity>
            </View>
          </View>
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
  subtitle: { fontSize: 14, textAlign: 'center' },
  form: { gap: 14 },
  inputWrap: { flexDirection: 'row', alignItems: 'center', borderRadius: 14, borderWidth: 1, paddingHorizontal: 14, height: 52, gap: 10 },
  input: { flex: 1, fontSize: 15, height: '100%' },
  errorBox: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 14, paddingVertical: 10, borderRadius: 10 },
  errorText: { fontSize: 13, flex: 1 },
  btn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 15, gap: 8, marginTop: 4 },
  btnText: { fontSize: 16, fontWeight: '700', color: '#0F172A' },
  bottomRow: { flexDirection: 'row', justifyContent: 'center', marginTop: 8 },
  bottomText: { fontSize: 14 },
  bottomLink: { fontSize: 14, fontWeight: '700' },
});
