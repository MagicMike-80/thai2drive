# Changelog

All notable changes to Thai2Drive are documented in this file.

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
