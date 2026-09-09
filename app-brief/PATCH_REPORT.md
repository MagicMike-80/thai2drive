# PATCH REPORT: Web guest entry to Michael

**Status:** IMPLEMENTED AND LOCALLY VERIFIED
**Date:** 2026-09-09

## Changed files

- `backend/webapp.py`
  - Added one calm secondary guest action on the auth screen.
  - Added complete NO/TH/EN labels through the global UI dictionary.
  - Added a persistent random `web_guest_...` browser identifier.
  - Added `enterGuest()` that enters the existing app without minting a user or premium status.
- `tests/test_web_guest_entry_contract.py`
  - Requires localized guest controls, persistent random identity, no signup side effect, and unchanged 5/10 access constants.

## Verification

- New and related Michael/web suites: **45/45 PASS**.
- Inline JavaScript syntax: **2/2 script blocks PASS**.
- `git diff --check`: PASS (only existing Windows line-ending conversion notices for report files).
- Diff inspection: guest patch adds 58 lines to `backend/webapp.py`; no backend endpoint, database, payment, entitlement, media-ranking, or mobile file changed.
- QA caught and removed one extra closing HTML tag before push; the regression suite now parses the auth fragment and requires balanced markup.

## Remaining proof

Production is not yet claimed fixed. After deploy, a fresh signed-out customer flow must use the guest button and visibly prove all three Michael responses: right-rule image, bus video, and sign 202 card. NO/TH/EN must remain isolated and the right-rule and bus answers must be complete.

## Rollback

Revert the guest CSS/markup, two UI keys, two helper functions, and the dedicated contract test. No database rollback is required.

Handoff to QA Gate.
