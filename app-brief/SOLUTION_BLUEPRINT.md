# SOLUTION BLUEPRINT: Restore the web guest entry

**Status:** READY FOR AGENT 3
**Date:** 2026-09-09

## Goal

Allow a signed-out customer to enter the existing web app as a guest and reach Michael, using the existing server-authoritative guest access contract.

## Explicit non-goals

- No backend endpoint or database changes.
- No changes to login, registration, Stripe, RevenueCat, premium entitlements, quotas, Railway configuration, media ranking, or mobile/Expo.
- No automatic anonymous account creation.

## Files

- `backend/webapp.py`: add localized guest UI, stable browser-local guest device ID, and `enterGuest()`.
- `tests/test_web_guest_entry_contract.py`: narrow regression contract.
- `app-brief/PATCH_REPORT.md`: implementation evidence and rollback.

## Data flow and API contracts

1. Customer chooses the localized guest button.
2. `ensureGuestDeviceId()` reuses `t2d_guest_device_id` from local storage or creates a random `web_guest_...` identifier. It contains no email, name, or password.
3. `enterGuest()` clears in-memory authenticated identity, assigns the guest ID, and calls the existing `enterApp()`.
4. Existing frontend requests continue to pass `device_id` to `/api/access/status`, `/api/access/consume`, and `/api/teacher/chat`.
5. Backend remains source of truth for the five-question guest allowance.

## Language, access, and premium consequences

- The guest button and supporting hint use the global NO/TH/EN UI dictionary.
- Missing/unknown language behavior remains governed by the existing global language function.
- The patch grants no premium entitlement and changes no numerical limit.
- Login and registration remain available and unchanged.

## Patch plan

1. Add a calm secondary guest action to the auth card.
2. Add `auth_guest_btn` and `auth_guest_hint` in NO/TH/EN.
3. Add a stable, random guest device helper plus `enterGuest()` next to existing auth functions.
4. Add static contract tests for the exact scope.

## Tests and manual verification

- Run the new guest-entry contract tests.
- Run existing Michael media/link tests and relevant web contract tests.
- Inspect the diff for auth/payment/premium spillover and secrets.
- After approved deployment, verify fresh production customer UI in NO/TH/EN:
  - guest reaches Michael;
  - right-rule answer is complete and shows the right-rule image;
  - bus answer is complete and shows the bus video;
  - sign 202 answer shows the sign card.

## Rollback

Revert the guest markup, two UI dictionary entries, helper functions, and the dedicated test file. No database rollback is needed.

## Production risk

Low and localized to signed-out web entry. The main risk is a malformed or unstable device ID; the contract test requires persistent storage and a random generator fallback.

No additional Michael decision is required because the product rules already explicitly define guest access as five questions.

**READY FOR AGENT 3**
