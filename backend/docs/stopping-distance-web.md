# Stopping-distance web screen

The actual HTML web app (`/api/web`) has a Stopplengde entry below the official theory exam button. It opens `/api/web?tool=stopping-distance` in the existing language/session shell. Desktop expands to 1100 px; narrow web view stacks controls above the road. The Expo/native app is not changed.

Controls: speed 30–120 km/h, presets 30/50/80/100/120, dry/wet/snow/ice, fixed 1-second reaction time, Show stopping distance, 2/3-second following distance, four expandable calculation steps, and return home. Defaults are 80 km/h, dry road and 2 seconds. The silver Tesla moves briefly on Show; reduced-motion preference disables motion. The red Tesla is the home entry icon. The supplied T2D logo is already the existing asset.

Calculations use the unchanged `/api/math/stopping-distance` and `/api/math/following-distance` endpoints. At 80 km/h on dry road: 22.2 m reaction + 64 m braking = 86.2 m; following distance is 44.4 m at 2 seconds or 66.7 m at 3 seconds. Illustrations adapt their scale and are not physical stopping-performance measurements. Errors hide stale results and permit retry. New labels use the global `UI`/`appLang` language system with NO/TH/EN values.

## Local verification

Run `.venv/Scripts/python.exe -m pytest -p no:cacheprovider backend/tests/test_stopping_distance_web.py backend/tests/test_exam_ui.py -q`. Node is required for the executable JavaScript harness. It checks controls, formulas, language/status changes, stale requests, API failures, navigation, animation cancellation and reduced motion.

For an isolated local preview, run `.venv/Scripts/python.exe backend/scripts/preview_stopping_distance.py` and open `http://127.0.0.1:8088/api/web`. Continue as guest. This preview serves the real HTML, assets and math endpoints, but deliberately omits auth, payment, database and content services. Their 404 responses in preview are not production regressions or proof that those integrations work.

Check all controls in NO/TH/EN and at desktop/narrow widths. Verify the home entry, Show animation, steps toggle, browser Back, bottom navigation and reload. No deployment is part of the feature-branch push.
