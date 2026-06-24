import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient

# Reconfigure stdout for UTF-8 in Windows console
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv('backend/.env')

if 'MONGO_URL' not in os.environ:
    print("Error: MONGO_URL not found in environment. Make sure to run from project root and backend/.env is populated.")
    sys.exit(1)

client = MongoClient(os.environ['MONGO_URL'])
db = client[os.environ.get('DB_NAME', 'thai2drive')]
col = db['questions']

translations = {
    "b609d469-7b7a-4a29-8b71-e0d7980a0602": {
        "explanation.no": "Michaels regel: Du har vikeplikt FOR trafikk som kommer fra høyre. Lytt! Alle kryss uten skilt krever at du viker for trafikk som kommer fra høyre (høyreregelen)."
    },
    "quiz_speed_14kmh": {
        "question.no": "Du kjører i 14 km/t. Hva er reaksjonslengden?",
        "explanation.no": "Ved 14 km/t er reaksjonslengden ca. 3 meter. Reaksjonslengden øker med farten."
    },
    "quiz_stop_complete": {
        "question.no": "Hva betyr et stoppskilt?",
        "options.1.text.no": "Du kan sakte kjøre gjennom",
        "options.2.text.no": "Du kan bremse mens du kjører gjennom",
        "options.3.text.no": "Du må sjekke og kjøre videre",
        "explanation.no": "Stoppskilt krever fullstendig stopp. Hjulene må være helt stille. Ikke rulling eller sakte kjøring."
    },
    "quiz_solid_line": {
        "question.no": "Hva betyr en heltrukken linje på veien?",
        "options.0.text.no": "Forbudt å kjøre forbi",
        "options.1.text.no": "Tillatt å kjøre forbi",
        "options.2.text.no": "Kjøre sakte",
        "options.3.text.no": "Parkering tillatt",
        "explanation.no": "Heltrukken linje = forbudt. Du kan IKKE kjøre forbi en annen bil. Stiplet linje = tillatt."
    },
    "quiz_dashed_line": {
        "question.no": "Hva betyr en stiplet linje på veien?",
        "options.0.text.no": "Tillatt å kjøre forbi når det er trygt",
        "options.1.text.no": "Forbudt å kjøre forbi",
        "options.2.text.no": "Parkering bare her",
        "options.3.text.no": "Alltid kjøre sakte",
        "explanation.no": "Stiplet linje = tillatt å kjøre forbi. Men du må sjekke at det er trygt før du kjører forbi."
    },
    "quiz_pedestrian_crossing": {
        "question.no": "Du ser et fotgjengerfelt. Hva gjør du?",
        "options.0.text.no": "Kjøre sakte og være oppmerksom på fotgjengere",
        "options.1.text.no": "Kjøre raskt gjennom",
        "options.2.text.no": "Tute for å se fotgjengerne",
        "options.3.text.no": "Ikke stoppe og kjøre gjennom",
        "explanation.no": "Fotgjengerfelt = fotgjengere har prioritet. Du må stoppe om de krysser, eller kjøre sakte og være oppmerksom."
    },
    "quiz_roundabout_enter": {
        "question.no": "Du skal inn i en rundkjøring. Hva gjør du?",
        "options.0.text.no": "Vike for biler inne i rundkjøringen",
        "options.1.text.no": "Kjøre inn først",
        "options.2.text.no": "Tute for å varsle andre biler",
        "options.3.text.no": "Stoppe og vente hver gang",
        "explanation.no": "Rundkjøring: biler inne i rundkjøringen har prioritet. Du må vike og sjekke før du kjører inn."
    },
    "quiz_right_of_way_left_turn": {
        "question.no": "Du skal svinge til venstre. En bil kjører imot deg. Hvem har prioritet?",
        "options.0.text.no": "Bilen som kjører imot deg har prioritet",
        "options.1.text.no": "Du har prioritet fordi du svinger",
        "options.2.text.no": "Dere kan kjøre samtidig",
        "options.3.text.no": "Det avhenger av fartsgrensen",
        "explanation.no": "Når du svinger til venstre, må du vike for biler som kjører imot deg. De har prioritet!"
    },
    "quiz_yellow_light": {
        "question.no": "Lyset skifter til gult. Hva skal du gjøre?",
        "options.0.text.no": "Forbered deg på å bremse — rødt lys kommer etterpå",
        "options.1.text.no": "Akselerere og kjøre gjennom",
        "options.2.text.no": "Tute på alle biler",
        "options.3.text.no": "Rygge straks",
        "explanation.no": "Gult lys = forberedelsessignal. Rødt lys kommer etterpå. Du skal bremse eller være klar til å stoppe."
    },
    "quiz_braking_distance_80kmh": {
        "question.no": "Du kjører i 80 km/t. Hva er omtrentlig bremselengde?",
        "explanation.no": "Ved 80 km/t er bremselengden omtrent 60 meter. Høyere fart = lengre bremselengde!"
    },
    "quiz_right_from_right": {
        "question.no": "Hva er Michaels første regel?",
        "options.0.text.no": "Vikeplikt fra høyre — bilen fra høyre har prioritet",
        "options.1.text.no": "Vikeplikt fra venstre",
        "options.2.text.no": "Vikeplikt for møtende",
        "options.3.text.no": "Vikeplikt bakfra",
        "explanation.no": "Michaels første regel: I Norge gjelder vikeplikt fra høyre! Ikke fra venstre som i Thailand. Bilen fra høyre har prioritet!"
    },
    "quiz_speed_norway_vs_thailand": {
        "question.no": "50 km/t i Norge er?",
        "options.0.text.no": "En vanlig normal fart i byer",
        "options.1.text.no": "En fartsgrense på motorvei",
        "options.2.text.no": "For sakte for Norge",
        "options.3.text.no": "Ikke lovlig i Norge",
        "explanation.no": "50 km/t er typisk fartsgrense i norske byer. I Thailand var 50 km/t trygt. I Norge kan 50 km/t være en felle!"
    },
    "quiz_distance_between_cars": {
        "question.no": "Hva er riktig avstand mellom biler i Norge?",
        "options.0.text.no": "Minst 2 sekunders kjøretid",
        "options.1.text.no": "Minst 1 sekunds kjøretid",
        "options.2.text.no": "Minst 5 sekunders kjøretid",
        "options.3.text.no": "Ikke nødvendig, kjør tett",
        "explanation.no": "I Norge skal det være minst 2 sekunders avstand mellom biler. Det vil si at når bilen foran passerer et punkt, bør du passere det samme punktet etter minst 2 sekunder."
    },
    "quiz_rain_visibility": {
        "question.no": "Du kjører i regnvær. Hva skal du gjøre?",
        "options.0.text.no": "Slå på lysene, redusere farten, øke avstanden",
        "options.1.text.no": "Kjøre i normal fart",
        "options.2.text.no": "Slå av lysene fordi regnet er kraftig",
        "options.3.text.no": "Tute på alle biler",
        "explanation.no": "Regnvær: Lys + redusert fart + økt avstand. Du ser dårlig, andre ser deg dårlig, og veien er glatt."
    },
    "quiz_night_driving": {
        "question.no": "Du kjører om natten. Hva skal du gjøre?",
        "options.0.text.no": "Slå på billyktene, redusere farten, være oppmerksom",
        "options.1.text.no": "Kjøre som vanlig — natten er trygg",
        "options.2.text.no": "Bruke bare fjernlys",
        "options.3.text.no": "Slå av lysene og se i mørket",
        "explanation.no": "Mørkekjøring: Slå på lysene, redusere farten, være oppmerksom. Sikten er dårlig, og fotgjengere kan være vanskelige å se."
    },
    "quiz_ice_conditions": {
        "question.no": "Veien er isete. Hva skal du gjøre?",
        "options.0.text.no": "Kjøre veldig sakte, bruke lavt gir, øke avstanden",
        "options.1.text.no": "Kjøre i normal fart",
        "options.2.text.no": "Akselerere og 'teste' isen",
        "options.3.text.no": "Bruke håndbrekket for å kontrollere",
        "explanation.no": "Is = ekstrem fare! Kjør veldig sakte, bruk lavt gir, øk avstanden, vær oppmerksom. Biler sklir lett!"
    },
    "quiz_emergency_stop": {
        "question.no": "Nødbremsing: Hva skal du gjøre?",
        "options.0.text.no": "Bremse hardt, holde styringen fast, komme deg trygt av veien",
        "options.1.text.no": "Bremse langsomt og sakte",
        "options.2.text.no": "Akselerere for å unngå situasjonen",
        "options.3.text.no": "Svinge til venstre med en gang",
        "explanation.no": "Nødbremsing: Brems HARDT, hold styringen fast, sving unna til et trygt sted. Ikke sving brått — det kan være farlig!"
    },
    "quiz_merge_from_side": {
        "question.no": "Du skal flette inn på motorvei fra påkjøringsrampe. Hva gjør du?",
        "options.0.text.no": "Akselerere for å få samme fart som trafikken, sjekke speil og blindsone, flette rolig inn",
        "options.1.text.no": "Kjøre inn uten å sjekke",
        "options.2.text.no": "Stoppe på påkjøringsrampen og vente",
        "options.3.text.no": "Kjøre mot trafikken for å flette",
        "explanation.no": "Fletting: Akselerer til samme fart, sjekk speil og blindsone, flett rolig inn. Stopp aldri på påkjøringsrampen!"
    },
    "quiz_authority_pyramid": {
        "question.no": "Hva er autoritetspyramiden i Norge?",
        "options.0.text.no": "Lovverk > politimann > trafikkskilt > gjøre som alle andre",
        "options.1.text.no": "Gjøre som politimannen sier, uansett loven",
        "options.2.text.no": "Gjøre som alle andre, uansett skilt",
        "options.3.text.no": "Gjøre som du vil, uten regler",
        "explanation.no": "Michaels autoritetspyramide: 1. Lovverk (øverst), 2. Politimann, 3. Trafikkskilt, 4. Gjøre som andre (lavest). I Thailand er det omvendt!"
    },
    "quiz_horn_when": {
        "question.no": "Når skal du bruke hornet (tuten)?",
        "options.0.text.no": "Bare når det er fare eller for å advare",
        "options.1.text.no": "Tute hver gang du blir irritert",
        "options.2.text.no": "Tute på alle fotgjengere",
        "options.3.text.no": "Ikke bruke hornet, det er ulovlig",
        "explanation.no": "Hornet skal bare brukes til å avverge fare eller advare — ikke til å uttrykke irritasjon. I Norge brukes hornet for sikkerhet, ikke til sosial kommunikasjon!"
    },
    "quiz_fog_lights": {
        "question.no": "Når skal du bruke tåkelys (fog lights)?",
        "options.0.text.no": "Bare når det er tåke eller veldig dårlig sikt",
        "options.1.text.no": "Alltid når du kjører",
        "options.2.text.no": "Bare om natten",
        "options.3.text.no": "Aldri — det er ikke lovlig",
        "explanation.no": "Tåkelys skal bare brukes ved tåke eller svært dårlig sikt. De skal ikke brukes om natten uten tåke."
    },
    "quiz_parking_hill": {
        "question.no": "Du parkerer i en bakke. Hva skal du gjøre?",
        "options.0.text.no": "Bruke håndbrekk, svinge hjulene inn mot kanten, sette bilen i gir",
        "options.1.text.no": "Bare slå av motoren",
        "options.2.text.no": "Holde bremsepedalen inne mens du er borte",
        "options.3.text.no": "Ikke bruke håndbrekk, det er farlig",
        "explanation.no": "Parkering i bakke: Håndbrekk + svinge hjulene mot kanten + sette i gir. Dette sikrer at bilen ikke ruller av gårde!"
    },
    "quiz_school_bus_stop": {
        "question.no": "Du ser en skolebuss som stopper. Hva gjør du?",
        "options.0.text.no": "Stoppe og vente til bussen kjører videre",
        "options.1.text.no": "Kjøre forsiktig forbi bussen",
        "options.2.text.no": "Tute til bussen beveger seg",
        "options.3.text.no": "Kjøre som normalt, barna er inne i bussen",
        "explanation.no": "Skolebuss: Når bussen stopper, skal barn gå av eller på. Du må stoppe og vente. Barna har prioritet!"
    },
    "quiz_bicycle_space": {
        "question.no": "Du ser en syklist foran deg. Hva gjør du?",
        "options.0.text.no": "Gi god avstand, ikke kjør forbi for tett, vær oppmerksom",
        "options.1.text.no": "Tute for å få syklisten av veien",
        "options.2.text.no": "Kjøre forbi tett og raskt",
        "options.3.text.no": "Stoppe rett bak syklisten",
        "explanation.no": "Syklist: Gi minst 1,5 meter avstand når du kjører forbi. Syklisten kan velte eller svinge brått. Vær oppmerksom!"
    },
    "quiz_thai_vs_norway_culture": {
        "question.no": "Hva er en stor kulturforskjell i kjørestil mellom Thailand og Norge?",
        "options.0.text.no": "Thailand: relasjonell og forhandling. Norge: regelbasert og disiplin.",
        "options.1.text.no": "Thailand har bedre veier enn Norge",
        "options.2.text.no": "Norge bruker ikke trafikklys",
        "options.3.text.no": "Thailand og Norge har samme regler",
        "explanation.no": "Thailand: Kjøring er relasjonell — man forhandler, viker for makt. Norge: Kjøring er regelbasert — lover, disiplin og respekt for loven. Stor kulturforskjell!"
    },
    "quiz_glossary_vikeplikt": {
        "question.no": "Hva er 'vikeplikt'?",
        "options.0.text.no": "Å vike (gi prioritet) for en annen bil i bestemte situasjoner",
        "options.1.text.no": "Å kjøre fort",
        "options.2.text.no": "Å parkere på siden av veien",
        "options.3.text.no": "Å gå til fots",
        "explanation.no": "Vikeplikt = regel for forkjørsrett. I visse situasjoner må en bil vike for en annen. Eksempel: man har vikeplikt for biler fra høyre."
    },
    "quiz_glossary_forkjøring": {
        "question.no": "Hva er 'forbikjøring'?",
        "options.0.text.no": "Å kjøre forbi en annen bil",
        "options.1.text.no": "Å bremse hardt",
        "options.2.text.no": "Å parkere",
        "options.3.text.no": "Å svinge til høyre",
        "explanation.no": "Forbikjøring = å kjøre forbi en annen bil. Du kjører forbi på siden av en annen bil. Heltrukken linje = forbudt, stiplet linje = tillatt."
    },
    "quiz_glossary_bremselengde": {
        "question.no": "Hva er 'bremselengde'?",
        "options.0.text.no": "Avstanden bilen kjører fra du trykker på bremsepedalen til bilen har stoppet helt",
        "options.1.text.no": "Tiden det tar å bremse",
        "options.2.text.no": "Avstanden mellom biler",
        "options.3.text.no": "Farten man holder på motorvei",
        "explanation.no": "Bremselengde = avstanden fra du begynner å bremse til full stopp. Høyere fart = lengre bremselengde. Ved 50 km/t er bremselengden ca. 27 meter."
    },
    "quiz_glossary_reaktidslengde": {
        "question.no": "Hva er 'reaksjonslengde'?",
        "options.0.text.no": "Avstanden bilen kjører mens du oppfatter faren og trykker på bremsepedalen",
        "options.1.text.no": "Tiden det tar å tenke",
        "options.2.text.no": "Bremselengden på glatt vei",
        "options.3.text.no": "Farten i en bakke",
        "explanation.no": "Reaksjonslengde = avstanden bilen kjører mens du reagerer (normalt 1 sekund). Ved 50 km/t er reaksjonslengden ca. 14 meter. Du tenker, ser faren og flytter foten til bremsen. Bilen kjører videre i denne tiden!"
    },
    "quiz_glossary_stopplengde": {
        "question.no": "Hva er 'stoppelengde'?",
        "options.0.text.no": "Reaksjonslengde + bremselengde = total avstand fra du ser en fare to du står stille",
        "options.1.text.no": "Bare bremselengden",
        "options.2.text.no": "Bare reaksjonslengden",
        "options.3.text.no": "Avstanden mellom biler",
        "explanation.no": "Stoppelengde = Reaksjonslengde (14m) + bremselengde (27m) = 41 meter totalt ved 50 km/t. Michael sier: det er livsfarlig å ikke kunne disse tallene!"
    }
}

count = 0
for q_id, fields in translations.items():
    doc = col.find_one({"id": q_id})
    if not doc:
        print(f"Warning: Question ID '{q_id}' not found in database!")
        continue
        
    set_fields = {}
    for key, val in fields.items():
        set_fields[key] = val
        
    r = col.update_one({"id": q_id}, {"$set": set_fields})
    if r.modified_count > 0:
        count += 1
        print(f"Updated {q_id}")
    else:
        print(f"Skipped/No Change for {q_id}")

print(f"\nSuccessfully migrated {count} questions in MongoDB.")
