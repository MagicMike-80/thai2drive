# Thai2Drive — App Icons

Production-ready app icons for iOS and Android, generated from AI-designed master.

## Files

### Master
- `master_1024.png` (1024×1024) — Source for all downscaled sizes.

### iOS (`ios/`)
| Size | File | Purpose |
|------|------|---------|
| 1024×1024 | `icon-1024.png` | App Store listing |
| 180×180 | `icon-180.png` | iPhone @3x |
| 120×120 | `icon-120.png` | iPhone @2x / Spotlight |
| 87×87 | `icon-87.png` | iPhone Settings @3x |
| 60×60 | `icon-60.png` | iPhone legacy |

### Android (`android/`)
| Size | File | Purpose |
|------|------|---------|
| 512×512 | `icon-512.png` | Play Store listing |
| 192×192 | `icon-192.png` | xxxhdpi |
| 144×144 | `icon-144.png` | xxhdpi |
| 96×96 | `icon-96.png` | xhdpi |
| 72×72 | `icon-72.png` | hdpi |
| 48×48 | `icon-48.png` | mdpi |

### Android Adaptive (`android_adaptive/`)
- `foreground.png` (512×512) — Logo on transparent background
- `background.png` (1080×1080) — Solid navy-blue gradient

## Expo integration

The active Expo icons are symlinked/copied to:
- `../images/icon.png` (iOS base icon)
- `../images/adaptive-icon.png` (Android adaptive foreground)
- `../images/splash-icon.png` (splash screen logo)
- `../images/favicon.png` (web)

No changes to `app.json` are required — it already points to these paths.

## Regenerating

1. **Master icon:** `python /app/backend/scripts/generate_app_icon.py`
   (uses Gemini Nano Banana via Emergent LLM Key)
2. **All sizes:** `python /app/backend/scripts/generate_icon_sizes.py`

## Design

- **T2D** text: white "T" and "D", orange-yellow "2" highlighted
- Thai flag (🇹🇭) waving at top
- Minimal road element with dashed lines
- Dark navy-blue gradient background
- Flat-ish, high-contrast, clean, premium mobile style
- Readable at 48×48 pixels
