"""
Shared language-routing helpers for the public thai2drive.no site
(landing page, guide, quiz app entry points).

Single source of truth for:
- which languages exist and how they map to <html lang>/og:locale/hreflang
- the shared language-preference cookie (read server-side for redirects)
- hreflang / canonical link generation per page
- per-language SEO title/description strings
- server-side language filtering to avoid mixed-language markup for crawlers

Deliberately NOT used by anything under /api/admin, Stripe, auth, or the
mobile app — this module only concerns the public marketing site + quiz app shell.
"""
from __future__ import annotations

import re
from typing import Optional

from fastapi import Request, Response

from site_config import public_site_url

LANGS = ["th", "no", "en"]
HTML_LANG = {"th": "th", "no": "nb", "en": "en"}
OG_LOCALE = {"th": "th_TH", "no": "nb_NO", "en": "en_US"}

LANG_COOKIE = "t2d_site_lang"
_COOKIE_MAX_AGE = 365 * 24 * 3600

SEO_META = {
    "home": {
        "th": {
            "title": "สอบทฤษฎีใบขับขี่นอร์เวย์ ภาษาไทย | Thai2Drive",
            "description": "ฝึกสอบทฤษฎีใบขับขี่นอร์เวย์ด้วยภาษาไทย กว่า 1000 ข้อพร้อมคำอธิบาย เตรียมพร้อมสำหรับการสอบจริง",
        },
        "no": {
            "title": "Teoriprøven på thai – øv med 1000+ spørsmål | Thai2Drive",
            "description": "Bestå den norske teoriprøven lettere – over 1000 spørsmål med forklaringer på thai, norsk og engelsk.",
        },
        "en": {
            "title": "Norwegian driving theory test in Thai | Thai2Drive",
            "description": "Practice for the Norwegian driving theory test with 1000+ questions and explanations in Thai, Norwegian and English.",
        },
    },
    "guide": {
        "th": {
            "title": "คู่มือสอบใบขับขี่นอร์เวย์ฉบับคนไทย | Thai2Drive",
            "description": "คู่มือฉบับสมบูรณ์สำหรับคนไทยในนอร์เวย์ อธิบายทฤษฎีและการสอบขับรถเป็นภาษาไทย",
        },
        "no": {
            "title": "Fra Thailand til norsk førerkort | Thai2Drive",
            "description": "Komplett guide for thai-folk i Norge: teoriprøve og kjøreprøve forklart på norsk.",
        },
        "en": {
            "title": "Guide: Norwegian driving licence for Thai residents | Thai2Drive",
            "description": "A complete guide for Thai residents in Norway: the theory and practical driving tests explained in English.",
        },
    },
    "app": {
        "th": {
            "title": "แอปฝึกสอบทฤษฎีใบขับขี่นอร์เวย์ | Thai2Drive",
            "description": "ฝึกข้อสอบทฤษฎีใบขับขี่นอร์เวย์ด้วยภาษาไทย กว่า 1000 ข้อ พร้อมคำอธิบาย",
        },
        "no": {
            "title": "Øv til teoriprøven – quiz-app | Thai2Drive",
            "description": "Øv til den norske teoriprøven med over 1000 spørsmål og forklaringer på norsk.",
        },
        "en": {
            "title": "Practice the Norwegian theory test – quiz app | Thai2Drive",
            "description": "Practice for the Norwegian driving theory test with 1000+ questions and explanations in English.",
        },
    },
}


def normalize_lang(lang: Optional[str]) -> str:
    return lang if lang in LANGS else "th"


def detect_lang(request: Request) -> str:
    """Cookie first (explicit prior choice), then Accept-Language, then Thai."""
    cookie = request.cookies.get(LANG_COOKIE)
    if cookie in LANGS:
        return cookie
    accept = request.headers.get("accept-language", "")
    for part in accept.split(","):
        code = part.split(";")[0].strip().lower()[:2]
        if code in ("nb", "nn"):
            code = "no"
        if code in LANGS:
            return code
    return "th"


def api_prefix_redirect(request: Request, status_code: int = 301):
    """
    Several routers in this app are double-mounted at both "" and "/api"
    (Railway historically routed /api/* to the backend). For the specific
    pages this language cleanup touches (home, guide, app), the old
    /api/-prefixed URL should permanently redirect to the clean one instead
    of serving duplicate content. Returns a RedirectResponse if `request`
    came in via the /api/ mount, else None (caller proceeds normally).
    """
    path = request.url.path
    if path.startswith("/api/") or path == "/api":
        from fastapi.responses import RedirectResponse
        stripped = path[4:] or "/"
        qs = f"?{request.url.query}" if request.url.query else ""
        return RedirectResponse(url=f"{stripped}{qs}", status_code=status_code)
    return None


def set_lang_cookie(response: Response, lang: str) -> None:
    response.set_cookie(
        LANG_COOKIE,
        normalize_lang(lang),
        max_age=_COOKIE_MAX_AGE,
        path="/",
        samesite="lax",
    )


def seo_meta(page: str, lang: str) -> dict:
    return SEO_META[page][normalize_lang(lang)]


def hreflang_tags(path_suffix: str) -> str:
    """path_suffix: '' for home, '/guide' for the guide, '/app' for the webapp."""
    base = public_site_url()
    tags = [
        f'<link rel="alternate" hreflang="th" href="{base}/th{path_suffix}"/>',
        f'<link rel="alternate" hreflang="nb" href="{base}/no{path_suffix}"/>',
        f'<link rel="alternate" hreflang="no" href="{base}/no{path_suffix}"/>',
        f'<link rel="alternate" hreflang="en" href="{base}/en{path_suffix}"/>',
        f'<link rel="alternate" hreflang="x-default" href="{base}/th{path_suffix}"/>',
    ]
    return "\n".join(tags)


def canonical_for(lang: str, path_suffix: str) -> str:
    return f"{public_site_url()}/{normalize_lang(lang)}{path_suffix}"


def app_hreflang_tags() -> str:
    return hreflang_tags("/app")


def app_canonical_for(lang: str) -> str:
    return canonical_for(lang, "/app")


def filter_landing_html(html: str, target_lang: str) -> str:
    """
    Filter landing page HTML server-side:
    Removes <span ... data-lang="other">...</span> for all languages other than target_lang.
    Preserves target_lang content, preserving classes like .block.
    """
    target = normalize_lang(target_lang)

    def repl(m: re.Match) -> str:
        tag_attrs = m.group(1)
        content = m.group(2)
        lang_match = re.search(r'data-lang=["\']([a-z]+)["\']', tag_attrs)
        if not lang_match:
            return m.group(0)
        tag_lang = lang_match.group(1)
        if tag_lang != target:
            return ""
        class_match = re.search(r'class=["\']([^"\']+)["\']', tag_attrs)
        cls = class_match.group(1) if class_match else ""
        if "block" in cls:
            return f'<span class="block">{content}</span>'
        return content

    filtered = re.sub(r'<span\s+([^>]*data-lang=[^>]+)>([\s\S]*?)</span>', repl, html)
    return filtered


def filter_guide_html(html: str, target_lang: str) -> str:
    """
    Filter guide page HTML server-side:
    Removes <span class="tl tl-other">...</span> for all languages other than target_lang.
    Unwraps <span class="tl tl-target">...</span> so only the target text remains.
    """
    target = normalize_lang(target_lang)

    def repl(m: re.Match) -> str:
        tag_lang = m.group(1)
        content = m.group(2)
        if tag_lang != target:
            return ""
        return content

    filtered = re.sub(r'<span\s+class=["\']tl\s+tl-([a-z]+)["\']>([\s\S]*?)</span>', repl, html)
    return filtered


# Shared client-side language-switch helper: navigates to the sibling-language
# version of the CURRENT page (not the homepage), and persists the choice in
# both the shared cookie (read server-side) and localStorage.
LANG_SWITCH_JS = r"""
function t2dSwitchLang(lang){
  var path = window.location.pathname;
  var rest = '';
  var m = path.match(/^\/(th|no|en)(\/.*)?$/);
  if (m) {
    rest = m[2] || '';
  } else {
    var m2 = path.match(/^\/app\/(th|no|en)$/);
    if (m2) {
      rest = '/app';
    } else if (path === '/app' || path.startsWith('/app/')) {
      rest = '/app';
    } else if (path === '/guide' || path.startsWith('/guide/')) {
      rest = '/guide';
    }
  }
  document.cookie = 't2d_site_lang=' + lang + ';path=/;max-age=31536000;SameSite=Lax';
  window.location.href = '/' + lang + rest + window.location.search;
}
"""
