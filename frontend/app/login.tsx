import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAppStore } from '../src/store/appStore';

const TR: Record<string, Record<string, string>> = {
  no: {
    welcome: 'Velkommen til',
    subtitle: 'Norsk f\u00f8rerpr\u00f8ve for thai-folk',
    email: 'E-post',
    password: 'Passord',
    login: 'Logg inn',
    noAccount: 'Har du ikke konto?',
    signUp: 'Registrer deg',
    forgot: 'Glemt passord?',
    emailError: 'Ugyldig e-postformat',
    passError: 'Passord m\u00e5 v\u00e6re minst 6 tegn',
  },
  th: {
    welcome: '\u0e22\u0e34\u0e19\u0e14\u0e35\u0e15\u0e49\u0e2d\u0e19\u0e23\u0e31\u0e1a\u0e2a\u0e39\u0e48',
    subtitle: '\u0e2a\u0e2d\u0e1a\u0e43\u0e1a\u0e02\u0e31\u0e1a\u0e02\u0e35\u0e48\u0e19\u0e2d\u0e23\u0e4c\u0e40\u0e27\u0e22\u0e4c\u0e2a\u0e33\u0e2b\u0e23\u0e31\u0e1a\u0e04\u0e19\u0e44\u0e17\u0e22',
    email: '\u0e2d\u0e35\u0e40\u0e21\u0e25',
    password: '\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19',
    login: '\u0e40\u0e02\u0e49\u0e32\u0e2a\u0e39\u0e48\u0e23\u0e30\u0e1a\u0e1a',
    noAccount: '\u0e22\u0e31\u0e07\u0e44\u0e21\u0e48\u0e21\u0e35\u0e1a\u0e31\u0e0d\u0e0a\u0e35?',
    signUp: '\u0e2a\u0e21\u0e31\u0e04\u0e23\u0e2a\u0e21\u0e32\u0e0a\u0e34\u0e01',
    forgot: '\u0e25\u0e37\u0e21\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19?',
    emailError: '\u0e23\u0e39\u0e1b\u0e41\u0e1a\u0e1a\u0e2d\u0e35\u0e40\u0e21\u0e25\u0e44\u0e21\u0e48\u0e16\u0e39\u0e01\u0e15\u0e49\u0e2d\u0e07',
    passError: '\u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19\u0e15\u0e49\u0e2d\u0e07\u0e21\u0e35\u0e2d\u0e22\u0e48\u0e32\u0e07\u0e19\u0e49\u0e2d\u0e22 6 \u0e15\u0e31\u0e27\u0e2d\u0e31\u0e01\u0e29\u0e23',
  },
  en: {
    welcome: 'Welcome to',
    subtitle: 'Norwegian driving test for Thai people',
    email: 'Email',
    password: 'Password',
    login: 'Log In',
    noAccount: "Don't have an account?",
    signUp: 'Sign Up',
    forgot: 'Forgot password?',
    emailError: 'Invalid email format',
    passError: 'Password must be at least 6 characters',
  },
};

export default function LoginScreen() {
  const router = useRouter();
  const { language, colors, login: doLogin } = useAppStore();
  const t = TR[language] || TR.en;
  const c = colors;

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const validateEmail = (e: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.trim());

  const handleLogin = async () => {
    setError('');
    const trimmedEmail = email.trim().toLowerCase();
    if (!validateEmail(trimmedEmail)) { setError(t.emailError); return; }
    if (password.length < 6) { setError(t.passError); return; }

    setLoading(true);
    try {
      await doLogin(trimmedEmail, password);
      router.replace('/');
    } catch (e: any) {
      setError(e.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={[st.container, { backgroundColor: c.bg }]}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1 }}>
        <ScrollView contentContainerStyle={st.scroll} keyboardShouldPersistTaps="handled">
          {/* Logo */}
          <View style={st.logoSection}>
            <Text style={st.flag}>{"🇹🇭"}</Text>
            <Text style={[st.welcome, { color: c.textSecondary }]}>{t.welcome}</Text>
            <Text style={[st.appName, { color: c.text }]}>Thai2Drive</Text>
            <Text style={[st.subtitle, { color: c.textMuted }]}>{t.subtitle}</Text>
          </View>

          {/* Form */}
          <View style={st.form}>
            {/* Email */}
            <View style={[st.inputWrap, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
              <Ionicons name="mail-outline" size={18} color={c.textMuted} />
              <TextInput
                testID="login-email"
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
                testID="login-password"
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

            {/* Forgot password */}
            <TouchableOpacity testID="forgot-pass-link" onPress={() => router.push('/forgot-password')} style={st.forgotRow}>
              <Text style={[st.forgotText, { color: c.accent }]}>{t.forgot}</Text>
            </TouchableOpacity>

            {/* Error */}
            {error ? (
              <View style={[st.errorBox, { backgroundColor: c.incorrectBg }]}>
                <Ionicons name="alert-circle" size={16} color={c.incorrect} />
                <Text style={[st.errorText, { color: c.incorrect }]}>{error}</Text>
              </View>
            ) : null}

            {/* Login Button */}
            <TouchableOpacity testID="login-btn" style={[st.btn, { backgroundColor: c.accent }]} onPress={handleLogin} disabled={loading} activeOpacity={0.8}>
              {loading ? <ActivityIndicator color="#0F172A" /> : (
                <>
                  <Ionicons name="log-in-outline" size={20} color="#0F172A" />
                  <Text style={st.btnText}>{t.login}</Text>
                </>
              )}
            </TouchableOpacity>

            {/* Sign up link */}
            <View style={st.bottomRow}>
              <Text style={[st.bottomText, { color: c.textSecondary }]}>{t.noAccount} </Text>
              <TouchableOpacity testID="goto-signup" onPress={() => router.push('/signup')}>
                <Text style={[st.bottomLink, { color: c.accent }]}>{t.signUp}</Text>
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
  scroll: { flexGrow: 1, justifyContent: 'center', padding: 24 },
  logoSection: { alignItems: 'center', marginBottom: 40 },
  flag: { fontSize: 48, marginBottom: 12 },
  welcome: { fontSize: 15, marginBottom: 4 },
  appName: { fontSize: 34, fontWeight: '800', letterSpacing: -1 },
  subtitle: { fontSize: 13, marginTop: 4, textAlign: 'center' },
  form: { gap: 14 },
  inputWrap: { flexDirection: 'row', alignItems: 'center', borderRadius: 14, borderWidth: 1, paddingHorizontal: 14, height: 52, gap: 10 },
  input: { flex: 1, fontSize: 15, height: '100%' },
  forgotRow: { alignSelf: 'flex-end', marginTop: -4 },
  forgotText: { fontSize: 13, fontWeight: '600' },
  errorBox: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 14, paddingVertical: 10, borderRadius: 10 },
  errorText: { fontSize: 13, flex: 1 },
  btn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderRadius: 14, paddingVertical: 15, gap: 8, marginTop: 4 },
  btnText: { fontSize: 16, fontWeight: '700', color: '#0F172A' },
  bottomRow: { flexDirection: 'row', justifyContent: 'center', marginTop: 8 },
  bottomText: { fontSize: 14 },
  bottomLink: { fontSize: 14, fontWeight: '700' },
});
