/**
 * ExplanationCard — AI-powered deep explanation shown after a quiz answer.
 *
 * Usage:
 *   <ExplanationCard
 *     questionId="..."
 *     correctOptionId="B"
 *     options={question.options}
 *     lang="no"
 *     colors={c}
 *   />
 *
 * The user taps "Get AI Explanation" → we fetch, show structured blocks.
 * Falls back gracefully when AI is unavailable.
 */
import React, { useState, useCallback } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet,
  ActivityIndicator, LayoutAnimation, Platform, UIManager,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { aiLearningApi, AIExplanation } from '../services/aiLearning';
import type { ThemeColors } from '../theme';
import type { QuestionOption } from '../services/api';

// Enable LayoutAnimation on Android
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

// ─── Translations ─────────────────────────────────────────────────────────────
const TR: Record<string, Record<string, string>> = {
  no: {
    getExplanation: 'AI-forklaring',
    loading:        'Genererer forklaring…',
    whyCorrect:     'Hvorfor riktig',
    whyWrong:       'Hvorfor feil',
    importantRule:  'Viktig trafikkregl',
    realSituation:  'I trafikken',
    commonMistake:  'Vanlig feil',
    examTip:        'Eksamenstips',
    memoryRule:     'Huskeregel',
    formula:        'Beregning',
    noExplanation:  'AI-forklaring ikke tilgjengelig akkurat nå.',
    wrongOption:    'Alternativ',
  },
  th: {
    getExplanation: 'คำอธิบาย AI',
    loading:        'กำลังสร้างคำอธิบาย…',
    whyCorrect:     'ทำไมถึงถูก',
    whyWrong:       'ทำไมถึงผิด',
    importantRule:  'กฎจราจรสำคัญ',
    realSituation:  'สถานการณ์จริง',
    commonMistake:  'ข้อผิดพลาดที่พบบ่อย',
    examTip:        'เคล็ดลับสอบ',
    memoryRule:     'วิธีจำ',
    formula:        'การคำนวณ',
    noExplanation:  'ยังไม่มีคำอธิบาย AI ในขณะนี้',
    wrongOption:    'ตัวเลือก',
  },
  en: {
    getExplanation: 'AI Explanation',
    loading:        'Generating explanation…',
    whyCorrect:     'Why correct',
    whyWrong:       'Why others are wrong',
    importantRule:  'Important rule',
    realSituation:  'In traffic',
    commonMistake:  'Common mistake',
    examTip:        'Exam tip',
    memoryRule:     'Memory trick',
    formula:        'Calculation',
    noExplanation:  'AI explanation not available right now.',
    wrongOption:    'Option',
  },
};

// ─── Block definitions ────────────────────────────────────────────────────────
type BlockKey =
  | 'whyCorrect' | 'importantRule' | 'realSituation'
  | 'commonMistake' | 'examTip' | 'memoryRule' | 'formula';

const BLOCKS: {
  key: BlockKey;
  icon: keyof typeof Ionicons.glyphMap;
  accentColor: string;
}[] = [
  { key: 'whyCorrect',     icon: 'checkmark-circle',       accentColor: '#10B981' },
  { key: 'importantRule',  icon: 'document-text-outline',  accentColor: '#3B82F6' },
  { key: 'realSituation',  icon: 'car-outline',            accentColor: '#F59E0B' },
  { key: 'commonMistake',  icon: 'alert-circle-outline',   accentColor: '#EF4444' },
  { key: 'examTip',        icon: 'school-outline',         accentColor: '#8B5CF6' },
  { key: 'memoryRule',     icon: 'bulb-outline',           accentColor: '#EC4899' },
  { key: 'formula',        icon: 'calculator-outline',     accentColor: '#06B6D4' },
];

// ─── Props ────────────────────────────────────────────────────────────────────
interface ExplanationCardProps {
  questionId:     string;
  correctOptionId: string;
  options:        QuestionOption[];
  lang:           string;
  colors:         ThemeColors;
}

// ─── Component ────────────────────────────────────────────────────────────────
export function ExplanationCard({
  questionId,
  correctOptionId,
  options,
  lang,
  colors: c,
}: ExplanationCardProps) {
  const t = TR[lang] || TR.en;

  const [state, setState] = useState<'idle' | 'loading' | 'loaded' | 'error'>('idle');
  const [data, setData] = useState<AIExplanation | null>(null);
  const [expandedBlocks, setExpandedBlocks] = useState<Set<string>>(new Set(['whyCorrect']));

  const load = useCallback(async () => {
    if (state === 'loading' || state === 'loaded') return;
    setState('loading');
    try {
      const resp = await aiLearningApi.getExplanation(questionId, lang);
      if (resp && !resp.is_fallback) {
        LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
        setData(resp.explanation);
        setState('loaded');
      } else {
        setState('error');
      }
    } catch {
      setState('error');
    }
  }, [questionId, lang, state]);

  const toggleBlock = (key: string) => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpandedBlocks((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  // Resolve text for a block key
  const getBlockText = (key: BlockKey): string | null => {
    if (!data) return null;
    switch (key) {
      case 'whyCorrect':    return data.why_correct || null;
      case 'importantRule': return data.important_rule || null;
      case 'realSituation': return data.real_traffic_situation || null;
      case 'commonMistake': return data.common_mistake || null;
      case 'examTip':       return data.exam_tip || null;
      case 'memoryRule':    return data.memory_rule || null;
      case 'formula':       return data.is_math ? (data.formula_explanation || null) : null;
      default:              return null;
    }
  };

  const wrongOptions = options.filter((o) => o.id !== correctOptionId);

  // ── Idle state: show trigger button ──────────────────────────────────────────
  if (state === 'idle') {
    return (
      <TouchableOpacity
        style={[styles.triggerBtn, { borderColor: `${c.accent}60`, backgroundColor: c.accentBg }]}
        onPress={load}
        activeOpacity={0.75}
      >
        <Ionicons name="sparkles" size={16} color={c.accent} />
        <Text style={[styles.triggerTxt, { color: c.accent }]}>{t.getExplanation}</Text>
        <Ionicons name="chevron-forward" size={14} color={`${c.accent}90`} />
      </TouchableOpacity>
    );
  }

  // ── Loading ───────────────────────────────────────────────────────────────────
  if (state === 'loading') {
    return (
      <View style={[styles.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
        <View style={styles.loadingRow}>
          <ActivityIndicator size="small" color={c.accent} />
          <Text style={[styles.loadingTxt, { color: c.textSecondary }]}>{t.loading}</Text>
        </View>
      </View>
    );
  }

  // ── Error ─────────────────────────────────────────────────────────────────────
  if (state === 'error') {
    return (
      <View style={[styles.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
        <Text style={[styles.errorTxt, { color: c.textMuted }]}>{t.noExplanation}</Text>
      </View>
    );
  }

  // ── Loaded: show explanation blocks ───────────────────────────────────────────
  return (
    <View style={[styles.card, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
      {/* Header */}
      <View style={styles.cardHeader}>
        <Ionicons name="sparkles" size={15} color={c.accent} />
        <Text style={[styles.cardHeaderTxt, { color: c.accent }]}>{t.getExplanation}</Text>
      </View>

      {/* Main explanation blocks */}
      {BLOCKS.map(({ key, icon, accentColor }) => {
        const text = getBlockText(key);
        if (!text) return null;
        const expanded = expandedBlocks.has(key);
        return (
          <TouchableOpacity
            key={key}
            style={[styles.block, { borderLeftColor: accentColor }]}
            onPress={() => toggleBlock(key)}
            activeOpacity={0.7}
          >
            <View style={styles.blockHeader}>
              <Ionicons name={icon} size={15} color={accentColor} />
              <Text style={[styles.blockTitle, { color: c.text }]}>{t[key]}</Text>
              <Ionicons
                name={expanded ? 'chevron-up' : 'chevron-down'}
                size={14}
                color={c.textMuted}
              />
            </View>
            {expanded && (
              <Text style={[styles.blockText, { color: c.textSecondary }]}>{text}</Text>
            )}
          </TouchableOpacity>
        );
      })}

      {/* Why wrong — each wrong option */}
      {data && Object.keys(data.why_wrong || {}).length > 0 && (
        <TouchableOpacity
          style={[styles.block, { borderLeftColor: '#EF4444' }]}
          onPress={() => toggleBlock('whyWrong')}
          activeOpacity={0.7}
        >
          <View style={styles.blockHeader}>
            <Ionicons name="close-circle-outline" size={15} color="#EF4444" />
            <Text style={[styles.blockTitle, { color: c.text }]}>{t.whyWrong}</Text>
            <Ionicons
              name={expandedBlocks.has('whyWrong') ? 'chevron-up' : 'chevron-down'}
              size={14}
              color={c.textMuted}
            />
          </View>
          {expandedBlocks.has('whyWrong') && wrongOptions.map((opt) => {
            const reason = data.why_wrong[opt.id];
            if (!reason) return null;
            return (
              <View key={opt.id} style={styles.wrongRow}>
                <View style={[styles.wrongBadge, { backgroundColor: `${c.incorrect}22` }]}>
                  <Text style={[styles.wrongBadgeTxt, { color: c.incorrect }]}>{opt.id}</Text>
                </View>
                <Text style={[styles.wrongText, { color: c.textSecondary }]}>{reason}</Text>
              </View>
            );
          })}
        </TouchableOpacity>
      )}
    </View>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────
const styles = StyleSheet.create({
  triggerBtn: {
    flexDirection:   'row',
    alignItems:      'center',
    gap:             6,
    marginTop:       12,
    borderRadius:    10,
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderWidth:     1,
  },
  triggerTxt: {
    flex:       1,
    fontSize:   13,
    fontWeight: '700',
    letterSpacing: 0.2,
  },
  card: {
    marginTop:    12,
    borderRadius: 14,
    borderWidth:  1,
    overflow:     'hidden',
  },
  loadingRow: {
    flexDirection: 'row',
    alignItems:    'center',
    gap:           10,
    padding:       16,
  },
  loadingTxt: {
    fontSize: 13,
  },
  errorTxt: {
    fontSize: 13,
    padding:  16,
    textAlign: 'center',
  },
  cardHeader: {
    flexDirection:  'row',
    alignItems:     'center',
    gap:            6,
    paddingHorizontal: 14,
    paddingTop:     12,
    paddingBottom:  8,
  },
  cardHeaderTxt: {
    fontSize:   12,
    fontWeight: '800',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
  },
  block: {
    borderLeftWidth: 3,
    marginHorizontal: 10,
    marginBottom:    8,
    borderRadius:    8,
    paddingLeft:     10,
    paddingRight:    10,
    paddingVertical: 8,
    backgroundColor: 'transparent',
  },
  blockHeader: {
    flexDirection: 'row',
    alignItems:    'center',
    gap:           7,
  },
  blockTitle: {
    flex:       1,
    fontSize:   13,
    fontWeight: '700',
  },
  blockText: {
    marginTop:  6,
    fontSize:   13,
    lineHeight: 19,
  },
  wrongRow: {
    flexDirection: 'row',
    alignItems:    'flex-start',
    gap:           8,
    marginTop:     6,
  },
  wrongBadge: {
    width:         24,
    height:        24,
    borderRadius:  7,
    alignItems:    'center',
    justifyContent:'center',
    marginTop:     1,
    flexShrink:    0,
  },
  wrongBadgeTxt: {
    fontSize:   12,
    fontWeight: '700',
  },
  wrongText: {
    flex:       1,
    fontSize:   13,
    lineHeight: 19,
  },
});
