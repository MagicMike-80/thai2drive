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
- User account based tracking (email/password auth)
- Total questions answered, correct answers, accuracy percentage
- Per-category statistics
- Quiz attempt history with dates, scores, modes

### Authentication
- **Sign Up**: Email + password with validation (email format, min 6 char password)
- **Login**: Email + password with proper error handling (wrong password, user not found)
- **Password Reset**: Forgot password flow via email (MOCKED email, code-based reset)
- **JWT Tokens**: 7-day session persistence with auto-restore
- **Admin Whitelist**: Admins bypass paywall, auto-premium access
- User email stored for admin check and premium status

### Bookmarks
- Bookmark questions during quiz
- View bookmarked questions with expandable answers
- Remove bookmarks

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/signup | Register new user |
| POST | /api/auth/login | Login with email/password |
| GET | /api/auth/me | Get current user (JWT) |
| POST | /api/auth/forgot-password | Request password reset |
| POST | /api/auth/reset-password | Reset password with code |
| POST | /api/admin/check | Check admin whitelist |
| POST | /api/admin/add | Add email to admin whitelist |
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
