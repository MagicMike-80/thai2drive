# Changelog

All notable changes to Thai2Drive are documented in this file.

## [0.2.5.2] - 2026-10-08

### Security

- Require valid account authentication for statistics and attempt-history reads; reject mismatched account IDs and filter only by authenticated ownership.
- Preserve anonymous quiz submission and local results. Anonymous server-history readers, including older mobile calls without tokens, are now denied.

## [0.2.5.1] - 2026-10-08

### Fixed

- Remove the remaining attempt-completion call from the language selector. Result language changes now render without saving again.
- Ignore trailing Next/answer activations until a 450 ms quiet interval after advancing a question.
- Move focus from a completed, focused practice answer to the visible Next button, without overriding focus moved elsewhere.
- Exercise the real setLang entry point and transition/focus behavior in runtime regressions. No historical data cleanup.

## [0.2.5.0] - 2026-10-08

### Fixed

- Result summaries and exam review cards refresh when the UI language changes, without saving another attempt or changing scores.
- Translated answers retain their original option identity after shuffling; missing translations fail closed. Question coaching uses the selected language.
- Add NO/TH/EN result, action, immutable-history and shuffled-answer regressions. Mobile, quotas, payment and campaign logic remain unchanged.

## [0.2.4.0] - 2026-10-07

### Fixed

- Ordinary Michael conversations preserve explanations instead of reducing replies to a final question or restarting the guided onboarding flow.
- Guided quiz and document practice retain their staged teaching flow; ordinary chat can acknowledge missing student results without inventing readiness evidence.
- Add isolated reply-preservation regressions across Norwegian, Thai and English. Mobile, payments, quotas and legacy campaign containment are unchanged.

## [0.2.3.0] - 2026-10-07

### Fixed

- Result buttons retain their own translated labels after language updates, including the guest account action, Michael, Home and categories.
- Regressions exercise the full language updater and result handlers across Norwegian, Thai, English and back to Norwegian. Legacy campaign containment remains unchanged.

## [0.2.2.0] - 2026-10-07

### Security

- Retire anonymous campaign grants with a permanent no-write HTTP 410 response.
- Remove the legacy campaign enrollment UI and mark its historical status inactive.
- Preserve normal signup, existing entitlements and all historical data; document the remaining signup campaign and safe recovery baseline.
- Add an aggregate-only, read-only historical campaign inspection script.

## [0.2.1.0] - 2026-10-07

### Fixed

- Guests see their answered-question result before choosing a free account, and signup/login carry their guest identity into the existing history migration.
- History and answer review use the selected language and hide legacy text whose language cannot be established.
- Quiz keyboard shortcuts respect focused controls and wait for the answer response before advancing.
- Public pricing links lead to a price section backed by the current pricing endpoint; the unsupported savings badge is removed.
- Support chat labels render correctly on legacy pages and no longer borrow Norwegian text for other languages.

## [0.2.0.3] - 2026-09-23

### Fixed

- Weak and strong topic guidance also returns its answer when chat history storage is full.

## [0.2.0.2] - 2026-09-23

### Fixed

- Michael returns completed chat replies even when conversation history cannot be written to MongoDB.

## [0.2.0.1] - 2026-09-23

### Changed

- Michael now uses a calm, single-field chat composer with image/document upload, voice input and a circular send action.
- Permanent suggestion buttons are removed from the conversation; five localized learning paths are available in an optional neon sidebar.

## [0.2.0.0] - 2026-09-16

### Added

- Learners can open a wide stopping-distance page from the web home screen, with red and silver Tesla illustrations.
- Speed and road-condition controls show reaction, braking and total distance, four calculation steps, and 2/3-second following distances in Norwegian, Thai and English.
- A short stopping animation respects reduced-motion settings; local offline preview and regression tests cover the new screen.

## [0.1.0.0] - 2026-09-09

### Added

- Learners can open 25 indexed right-of-way and stopping-distance video lessons with localized Norwegian, Thai, and English titles.
- Lesson videos and thumbnails are served from stable static URLs with browser-compatible byte-range streaming.
- Signed-out learners can enter Michael directly as guests from the localized web interface.

### Fixed

- Static media routes reject traversal attempts and unsupported file types.
