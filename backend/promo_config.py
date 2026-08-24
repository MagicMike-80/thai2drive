"""
Lanseringskampanje — delt konfigurasjon.

Egen modul fordi BÅDE server.py (tilgangslogikk) og webapp.py (betalingssiden)
trenger flagget, og server.py importerer webapp.py. Ville flagget bodd i én av
dem, ville den andre fått sirkulær import.

Slå kampanjen AV: sett FREE_PROMO_MODE = False her, eller
miljøvariabelen FREE_PROMO_MODE=false i Railway. Da er den ordinære
betalingsmuren og prisene 99 / 249 / 699 tilbake ved neste forespørsel —
ingen omstart, ingen deploy, ingen databaseendring.
"""
import os


def _env_flag(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on", "ja")


# ── Hovedbryteren ─────────────────────────────────────────────────────────────
FREE_PROMO_MODE = _env_flag("FREE_PROMO_MODE", True)

# Hvor lenge en bruker som registrerer seg UNDER kampanjen beholder full tilgang.
# Dette er en ekte prøveperiode i databasen, ikke en visningseffekt: slås
# kampanjen av, beholder disse brukerne resten av sine 30 dager i stedet for å
# miste tilgangen midt i løpet. Nye brukere etter det får den vanlige gratisuken.
FREE_PROMO_DAYS = int(os.environ.get("FREE_PROMO_DAYS", "30") or 30)


def free_promo_active() -> bool:
    """Leses ved hver forespørsel, aldri cachet — derfor virker av-bryteren straks."""
    return _env_flag("FREE_PROMO_MODE", FREE_PROMO_MODE)
