---
name: frontend-design-thai2drive
description: 'Thai2Drive premium UI/UX design system. Use when: building components, designing layouts, choosing colors, refining typography, creating dark mode interfaces. Enforces modern design patterns, neon accents, cyberpunk elements, and accessibility for thai2drive mobile & web.'
argument-hint: 'Component type or design task (e.g., "quiz card", "teacher chat", "button styles")'
user-invocable: true
---

# Thai2Drive Frontend Design System

## Purpose

This skill ensures thai2drive gets a **professional, exclusive, and modern** UI that makes students want to log in and learn. Dark mode with strategic neon accents creates visual impact without distraction.

---

## Design Principles

### 1. **Dark Mode Foundation**
- **Primary Background:** Deep matte dark blue or near-black (`#0a0f1c` or similar)
- **Secondary Surface:** Slightly lighter blue-gray (`#131a2e`)
- **Never use:** Pure white, bright yellows, or bright greens
- **Text:** White or very light gray (`#e8eaed`, `#d0d2d7`)

### 2. **Neon Accents (Cyberpunk)**
- **Allowed Colors:**
  - `Cyan/Aqua` — active states, hover effects, highlights
  - `Magenta/Pink` — interactive elements, call-to-action buttons
  - `Deep Orange/Amber` — warnings, secondary actions, focus states
  
- **Forbidden Colors:**
  - Yellow (no neon yellow)
  - Bright Green (no neon green)
  - These create a chaotic, cheap-looking rainbow effect

### 3. **Neon Glow Effects** (Subtle & Selective)
- Use glowing **border effects** sparingly on active buttons and important elements
- Example: Active quiz button = thin magenta border with soft glow
- **Limit to:** 1–2 key UI elements per screen (not every button)
- **Effect:** `box-shadow: 0 0 12px rgba(255, 0, 127, 0.6)` (example)

### 4. **Accessibility & Contrast**
- **WCAG AA minimum:** 4.5:1 contrast ratio for text on backgrounds
- **Dark text on light backgrounds:** Use sparingly
- **Light text on dark backgrounds:** Default choice
- Test readability with Thai, Norwegian, and English languages

### 5. **Typography & Spacing**
- **Font Pairing:** Use modern sans-serifs (e.g., Inter, Poppins, DM Sans)
- **Font Weights:** Regular (400), Medium (500), Bold (700) — avoid exotic weights
- **Line Height:** 1.4–1.6 for readability across languages
- **Letter Spacing:** Slightly increased for visual breathing room
- **Hierarchy:** Clear size differences (e.g., 12px body, 16px medium, 20px large, 28px heading)

### 6. **Spacing & Layout**
- **Padding:** 12px, 16px, 24px, 32px (base unit = 4px or 8px)
- **Margins:** Consistent rhythm, avoid random gaps
- **Alignment:** Center when possible, edge-alignment for sidebars
- **Density:** Comfortable spacing for touch (min 44px tap targets on mobile)

---

## Component Guidelines

### Buttons
- **Primary (Action):** Magenta or Cyan background, white text, subtle glow on hover
- **Secondary:** Dark gray border, white text, light background on hover
- **Disabled:** Grayed out, no glow, reduced opacity (0.5)

### Cards
- **Background:** Slightly lighter than page background (`#131a2e` or similar)
- **Border:** Thin subtle border in dark cyan or magenta (~0.5–1px, low opacity)
- **Shadow:** Minimal (if any) — dark mode shouldn't use heavy shadows
- **Hover:** Subtle lift effect or border glow

### Forms & Inputs
- **Background:** Very dark (`#0f1424`)
- **Border:** Subtle cyan or magenta (active state)
- **Placeholder:** Faded gray text
- **Focus:** Neon border glow (cyan or magenta)
- **Validation:** Red for errors, green for success (accessible colors)

### Navigation (Bottom Tabs or Sidebar)
- **Active Tab:** Bold icon + magenta/cyan underline or background
- **Inactive Tab:** Faded gray icon
- **Hover:** Subtle color transition

---

## When to Use This Skill

✅ **Before writing CSS or React Native styles**  
✅ **When designing a new component or page**  
✅ **When choosing colors or deciding on a layout**  
✅ **When setting typography or spacing**  
✅ **When creating dark mode interfaces**  
✅ **When adding interactive effects (hover, focus, transitions)**  

---

## Quick Checklist

- [ ] Is the background dark (matte blue-black)?
- [ ] Are neon accents (cyan/magenta/orange) limited to interactive elements?
- [ ] Is text contrast ≥4.5:1 (WCAG AA)?
- [ ] Are buttons and tap targets ≥44px high?
- [ ] Is there consistent spacing (4px, 8px, 16px grid)?
- [ ] Are glows subtle and not on every element?
- [ ] Is the design consistent across web and mobile?
- [ ] Does it feel "exclusive and expensive" (not cheap)?

---

## Example Color Palette

```json
{
  "colors": {
    "background": "#0a0f1c",
    "surface": "#131a2e",
    "text": "#e8eaed",
    "textSecondary": "#a8adb5",
    "cyan": "#00d9ff",
    "magenta": "#ff0080",
    "orange": "#ff8c00",
    "success": "#10b981",
    "error": "#ef4444",
    "warning": "#f59e0b"
  }
}
```

---

## Related Resources

- [Thai2Drive AGENTS.md](../../AGENTS.md) — Design guidelines and color constraints
- [design_guidelines.json](../../design_guidelines.json) — Project-specific design specs
- [frontend/src/theme.ts](../../frontend/src/theme.ts) — Active theme constants

---

## Example Prompts to Try

1. **Design a quiz card component** → Shows dark background, neon accents, spacing
2. **Create a teacher chat UI** → Shows message bubbles, input field, accessibility
3. **Style a button with hover effects** → Shows glow, color transitions
4. **Choose colors for a dashboard** → Applies neon accents strategically
