# Thai2Drive - Product Requirements Document

## Overview
Thai2Drive is a driving theory quiz app for Norway, targeting Thai people preparing for the Norwegian driving theory test. The app supports Norwegian (main), Thai (support), and English (secondary) languages.

## Tech Stack
- **Frontend**: React Native / Expo (Expo Router for navigation)
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **TTS**: expo-speech

## Features

### Core Quiz
- **Practice Mode**: 10 random questions, choose by category
- **Exam Mode**: 45 questions, 90-minute timer, 85% pass threshold
- **5 Categories**: Traffic Signs, Road Rules, Right of Way, Speed Limits, Safety
- **45 seed questions** (9 per category) with trilingual content

### Language Support
- 3 languages: Norwegian 🇳🇴, Thai 🇹🇭, English 🇬🇧
- Language switcher on home screen
- All question content available in all 3 languages
- **Tap-to-translate**: Tap question to reveal Thai translation inline
- **Text-to-speech**: Thai audio playback via expo-speech

### Quiz Feedback
- Selected answer highlighted in amber
- Correct answer highlighted in green with checkmark
- Incorrect answer highlighted in red with X mark
- Answers locked after checking
- Trilingual explanation shown after each answer

### Progress Tracking
- Anonymous device-based tracking (no auth required)
- Total questions answered, correct answers, accuracy percentage
- Per-category statistics
- Quiz attempt history with dates, scores, modes

### Bookmarks
- Bookmark questions during quiz
- View bookmarked questions with expandable answers
- Remove bookmarks

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/categories | Get categories with counts |
| GET | /api/questions/random | Get random questions |
| GET | /api/progress/{device_id} | Get user progress |
| PUT | /api/progress/{device_id} | Update progress |
| POST | /api/quiz-attempts | Save quiz attempt |
| GET | /api/quiz-attempts/{device_id} | Get quiz history |
| POST | /api/bookmarks | Add bookmark |
| DELETE | /api/bookmarks/{device_id}/{question_id} | Remove bookmark |
| GET | /api/bookmarked-questions/{device_id} | Get bookmarked questions |
| POST | /api/seed | Seed database |

## Design
- Dark theme (#0F172A background, #1E293B cards)
- Amber (#F59E0B) brand accent
- Green (#10B981) for correct, Red (#EF4444) for incorrect
- Swiss & High-Contrast archetype
