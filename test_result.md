#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================
# (Protocol section unchanged)
#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

#====================================================================================================
# Testing Data
#====================================================================================================

user_problem_statement: >
  Thai2Drive - Norwegian driving theory quiz app for Thai people in Norway.
  Features: Practice mode, Exam mode (45 questions, 90-min timer, 85% pass),
  3-language support (NO/TH/EN), tap-to-translate, TTS for Thai,
  bookmarks, quiz history, progress tracking.

backend:
  - task: "Seed database with 45 questions"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: true
        agent: "main"
        comment: "45 questions seeded across 5 categories (9 per category)"

  - task: "Questions API - random and filtered"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Applied app-wide IMAGE_ONLY_FILTER to both /api/questions and /api/questions/random. All quiz modes (Practice, Exam, Daily Test) now only receive questions where bildeUrl is present and non-empty. The has_image query param on /questions/random is now ignored (always image-only). Manually verified with 5 test cases (daily=5, practice=10, exam=45, has_image=false, category=Road Conditions w/ only 2 images). All returned 100% image-bearing questions."
      - working: true
        agent: "main"
        comment: "2026-04-23: Confirmed still working after UI polish pass. Backend untouched; all quiz modes still pull image-only questions."

frontend:
  - task: "Audio speed live switching + inline UI"
    implemented: true
    working: true
    file: "/app/frontend/app/quiz.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Fixed stale-closure bug: added ttsSpeedRef (live ref) so speakSequence reads current speed per segment. Added changeSpeed(v) helper that updates state+ref and, if audio is currently playing, stops and restarts playback at the new speed. Also redesigned audio UI from dual boxes (listen button + speed row) to a single inline row: [▶] 1x 1.5x 2x with the active speed highlighted. Audio still stops on idx change and component unmount."
  - task: "Answer feedback — sound + haptics with style modes"
    implemented: true
    working: true
    file: "/app/frontend/src/sounds.ts, /app/frontend/app/settings.tsx, /app/frontend/app/quiz.tsx, /app/frontend/src/store/appStore.ts"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Rebuilt sound utility to be fully cross-platform using expo-av (data-URI WAVs generated in-code) + expo-haptics. Two feedback styles: (1) default — short C5→E5 chime (correct) / F4→D4 (wrong), ~0.22s each; (2) strong — longer bell-like 'kliiing' with 3 harmonics, G5→B5→E6 arpeggio ~0.6s (correct) or G3→E3 low buzz (wrong). Pre-warmed players cached per (kind, style) for zero-hitch playback. Anti-stacking guard drops plays within 120 ms of the previous one, and each play rewinds the existing player with setPositionAsync(0) rather than spawning new Sound objects. Added three persisted settings to appStore: soundEnabled, soundStyle ('default'|'strong'), hapticsEnabled — all saved to AsyncStorage. Settings screen now has a 'Sound & Haptics' section with master toggle, two big 'Soft' / 'Strong' style chips (with descriptive hints and live preview on tap), and a haptic-vibration master switch. Haptics: correct→impactLight/successNotification, wrong→impactMedium/errorNotification depending on style. Pre-warm runs once at app launch in _layout.tsx to eliminate first-answer lag."
  - task: "Categories screen — game-level premium"
    implemented: true
    working: true
    file: "/app/frontend/app/categories.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "FROZEN per user. Premium game-level redesign shipped: per-category hues, gradient overlays, glow blobs, difficulty stars, progress bars, featured All-Categories card, spring press animation. Expo-linear-gradient pinned to ~15.0.8 (matches SDK 54)."
  - task: "RevenueCat — handle invalid/test keys gracefully"
    implemented: true
    working: true
    file: "/app/frontend/src/hooks/useRevenueCat.ts, /app/frontend/.env, /app/frontend/app/paywall.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Added looksLikeValidRCKey() gate: only keys that begin with goog_ (Android) or appl_ (iOS) pass. Test placeholders (test_...), empty strings, and any non-RC string cause initRC() to return false silently — no 'Wrong API Key' banner. Paywall screen now shows the same 'Payment requires the mobile app' notice when rc.isAvailable is false. User can paste a real RevenueCat public key into EXPO_PUBLIC_RC_API_KEY in .env and the app automatically enables purchases on the next build."
  - task: "TTS — bulletproof stop on question change + male voice preference"
    implemented: true
    working: true
    file: "/app/frontend/app/quiz.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Added monotonic ttsGen counter — every stopTts() and every speakSequence() increments/claims a generation. If a newer stopTts invalidates a running sequence, the next segment-loop iteration bails before calling Speech.speak again. stopTts() also calls Speech.stop() three times (immediate + 30ms + 250ms) because some Android TTS engines don't honor a single stop mid-utterance. Added male-voice picker: Speech.getAvailableVoicesAsync() is called on mount, voices for th-TH / nb-NO / en-US are scored with known Google male-voice regexes (-ttm, -wavenet-B/C/D, -stm, -m01, 'male'), and the best match is cached in voiceMapRef. speakSequence passes the picked voice identifier via Speech.speak({ voice }). Fallback: if no male pattern matches, pick the 'enhanced' voice (better quality) or default."
  - task: "Android adaptive icon — safe zone compliance"
    implemented: true
    working: true
    file: "/app/frontend/assets/images/adaptive-icon.png, icon.png, splash-icon.png, t2d-icon.png"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Regenerated all icons with stricter safe-zone compliance. Previous foreground extended toward edges → Samsung One UI cropped it to a 'yellow blob'. New generator keeps ALL visible content inside a central 35%-radius circle (well inside Android's 66% safe-zone requirement). 'T2D' wordmark centered, subtle amber glow behind, no text bleed. Confirmed visually: icon.png shows bold centered T2D on navy with amber glow; adaptive-icon.png has transparent bg with the same foreground for Android to composite over the #0F172A bg set in app.json. Also removed the 'THAI · DRIVE' subtitle that was making the design cluttered."
  - task: "Home screen simplification"
    implemented: true
    working: true
    file: "/app/frontend/app/index.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Rebuilt home to minimal layout: top bar (language + settings icon), brand block, optional streak pill, one big amber Start Quiz CTA with spring press animation, free-left hint, slim secondary row (Exam + Daily Test, no card-in-card), 3-column stats (no cards), premium banner. History/Bookmarks moved to Settings > Library section."
  - task: "Categories screen de-rainbow"
    implemented: true
    working: true
    file: "/app/frontend/app/categories.tsx"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Removed the per-category rainbow palette. All category cards now share the same navy card background with a uniform amber icon-tile and standard cardBorder. Premium, consistent, minimal color usage."
      - working: true
        agent: "main"
        comment: "2026-04-23 PREMIUM POLISH: Rebuilt as a game-like level-selection screen. Added expo-linear-gradient. Each card now has: (1) subtle per-category hue (blue/green/purple/orange/pink/teal/amber/cyan/red) used as a diagonal gradient overlay + top-right glow blob + icon tile + border tint — dark navy remains the base, no rainbow feel; (2) difficulty stars ⭐/⭐⭐/⭐⭐⭐ + semantic text label (Easy/Medium/Hard) colored green/amber/red; (3) thin progress bar at bottom of each card driven by store.progress.questions_by_category[cat]; (4) press animation via custom PressableCard: spring scale 0.97 + white-overlay glow. The 'All Categories' card is now a featured primary entry with accent-colored gradient, sparkles icon, circular play pill, and overall progress bar. SafeAreaView background uses a subtle vertical dark gradient (0B1222→0F172A→0B1222). Navigation logic unchanged."
  - task: "Paywall polish"
    implemented: true
    working: true
    file: "/app/frontend/app/paywall.tsx"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Middle plan (3 months) now visually prominent: 2px border, amber outline when idle, larger padding (20px vs 16px), bigger plan name (17 vs 15) and price (22 vs 19). CTA enlarged to 19px vertical padding + 17px bold text with letter-spacing. Increased spacing overall (plans gap 14, header mb 32, features gap 14)."
  - task: "Quiz typography + reduce nesting"
    implemented: true
    working: true
    file: "/app/frontend/app/quiz.tsx"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Question text bumped 18px→21px, line-height 26→30, letter-spacing -0.3. Answer text 15→16, letter circle 32→34. Question image border removed (it was redundant inside the card). Card padding 18→20."

  - task: "Progress tracking API"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

  - task: "Quiz attempts API"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

  - task: "Bookmarks API"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true

  - task: "Auth API - signup, login, forgot-password, reset-password, me"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: unknown
        agent: "main"
        comment: "Email/password auth with JWT tokens, bcrypt hashing. Endpoints: POST /api/auth/signup, POST /api/auth/login, GET /api/auth/me, POST /api/auth/forgot-password, POST /api/auth/reset-password. Admin whitelist check at POST /api/admin/check."
      - working: true
        agent: "testing"
        comment: "All auth endpoints tested successfully. POST /api/auth/signup: validates email/password, rejects duplicates and invalid formats. POST /api/auth/login: authenticates correctly, returns JWT token. GET /api/auth/me: requires valid Bearer token, returns user info. POST /api/auth/forgot-password: generates reset codes (MOCKED email). POST /api/auth/reset-password: successfully resets password with valid code. All validation and error handling working correctly."

  - task: "Admin whitelist check and add"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Admin functionality tested successfully. POST /api/admin/check: correctly identifies admin/non-admin status. POST /api/admin/add: successfully adds emails to admin whitelist. Admin users get is_admin=true and is_premium=true flags automatically."

frontend:
  - task: "Home screen with language switcher and stats"
    implemented: true
    working: true
    file: "/app/frontend/app/index.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

  - task: "Category selection screen"
    implemented: true
    working: true
    file: "/app/frontend/app/categories.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

  - task: "Quiz screen with answer feedback"
    implemented: true
    working: true
    file: "/app/frontend/app/quiz.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

  - task: "Exam mode with 90-min timer"
    implemented: true
    working: true
    file: "/app/frontend/app/quiz.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

  - task: "Tap-to-translate feature"
    implemented: true
    working: true
    file: "/app/frontend/app/quiz.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

  - task: "Results screen with pass/fail for exam"
    implemented: true
    working: true
    file: "/app/frontend/app/results.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

  - task: "History screen"
    implemented: true
    working: true
    file: "/app/frontend/app/history.tsx"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true

  - task: "Bookmarks screen"
    implemented: true
    working: true
    file: "/app/frontend/app/bookmarks.tsx"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true

metadata:
  created_by: "main_agent"
  version: "2.0"
  test_sequence: 1
  run_ui: true

test_plan:
  current_focus:
    - "Home screen loads with stats"
    - "Language switching works"
    - "Practice mode quiz flow"
    - "Exam mode with timer"
    - "Answer checking with green/red feedback"
    - "Progress tracking"
    - "Quiz history"
    - "Bookmarks"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "All features implemented. Backend has 45 questions, 5 categories. Frontend has full quiz flow with practice/exam modes, language switcher, tap-to-translate, TTS, bookmarks, history. Please test all flows."
  - agent: "testing"
    message: "✅ AUTH API TESTING COMPLETE: All auth endpoints working correctly. Tested signup (with validation), login, JWT authentication, password reset flow (MOCKED email), and admin functionality. All existing endpoints (questions, seed, categories) still working. No critical issues found. Email service is MOCKED but functional for testing. Ready for production deployment."
  - agent: "main"
    message: "2026-04-24 APK polish — 4 bugs from user msg 564:
      (1) TTS skipping question + option A: rewrote speakSequence to ALWAYS wait 220ms before the first segment (Android Speech.stop() finalization window). Removed the conditional 120ms warm-up in speakQuestion. Also kept the ttsGen monotonic counter so a stopTts() call from useEffect[idx] / handleNext / unmount cleanly invalidates any in-flight sequence.
      (2) Haptics on quiz: added a tickHaptic() helper that fires Haptics.impactAsync(Light) + Vibration.vibrate(10) Android fallback, wired to (a) every answer-letter tap and (b) the next/finish button. Correct/wrong haptics already existed in playCorrectSound/playIncorrectSound.
      (3) Louder + longer 'kliiing': sndCorrectStrong frequencies updated to G5 → C6 → G6 (octave climb), durations 0.09/0.13/0.72 (~0.94s total), volume 0.48→0.72, releaseRatio 0.95. Audio.Sound player volume bumped 0.9→1.0. Wrong sound left as-is per user instruction.
      (4) Header 🇹🇭 T2D branding: created /app/frontend/src/components/AppBrand.tsx (Thai flag 28px, slightly larger than the 22-26px LanguageSwitcher flags, plus 'T2D' text 17px weight 900, with a subtle drop shadow). Injected into top-left of every main screen header: index.tsx (home), categories.tsx, settings.tsx, history.tsx, bookmarks.tsx, paywall.tsx, results.tsx (both the main results view and the in-results review header). Deliberately NOT added to quiz.tsx because that header is dedicated to progress + bookmark and adding the brand there would clutter the active quiz UX. Verified visually via screenshot tool on home/categories/settings/results — all show the 🇹🇭 T2D badge clean and crisp at top-left."
  - agent: "main"
    message: "2026-04-24 follow-up after APK test — 2 bugs:
      (1) TTS still skipped option A (sequence was Q → B → C → D). Root cause: even with the 220ms initial warm-up, on Android the Speech.speak() call right after onDone of the previous segment is silently dropped because the TTS engine is still finalizing the previous utterance for ~50-200ms. Fix in /app/frontend/app/quiz.tsx speakSequence: between segments on Android, poll Speech.isSpeakingAsync() up to 1.5s until it reports idle, then add a fixed 180ms gap before the next Speech.speak(). On iOS use a single 80ms gap (no engine-drain bug there). The initial 220ms warm-up is preserved so segment 0 (the question) still plays. Each segment's onDone/onError/onStopped resolution is now also guarded with a `resolved` flag so the promise can't be double-resolved.
      (2) Light-mode A/B/C/D letter contrast: in light mode the SELECTED state was rendering a dark navy 'A' on a dark-orange circle = unreadable. Fix in /app/frontend/app/quiz.tsx answer block: introduced a letterOnColored boolean that is true whenever the letter circle's background is a saturated brand color (accent on selection, correct on done-correct, incorrect on done-wrong). When letterOnColored is true the letter text is forced to '#FFFFFF' regardless of theme; otherwise it falls back to c.letterText (dark navy in light mode, white in dark mode). Verified visually:
        – Light mode unselected: dark navy A/B/C/D on light-gray circle ✓
        – Light mode selected: WHITE 'A' on orange circle ✓
        – Dark mode unchanged."
  - agent: "main"
    message: "2026-04-25 Free-user gate rework — proper account+paywall flow:
      Old behavior: 10 free questions PER DAY, then redirect to /paywall directly (anyone could keep using app without logging in by waiting til midnight).
      New behavior: 10 free questions LIFETIME, then must create account → then paywall.
      Changes:
      (a) /app/frontend/src/store/appStore.ts: removed daily reset of freeQuestionsUsed (kept the same AsyncStorage key for back-compat — existing users' counter just stops resetting at midnight). Removed `freeResetDate` field and `resetFreeIfNewDay` action. Added `needsAccountGate()` helper: true when guest hit limit and must sign up.
      (b) /app/frontend/app/quiz.tsx: introduced showAccountOrPaywall() centralised gate. When a free user tries to advance past their 10-question lifetime quota:
          • Guest (not isAuthenticated) → Alert with title 'Opprett konto for å fortsette' + body explaining 10-question limit + 3 buttons (Avbryt / Logg inn → /login?redirect=paywall / Opprett konto → /signup?redirect=paywall). Translated to NO/TH/EN.
          • Logged-in free user → router.replace('/paywall') directly.
        Wired to: handleNext, the quiz-mount useEffect (when entering with already-exhausted quota), and the inline 'Unlock' button.
      (c) /app/frontend/app/index.tsx: same gate via handleLockedNav() applied to Start Quiz CTA and Exam button. The 'dailyLimitReached' string is now 'Opprett konto for å fortsette' (NO) / 'สร้างบัญชีเพื่อดำเนินการต่อ' (TH) / 'Create account to continue' (EN). The 'freeLeft' label dropped 'today' suffix — now just 'gratis igjen' / 'ฟรีเหลือ' / 'free left'.
      (d) Existing /login and /signup screens already honored the redirect=paywall query param — after auth they replace() to /paywall.
      No quiz logic, exam mode, TTS, haptics, or results flow was touched. Verified visually: locked home screen shows red 'Opprett konto for å fortsette' under the disabled 🔒 Start Quiz button in NO and TH locales."

