"""
RevenueCat Live Billing & Fail-Soft Subscription Engine
--------------------------------------------------------
Sjekker abonnementstatus direkte mot RevenueCat REST API
med miljøstyrt nøkkel og feilsikker fallback som sikrer at
kunder aldri blir låst ute under eksterne driftsbrudd.
"""
import os
import logging
from typing import Optional
from fastapi import APIRouter, Header, Query
from fastapi.responses import JSONResponse
import httpx

logger = logging.getLogger("billing")
router = APIRouter(tags=["billing"])

# Hent produksjonsnøkkel fra miljøvariabel med sandkasse-fallback for testing
REVENUECAT_API_KEY = os.getenv("REVENUECAT_API_KEY", "goog_sandbox_testkey_123456").strip()
REVENUECAT_API_URL = "https://api.revenuecat.com/v1"


@router.get("/api/billing/subscription")
@router.get("/billing/subscription")
async def check_user_subscription(
    app_user_id: str = Query(...),
    authorization: Optional[str] = Header(None),
):
    """
    Sjekker abonnementsstatus direkte mot RevenueCat API med feilsikker fallback.
    """
    if not app_user_id:
        return JSONResponse({"premium": False, "error": "Missing app_user_id"}, status_code=400)

    # Hvis testnøkkel brukes lokalt, gi respons uten ekstern nettverksfeil
    if "sandbox" in REVENUECAT_API_KEY and not os.getenv("REVENUECAT_API_KEY"):
        logger.info("RevenueCat sandbox mode for user %s", app_user_id)
        return JSONResponse({
            "premium": False,
            "sandbox": True,
            "entitlements": {},
            "status": "sandbox_mode"
        })

    headers = {
        "Authorization": f"Bearer {REVENUECAT_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{REVENUECAT_API_URL}/subscribers/{app_user_id}",
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                entitlements = data.get("subscriber", {}).get("entitlements", {})
                premium_entitlement = entitlements.get("premium") or entitlements.get("pro") or entitlements.get("teori_tilgang")
                is_premium = False
                if premium_entitlement:
                    expires_date = premium_entitlement.get("expires_date")
                    is_premium = expires_date is not None

                return JSONResponse({
                    "success": True,
                    "premium": is_premium,
                    "entitlements": entitlements
                })
            else:
                logger.warning("RevenueCat svarte status %d for bruker %s", response.status_code, app_user_id)
                return JSONResponse({
                    "success": False,
                    "premium": False,
                    "status_code": response.status_code,
                    "error": "Unable to verify with RevenueCat"
                })

    except Exception as e:
        # Hvis nettverket eller RevenueCat er nede, kjør fail-soft så kunden ikke låses ute!
        logger.error("RevenueCat tilkoblingsfeil: %s — aktiverer fail-soft", e)
        return JSONResponse({
            "success": True,
            "premium": True,
            "offline_fallback": True,
            "warning": "External billing provider unavailable, temporary grace access granted."
        })
