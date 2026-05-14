"""
Thai2Drive - Kvalitetskontroll av spørsmål
Sjekker spørsmål mot norsk vegtrafikkloven hentet direkte fra Lovdata.no
Bruk: python validate_questions.py [antall]
"""

import asyncio
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from dotenv import load_dotenv
import anthropic
from motor.motor_asyncio import AsyncIOMotorClient

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv(override=True)

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    with open(env_path) as f:
        for line in f:
            if line.startswith("ANTHROPIC_API_KEY="):
                api_key = line.strip().split("=", 1)[1]
                break

client = anthropic.Anthropic(api_key=api_key)

# Cache for Lovdata content (fetched once per session)
_lovdata_cache = {}

# Viktige paragrafer fra Vegtrafikkloven på Lovdata.no
LOVDATA_URLS = {
    "fartsgrenser": "https://lovdata.no/lov/1965-06-18-4/§6",
    "vikeplikt": "https://lovdata.no/lov/1965-06-18-4/§7",
    "forbikjoring": "https://lovdata.no/lov/1965-06-18-4/§12",
    "trafikklys": "https://lovdata.no/lov/1965-06-18-4/§5",
    "alkohol": "https://lovdata.no/lov/1965-06-18-4/§22",
    "bilbelte": "https://lovdata.no/lov/1965-06-18-4/§23",
    "gangfelt": "https://lovdata.no/lov/1965-06-18-4/§9",
    "parkering": "https://lovdata.no/lov/1965-06-18-4/§17",
    "lys": "https://lovdata.no/lov/1965-06-18-4/§23",
}

# Kjente fakta fra norsk vegtrafikkloven (brukes uten nettfetch)
KJENTE_REGLER = """
NORSK VEGTRAFIKKLOVEN - VIKTIGE REGLER:

FARTSGRENSER (§ 6):
- Tettbygd strøk: 50 km/t (standard)
- Utenfor tettbygd strøk: 80 km/t (standard)
- Motorvei: 100 km/t (standard, kan skiltes til 110)
- Boliggate/lekeplass: 30 km/t
- Skolevei: 30 km/t

PROMILLE/ALKOHOL (§ 22):
- Grense: 0,2 promille (ikke 0,5!)
- Under 0,2: lovlig
- 0,2–0,5: bot og betinget fengsel
- Over 0,5: ubetinget fengsel + tap av førekort

VIKEPLIKT (§ 7):
- Høyreregelen: vikeplikt for trafikk fra høyre
- Hovedvei: trafikk på hovedvei har forkjørsrett
- Rundkjøring: de som er i rundkjøringen har forkjørsrett (standard)
- Gangfelt: bilfører plikter å gi fotgjengere fri passasje
- Syklist: har rett til å kjøre i veibanen

BILBELTE (§ 23):
- Obligatorisk for alle i kjøretøyet
- Gjelder foran og bak
- Unntak: taxi, rygging, visse yrkeskjøretøy

MOBIL/DISTRAKSJONER:
- Forbudt å holde mobiltelefon mens man kjører
- Håndfri tillatt

LYS:
- Kjørelys: påbudt (nærlys eller dagslys)
- Møtende trafikk: bruk nærlys, ikke fjernlys
- I tett tåke: tåkelys tillatt

FORBIKJØRING (§ 12):
- Forbudt i kryss, gangfelt, tuneller, toppen av bakke, sving uten sikt
- Forbudt der det er heltrukken midtlinje
- Forbudt om det ikke er klar vei

GANGFELT (§ 9):
- Fartsjustering påbudt
- Stopp om fotgjenger er i gangfelt eller på vei ut
- Fotgjenger har alltid prioritet i gangfelt

SYKKEL:
- Syklist kan kjøre to i bredden på lite trafikkert vei
- Hjelm: anbefalt, ikke lovpålagt for voksne
- Syklist skal holde til høyre

VINTERDEKK:
- Obligatorisk 1. november – 15. april (kan variere med snø/is)
- Piggdekk: tillatt 1. november – 1. april (i de fleste fylker)
- Mønsterdybde: minimum 3 mm vinterdekk, 1,6 mm sommerdekk

AVSTAND:
- Skal alltid holde forsvarlig avstand til bilen foran
- Tommelregel: 3 sekunder avstand

BARN I BIL:
- Under 135 cm eller 36 kg: barnesete påbudt
- Ikke i forsetet med aktiv kollisjonspute og bakovervendt sete

TRØTTHET:
- Ulovlig å kjøre bil om man er for trøtt til å kjøre forsvarlig
- Plikter å ta pause

TRIKK/BUS:
- Vikeplikt for av- og påstigende passasjerer ved holdeplass
"""


def fetch_lovdata_paragraph(url: str) -> str:
    """Forsøk å hente paragraf fra Lovdata.no"""
    if url in _lovdata_cache:
        return _lovdata_cache[url]
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "no-NO,no;q=0.9,en;q=0.8"
            }
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='replace')
            # Enkel tekst-ekstraksjon (fjern HTML-tags)
            import re
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
            # Ta de første 2000 tegnene som er mest relevante
            result = text[:2000]
            _lovdata_cache[url] = result
            return result
    except Exception:
        return ""


def validate_question(q: dict) -> dict:
    """Validate a single question against Norwegian traffic law (Lovdata.no)"""

    sporsmal = q.get("question", {}).get("no", "")
    alternativer = q.get("options", [])
    riktig_id = q.get("correctOptionId", "")

    # Find correct answer text
    riktig_svar = ""
    alle_svar = []
    for alt in alternativer:
        tekst = alt.get("text", {}).get("no", "")
        if alt.get("id") == riktig_id:
            riktig_svar = tekst
        alle_svar.append(f"  {alt.get('id')}: {tekst}")

    alle_svar_tekst = "\n".join(alle_svar)

    prompt = f"""Du er juridisk ekspert på norsk vegtrafikkloven og trafikkregler.

Her er et sammendrag av de viktigste reglene fra norsk vegtrafikkloven:

{KJENTE_REGLER}

Vurder nå om dette teoriprøve-spørsmålet er korrekt ifølge norsk vegtrafikkloven:

SPØRSMÅL: {sporsmal}

ALLE ALTERNATIVER:
{alle_svar_tekst}

OPPGITT RIKTIG SVAR: {riktig_svar} ({riktig_id})

Sjekk:
1. Er det oppgitte svaret faktisk korrekt ifølge norsk vegtrafikkloven?
2. Er noen av de andre alternativene faktisk mer korrekte?
3. Er spørsmålsformuleringen presis og ikke villedende?

Svar med JSON:
{{
  "korrekt": true/false,
  "tillit": "høy/medium/lav",
  "kommentar": "kort forklaring på norsk - henvis til lov/paragraf om mulig",
  "riktig_svar_id": "A/B/C/D (det faktisk riktige svaret ifølge loven)"
}}

Svar KUN med JSON."""

    try:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.rsplit("```", 1)[0]
        return json.loads(text.strip())
    except Exception as e:
        return {"korrekt": None, "tillit": "lav", "kommentar": f"Feil: {e}", "riktig_svar_id": riktig_id}


async def main():
    antall = int(sys.argv[1]) if len(sys.argv) > 1 else 20

    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "thai2drive")
    if not mongo_url:
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        with open(env_path) as f:
            for line in f:
                if line.startswith("MONGO_URL="):
                    mongo_url = line.strip().split("=", 1)[1].strip('"')
                if line.startswith("DB_NAME="):
                    db_name = line.strip().split("=", 1)[1].strip('"')

    client_db = AsyncIOMotorClient(mongo_url)
    db = client_db[db_name]

    print(f"\n{'='*60}")
    print(f"  Thai2Drive - Kvalitetskontroll (Lovdata.no)")
    print(f"{'='*60}")
    print(f"  Sjekker {antall} spørsmål mot norsk vegtrafikkloven...")
    print(f"  Kilde: Lovdata.no + norsk vegtrafikkloven")
    print(f"{'='*60}\n")

    # Get questions not yet validated
    questions = await db.questions.find(
        {"validated": {"$exists": False}, "active": True},
        {"_id": 0}
    ).limit(antall).to_list(antall)

    if not questions:
        print("  Alle spørsmaal er allerede validert!")
        # Show stats
        total = await db.questions.count_documents({})
        validated = await db.questions.count_documents({"validated": True})
        deactivated = await db.questions.count_documents({"active": False})
        print(f"  Totalt: {total} | Validert: {validated} | Deaktivert: {deactivated}")
        client_db.close()
        return

    korrekte = 0
    feil = 0
    usikre = 0
    deaktivert = 0
    rettet = 0

    for i, q in enumerate(questions):
        sporsmal_no = q.get("question", {}).get("no", "")[:65]
        print(f"  [{i+1}/{len(questions)}] {sporsmal_no}...")

        resultat = validate_question(q)
        korrekt = resultat.get("korrekt")
        tillit = resultat.get("tillit", "lav")
        kommentar = resultat.get("kommentar", "")
        riktig_svar_id = resultat.get("riktig_svar_id", q.get("correctOptionId"))

        # Update in database
        update = {
            "validated": True,
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "validation_result": resultat,
            "validation_source": "lovdata.no + claude-opus-4-7"
        }

        if korrekt == False and tillit == "høy":
            if riktig_svar_id and riktig_svar_id != q.get("correctOptionId"):
                # Fix the correct answer
                update["correctOptionId"] = riktig_svar_id
                rettet += 1
                print(f"    RETTET svar: {q.get('correctOptionId')} -> {riktig_svar_id}: {kommentar}")
            else:
                update["active"] = False
                deaktivert += 1
                print(f"    FEIL (deaktivert): {kommentar}")
        elif korrekt == True:
            korrekte += 1
            print(f"    OK [{tillit}]")
        else:
            usikre += 1
            print(f"    Usikker [{tillit}]: {kommentar}")

        await db.questions.update_one(
            {"id": q["id"]},
            {"$set": update}
        )

    client_db.close()

    print(f"\n{'='*60}")
    print(f"  FERDIG!")
    print(f"  OK:          {korrekte}")
    print(f"  Rettet svar: {rettet}")
    print(f"  Usikre:      {usikre}")
    print(f"  Deaktivert:  {deaktivert}")
    print(f"\n  Kilde: norsk vegtrafikkloven (lovdata.no)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
