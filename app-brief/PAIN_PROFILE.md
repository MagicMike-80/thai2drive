# PAIN PROFILE: Web blocks the guest path to Michael

**Status:** VERIFIED
**Date:** 2026-09-09
**Target:** `C:\Users\lexuz\AppData\Local\Temp\thai2drive-patch-a-ship`

## User pain and expected behavior

The production web app stops signed-out customers at the authentication screen, so a customer cannot reach Michael to verify the right-rule image, bus material, or traffic signs. Thai2Drive's access contract says a guest gets five questions. A signed-out customer must therefore be able to enter the web app as a guest, while registration, login, premium, and payment behavior remain unchanged.

## Verified observations

- Fresh production UI inspection at `https://thai2drive.no/api/web` showed only language, login, and registration controls. No guest entry was visible.
- `backend/webapp.py:5488-5501` sends every client without a stored token to `screenAuth`.
- `backend/webapp.py:5519-5532` already has an `enterApp()` flow that can open the web UI.
- `backend/webapp.py:4640-4642` initializes `deviceId` as null, and no signed-out startup path assigns it.
- `backend/usage.py:8-10` and `backend/usage.py:60-66` define the product contract: guest five lifetime questions, registered ten daily, premium unlimited.
- `backend/teacher_chat.py:2210-2228` accepts optional `device_id` and `user_id`; Michael chat itself does not require authentication.
- `backend/webapp.py:10643-10652` already sends Michael chat without an Authorization header and includes optional device/user identifiers.

## Root cause

The backend and Michael frontend call support a guest, but the auth screen exposes no guest action and startup assigns no stable guest device ID. This is a web-entry routing gap, not a media-linking or teacher API failure.

## Scope and risk

- Scope: auth-screen presentation, stable browser-local guest ID, and a signed-out `enterApp()` action in `backend/webapp.py`.
- Main risk: accidentally changing login/logout, access limits, premium gates, or language purity.
- Out of scope: backend APIs, MongoDB, Stripe, RevenueCat, Railway configuration, mobile/Expo, and media ranking.

## Acceptance criteria

1. Auth screen shows one calm guest button in NO, TH, and EN through the global UI dictionary.
2. Guest action creates or reuses a non-personal stable local device ID and enters the app without a token.
3. Existing login and registration flows remain unchanged.
4. Guest access continues to use the server-authoritative five-question rule; no client-side limit is increased.
5. Fresh customer UI questions can be sent to Michael and visibly render the right-rule image, bus material, and sign card.
6. No mixed-language learner-facing UI.

## Handoff

Root cause is verified. Ready for Solution Architect.
