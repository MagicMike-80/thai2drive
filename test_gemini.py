"""
Thai2Drive – Gemini Enterprise Agent Platform test
Kjør: python test_gemini.py
"""

import os
from google import genai
from google.genai.types import HttpOptions

# ── Config ──────────────────────────────────────────────────────────────────
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "thai2drive")   # <-- ditt project ID
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_ENTERPRISE", "True")

# ── Client ───────────────────────────────────────────────────────────────────
client = genai.Client(http_options=HttpOptions(api_version="v1"))

# ── Test 1: Enkel Thai2Drive-forespørsel ─────────────────────────────────────
print("=" * 60)
print("Thai2Drive – Gemini Enterprise API Test")
print("=" * 60)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=(
        "Du er en norsk kjørelærer som hjelper Thai-talende elever. "
        "Forklar på thai hva vikeplikt betyr i norsk trafikk. "
        "Svar på thai med norsk oversettelse i parentes."
    ),
)

print("\n✅ Test 1 – Kjørelærer på thai:")
print(response.text)

# ── Test 2: Teoriprøve-spørsmål ───────────────────────────────────────────────
response2 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=(
        "Lag et teoriprøve-spørsmål om fartsgrenser i Norge. "
        "Format: spørsmål på norsk, 4 svaralternativer (A-D), og korrekt svar. "
        "Legg til thai-oversettelse av spørsmålet under."
    ),
)

print("\n✅ Test 2 – Teoriprøve-spørsmål:")
print(response2.text)

print("\n" + "=" * 60)
print("✅ Gemini Enterprise fungerer for Thai2Drive!")
print("=" * 60)
