import { useEffect, useState } from 'react';
import { Platform, Alert } from 'react-native';
import * as ScreenCapture from 'expo-screen-capture';

const WARNING_MESSAGES: Record<string, { title: string; message: string }> = {
  no: {
    title: 'Skjermbilde oppdaget',
    message: 'Deling av sporsmal er ikke tillatt for a beskytte innholdet vart.',
  },
  th: {
    title: 'ตรวจพบการจับภาพหน้าจอ',
    message: 'ไม่อนุญาตให้แชร์คำถามเพื่อปกป้องเนื้อหาของเรา',
  },
  en: {
    title: 'Screenshot Detected',
    message: 'Sharing questions is not allowed to protect our content.',
  },
};

/**
 * Hook to protect screen content from screenshots and screen recording.
 *
 * Android: Blocks screenshots and screen recording entirely (FLAG_SECURE)
 * iOS: Detects screenshots and shows a warning alert
 *
 * @param language - Current app language for localized warning messages
 * @returns screenshotDetected - Whether a screenshot was recently detected (iOS)
 */
export function useScreenProtection(language: string = 'en') {
  const [screenshotDetected, setScreenshotDetected] = useState(false);

  useEffect(() => {
    let subscription: ScreenCapture.Subscription | null = null;

    const activate = async () => {
      try {
        // Android: Block screenshots entirely with FLAG_SECURE
        // iOS: This also helps but isn't 100% effective
        await ScreenCapture.preventScreenCaptureAsync('quiz-protection');

        // iOS: Add screenshot detection listener
        if (Platform.OS === 'ios' || Platform.OS === 'web') {
          subscription = ScreenCapture.addScreenshotListener(() => {
            setScreenshotDetected(true);
            const msg = WARNING_MESSAGES[language] || WARNING_MESSAGES.en;
            Alert.alert(msg.title, msg.message);

            // Reset after 3 seconds
            setTimeout(() => setScreenshotDetected(false), 3000);
          });
        }
      } catch (e) {
        console.log('Screen capture protection not available:', e);
      }
    };

    activate();

    return () => {
      // Re-allow screen capture when leaving the protected screen
      ScreenCapture.allowScreenCaptureAsync('quiz-protection').catch(() => {});
      if (subscription) {
        subscription.remove();
      }
    };
  }, [language]);

  return { screenshotDetected };
}
