"""
seed_studiebok.py — Insert 6 Studiebok chapters into MongoDB.
Run once: python seed_studiebok.py
"""
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent / ".env")

from motor.motor_asyncio import AsyncIOMotorClient

mongo_url = os.environ["MONGO_URL"]
db_name   = os.environ["DB_NAME"]

CHAPTERS = [
    {
        "order": 1,
        "icon": "🚦",
        "title_no": "Kapittel 1 — Trafikkregler",
        "content_no": (
            '<p>I Norge gjelder <strong>høyrekjøring</strong> — du holder til høyre på veien og møter trafikk fra venstre side.</p>'
            '<p><strong>Vikeplikt:</strong> Som hovedregel har du vikeplikt for trafikk fra høyre, med mindre skilt eller oppmerking sier noe annet.</p>'
            '<ul>'
            '<li>Stopp alltid for rødt lys</li>'
            '<li>Gult lys = forbered deg på stopp</li>'
            '<li>Grønt lys = kjør, men pass på fotgjengere</li>'
            '<li>Blinkende gult = sakte, vær forsiktig</li>'
            '</ul>'
            '<div class="study-tip"><strong>Tips:</strong> I rundkjøring har trafikk inne i rundkjøringen forkjørsrett. Du må gi vikeplikt når du kjører inn.</div>'
        ),
    },
    {
        "order": 2,
        "icon": "⏱️",
        "title_no": "Kapittel 2 — Fartsgrenser",
        "content_no": (
            '<p>Norges standard fartsgrenser:</p>'
            '<ul>'
            '<li><strong>50 km/t</strong> — tettbygd strøk (by og bygd)</li>'
            '<li><strong>80 km/t</strong> — landevei utenfor tettbygd strøk</li>'
            '<li><strong>110 km/t</strong> — motorvei med midtdeler</li>'
            '<li><strong>30 km/t</strong> — skolevei, lekeplasser, boliggater</li>'
            '</ul>'
            '<p>Fartsgrensen kan senkes eller heves av skilt. Husk at fartsgrensen er en <strong>maksimumsgrense</strong> — du skal alltid kjøre etter forholdene.</p>'
            '<div class="study-tip"><strong>Tips:</strong> Ved dårlig vær, mørke eller glatt vei skal du redusere farten selv om du holder lovlig hastighet.</div>'
        ),
    },
    {
        "order": 3,
        "icon": "🪧",
        "title_no": "Kapittel 3 — Trafikkskilt",
        "content_no": (
            '<p>Norske trafikkskilt er delt i fire grupper:</p>'
            '<ul>'
            '<li><strong>Forbudsskilt</strong> — røde, runde. Forbyr noe (f.eks. parkering, innkjøring)</li>'
            '<li><strong>Påbudsskilt</strong> — blå, runde. Påbyr noe (f.eks. kjøreretning)</li>'
            '<li><strong>Opplysningsskilt</strong> — blå, firkantede. Gir informasjon</li>'
            '<li><strong>Advarselsskilt</strong> — gule/hvite, trekantede. Varsler om fare</li>'
            '</ul>'
            '<div class="study-tip"><strong>Tips:</strong> En rød trekant med utropstegn betyr generell advarsel om fare. Vær ekstra forsiktig.</div>'
        ),
    },
    {
        "order": 4,
        "icon": "🍺",
        "title_no": "Kapittel 4 — Alkohol og rus",
        "content_no": (
            '<p>Norge har <strong>strenge regler</strong> mot kjøring i ruspåvirket tilstand:</p>'
            '<ul>'
            '<li>Promillegrense: <strong>0,2 promille</strong></li>'
            '<li>Under 0,5 promille: bot og kjøreforbud</li>'
            '<li>Over 0,5 promille: bot + betinget fengsel</li>'
            '<li>Over 1,2 promille: ubetinget fengsel</li>'
            '</ul>'
            '<p>Politiet kan stoppe enhver bilist og ta alkotest uten grunn.</p>'
            '<div class="study-tip"><strong>Tips:</strong> Alkohol er ikke det eneste som gir promillestraff — narkotika og visse medisiner teller også.</div>'
        ),
    },
    {
        "order": 5,
        "icon": "🦺",
        "title_no": "Kapittel 5 — Sikkerhet og verneutstyr",
        "content_no": (
            '<p><strong>Setebelte</strong> er påbudt for alle i kjøretøyet, både foran og bak. Sjåfør er ansvarlig for at passasjerer under 15 år bruker setebelte eller godkjent sikringsutstyr.</p>'
            '<ul>'
            '<li>Barn under 4 år: godkjent barnestol</li>'
            '<li>Barn 4–135 cm: barnesete eller bilstol</li>'
            '<li>Mobiltelefon uten håndfri er forbudt under kjøring</li>'
            '<li>Refleks og varseltrekant i bilen er krav ved uhell</li>'
            '</ul>'
            '<div class="study-tip"><strong>Tips:</strong> Sett alltid på varselblink og sett ut varseltrekant 50–150 m bak bilen ved stopp på vei.</div>'
        ),
    },
    {
        "order": 6,
        "icon": "🅿️",
        "title_no": "Kapittel 6 — Parkering",
        "content_no": (
            '<p>Generelle parkeringsregler i Norge:</p>'
            '<ul>'
            '<li>Ikke parker nærmere enn <strong>5 m</strong> fra kryss eller avkjørsel</li>'
            '<li>Ikke parker foran inn- og utkjøring</li>'
            '<li>Ikke parker på gangvei, sykkelvei, eller fortau (med mindre tillatt)</li>'
            '<li>Stoppforbud-skilt = ingen stopp i det hele tatt</li>'
            '<li>Parkeringsforbud-skilt = kortstopp for av/påstigning er OK</li>'
            '</ul>'
            '<div class="study-tip"><strong>Tips:</strong> Gul stripe langs kantstein betyr parkeringsforbud. Hvit stripe betyr parkeringsregulering.</div>'
        ),
    },
]


async def main():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    col = db.studiebok_chapters

    # Drop existing so re-running is idempotent
    await col.drop()

    now = datetime.now(timezone.utc).isoformat()
    docs = [{**ch, "created_at": now} for ch in CHAPTERS]
    result = await col.insert_many(docs)
    print(f"Inserted {len(result.inserted_ids)} studiebok chapters.")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
