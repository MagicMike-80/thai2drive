"""
Central site configuration — single source of truth for the public website URL.

How to change domains (now or in the future):
  Set env var PUBLIC_SITE_URL in backend/.env to your custom domain, e.g.:

    PUBLIC_SITE_URL=https://thai2drive.no

  If unset, falls back to the current Emergent preview URL so everything keeps
  working without any code changes.

Any code that needs the absolute public URL (SEO meta tags, sitemap, social
sharing, emails, etc.) MUST import from here — never hard-code a domain.
"""
from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Defaults (current preview) ───
_DEFAULT_PUBLIC_URL = "https://thai2drive.no"

# Alternate domains the site may also answer on (used for redirects/canonical).
# If you buy more than one domain, list them here.
_EXTRA_KNOWN_DOMAINS = [
    "thai2drive.no",
    "thai2driveapp.no",
    "thaiteori.no",
]


def public_site_url() -> str:
    """Absolute https URL of the marketing site (no trailing slash)."""
    raw = os.environ.get("PUBLIC_SITE_URL", _DEFAULT_PUBLIC_URL).strip()
    return raw.rstrip("/")


def site_host() -> str:
    """Bare hostname (for canonical HREFs, sitemap, etc.)."""
    return public_site_url().replace("https://", "").replace("http://", "")


def canonical_url(path: str = "/") -> str:
    """Build an absolute canonical URL for a given site path."""
    if not path.startswith("/"):
        path = "/" + path
    return public_site_url() + path


def website_base() -> str:
    """
    Base URL segment where the marketing pages are served.

    On the current Emergent preview the pages live under /api/ because the
    k8s ingress routes /api/* to the backend. When we deploy on a custom
    domain, set SITE_ROUTING_MODE=clean to drop the /api/ prefix from the
    canonical URLs (the actual FastAPI routes keep their /api prefix — we
    would add a front-door redirect at deploy time).
    """
    mode = os.environ.get("SITE_ROUTING_MODE", "prefixed")
    return "" if mode == "clean" else "/api"


def site_url(path: str) -> str:
    """Build an absolute URL for a site path, respecting routing mode."""
    if not path.startswith("/"):
        path = "/" + path
    base = website_base()
    return public_site_url() + base + path


def extra_known_domains() -> list[str]:
    return list(_EXTRA_KNOWN_DOMAINS)
