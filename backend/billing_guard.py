"""
billing_guard.py — rene hjelpere for RevenueCat-nøkkelvalidering.

Ingen nett, ingen HTTP-avhengighet, ingen import-tid-lesning av miljø. Alt her
er rene funksjoner så billing-koden kan testes offline.

Formål: oppdage at en sandkasse-/placeholder-nøkkel er i bruk, og la
billing.py logge tydelig (kritisk i produksjon, informativt ellers) uten at
appen krasjer når en ekte produksjonsnøkkel mangler.
"""

import os

PLACEHOLDER_KEY = "goog_sandbox_testkey_123456"
_PROD_ENV_VALUES = {"production", "prod"}
_ENV_VARS = ("RAILWAY_ENVIRONMENT", "RAILWAY_ENVIRONMENT_NAME", "ENVIRONMENT", "APP_ENV", "ENV")


def looks_like_sandbox_key(key) -> bool:
    """True hvis nøkkelen mangler eller åpenbart er en sandkasse-/placeholder-nøkkel."""
    k = (key or "").strip().lower()
    if not k:
        return True
    return "sandbox" in k or k == PLACEHOLDER_KEY


def is_production_env(env=None) -> bool:
    """True hvis en kjent miljøvariabel sier at dette er produksjon."""
    env = env if env is not None else os.environ
    for var in _ENV_VARS:
        if (env.get(var) or "").strip().lower() in _PROD_ENV_VALUES:
            return True
    return False


def sandbox_key_status(key, env=None):
    """Returner ``(level, message)`` for logging.

    * ``("ok", None)``     — en ekte nøkkel er satt, ingenting å melde.
    * ``("error", msg)``   — sandkassenøkkel i produksjon: abonnementssjekk av.
    * ``("warn", msg)``    — sandkassemodus utenfor produksjon: forventet lokalt.
    """
    if not looks_like_sandbox_key(key):
        return ("ok", None)
    if is_production_env(env):
        return (
            "error",
            "RevenueCat: SANDBOX/placeholder-nøkkel oppdaget i PRODUKSJON. "
            "Abonnementssjekk er deaktivert og alle brukere behandles som gratis. "
            "Sett REVENUECAT_API_KEY til en ekte produksjonsnøkkel.",
        )
    return (
        "warn",
        "RevenueCat kjører i sandbox-modus (ingen ekte REVENUECAT_API_KEY). "
        "Abonnementssjekk returnerer alltid 'ikke premium'.",
    )
