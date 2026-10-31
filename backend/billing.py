"""
RevenueCat Live Billing & Fail-Soft Subscription Engine
--------------------------------------------------------
Sjekker abonnementstatus direkte mot RevenueCat REST API
med miljøstyrt nøkkel og feilsikker fallback som sikrer at
kunder aldri blir låst ute under eksterne driftsbrudd.
"""
import os
import logging
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import quote
from fastapi import APIRouter, Header, Query
from fastapi.responses import JSONResponse
import httpx

logger = logging.getLogger("billing")
router = APIRouter(tags=["billing"])

# Hent produksjonsnøkkel utelukkende fra miljøvariabel — ingen hardkodet fallback-nøkkel
REVENUECAT_API_KEY = os.getenv("REVENUECAT_API_KEY", "").strip()
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

    # The caller may only inspect their own RevenueCat customer. Import lazily
    # because server.py includes this router after defining verify_token.
    from server import verify_token
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse({"premium": False, "error": "Not authenticated"}, status_code=401)
    claims = verify_token(authorization.removeprefix("Bearer ").strip())
    if not claims:
        return JSONResponse({"premium": False, "error": "Invalid token"}, status_code=401)
    if claims.get("sub") != app_user_id:
        return JSONResponse({"premium": False, "error": "Forbidden"}, status_code=403)

    # Never claim a sandbox state or access when the server key is missing.
    if not REVENUECAT_API_KEY:
        logger.warning("RevenueCat API key is not configured")
        return JSONResponse({"success": False, "premium": False,
                             "error": "RevenueCat is not configured"}, status_code=503)

    headers = {
        "Authorization": f"Bearer {REVENUECAT_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{REVENUECAT_API_URL}/subscribers/{quote(app_user_id, safe='')}",
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                entitlements = data.get("subscriber", {}).get("entitlements", {})
                premium_entitlement = entitlements.get("premium") or entitlements.get("pro") or entitlements.get("teori_tilgang")
                is_premium = False
                if isinstance(premium_entitlement, dict) and premium_entitlement:
                    expires_date = premium_entitlement.get("expires_date")
                    if expires_date is None:
                        # A non-expiring entitlement is a lifetime purchase.
                        is_premium = bool(premium_entitlement.get("purchase_date"))
                    else:
                        try:
                            expires_at = datetime.fromisoformat(str(expires_date).replace("Z", "+00:00"))
                            is_premium = expires_at > datetime.now(timezone.utc)
                        except (TypeError, ValueError):
                            is_premium = False

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
                }, status_code=503)

    except Exception as e:
        logger.error("RevenueCat connection error: %s", e)
        return JSONResponse({
            "success": False,
            "premium": False,
            "error": "Unable to verify with RevenueCat"
        }, status_code=503)
