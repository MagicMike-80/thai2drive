"""
premium_gate.py — FastAPI-avhengighet som setter AI-funksjoner bak betalingsmuren.

    from premium_gate import require_active_premium
    @router.post("/teacher/chat", dependencies=[Depends(require_active_premium)])

Regler
  * Uten innlogging eller med ugyldig/utløpt token            -> HTTP 402 (gate=register)
  * Innlogget men uten aktiv tilgang (gratis, utløpt, refundert) -> HTTP 402 (gate=upgrade)
  * Aktiv tilgang = admin, betalt abonnement som løper, aktiv gratisuke (trial),
    eller lanseringskampanjen (FREE_PROMO_MODE) — samme regel som /access/status og appens UI.

Status 402 er valgt fordi resten av appen allerede bruker den (usage.require_premium, /access/consume),
og webappen åpner betalingsmuren når den ser 402.

Databasen er fasit: token-påstanden `is_premium` leses aldri her, så en refundert eller utløpt
bruker mister tilgangen med en gang, selv med et token som fortsatt er gyldig i opptil 168 timer.
Strammes tilgangen til «kun betalt», er det denne ene funksjonen (`has_ai_access`) som endres.
"""

from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer(auto_error=False)


def has_ai_access(user: Optional[dict]) -> bool:
    """Har brukeren (fra databasen) rett til AI-funksjoner akkurat nå?"""
    import server  # lazy: server importerer rutene, så et toppnivå-import ville vært sirkulært

    return bool(user) and server._user_has_active_premium(user)


def _payment_required(error: str, gate: str, tier: str) -> HTTPException:
    return HTTPException(status_code=402, detail={"error": error, "gate": gate, "tier": tier})


async def require_active_premium(credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer)) -> dict:
    import server

    if not credentials:
        raise _payment_required("auth_required", "register", "guest")
    payload = server.verify_token(credentials.credentials)
    if not payload or not payload.get("sub"):
        raise _payment_required("auth_required", "register", "guest")
    user = await server.db.users.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise _payment_required("auth_required", "register", "guest")
    if not has_ai_access(user):
        raise _payment_required("premium_required", "upgrade", "registered")
    return user
