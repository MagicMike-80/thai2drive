# Stopping-distance web screen

The actual HTML web app (`/api/web`) has a Stopplengde entry below the official theory exam button. It opens `/api/web?tool=stopping-distance` in the existing language/session shell. Desktop expands to 1100 px; narrow web view stacks controls above the road. The Expo/native app is not changed.

Controls: speed 30–120 km/h, presets 30/50/80/100/120, dry/wet/snow/ice, selectable 1/2/3-second reaction time, Show stopping distance, four expandable calculation steps, and return home. A separate following-distance module uses a three-second gap. Defaults are 80 km/h, dry road, and 1-second reaction time. The silver Tesla moves briefly on Show; reduced-motion preference disables motion. The red Tesla is the home entry icon.

Calculations use `/api/math/stopping-distance` with the selected `reaction` parameter and `/api/math/following-distance?seconds=3` for the separate module. The educational shortcuts are `(speed/10)×3×seconds` for reaction distance and `(speed/10)²/2` for dry braking distance. At 80 km/h on dry road: 24 m reaction + 32 m braking = 56 m stop length at 1 second; 48 + 32 = 80 m at 2 seconds; 72 + 32 = 104 m at 3 seconds. Wet road doubles the braking part; snow and ice quadruple it in this simplified model. The physical three-second following gap is 66.7 m at 80 km/h. Illustrations and shortcuts are not measured stopping performance. Errors hide stale results and permit retry. New labels use the global `UI`/`appLang` language system with NO/TH/EN values.

## Local verification

Run `.venv/Scripts/python.exe -m pytest -p no:cacheprovider backend/tests/test_traffic_math.py backend/tests/test_stopping_distance_web.py backend/tests/test_exam_ui.py -q`. Node is required for the executable JavaScript harness. It checks controls, formulas, language/status changes, stale requests, API failures, navigation, animation cancellation and reduced motion.

For an isolated local preview, run `.venv/Scripts/python.exe backend/scripts/preview_stopping_distance.py` and open `http://127.0.0.1:8088/api/web`. Continue as guest. This preview serves the real HTML, assets and math endpoints, but deliberately omits auth, payment, database and content services. Their 404 responses in preview are not production regressions or proof that those integrations work.

Check all controls in NO/TH/EN and at desktop/narrow widths. Verify the home entry, Show animation, steps toggle, browser Back, bottom navigation and reload. No deployment is part of the feature-branch push.
