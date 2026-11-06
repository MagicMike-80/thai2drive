import re

path = 'backend/studybook_web.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace thumb_vikeplikt placeholders in CH07
replacements = {
    '("ch07_park_001", "1", "CH07-PARK-001", "Forskjellen på stans og parkering", "Definere stans som av/påstigning vs enhver annen hensetting", "bygateperspektiv", "Ulovlig stans som hindrer trafikkflyt", "bil ved fortau", "bygate", "kantstein", "stans vs parkering", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "")':
    '("ch07_park_001", "1", "CH07-PARK-001", "Forskjellen på stans og parkering", "Definere stans som av/påstigning vs enhver annen hensetting", "bygateperspektiv", "Ulovlig stans som hindrer trafikkflyt", "bil ved fortau", "bygate", "kantstein", "stans vs parkering", "/api/assets/studybook/bb_s121_hva_er_parkering_stans.png", "")',

    '("ch07_park_002", "2", "CH07-PARK-002", "Skilt 370 (Stans forbudt) med rødt kryss", "Forklare at skilt 370 forbyr all stans selv i få sekunder", "gateperspektiv", "Misforståelse av at raskt ærend er tillatt ved stansforbud", "bil og skilt 370", "bygate", "skilt 370 rødt kryss", "absolutt stansforbud", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "ch07_par_001")':
    '("ch07_park_002", "2", "CH07-PARK-002", "Skilt 370 (Stans forbudt) med rødt kryss", "Forklare at skilt 370 forbyr all stans selv i få sekunder", "gateperspektiv", "Misforståelse av at raskt ærend er tillatt ved stansforbud", "bil og skilt 370", "bygate", "skilt 370 rødt kryss", "absolutt stansforbud", "/api/assets/studybook/skilt_370_stans_forbudt.jpg", "ch07_par_001")',

    '("ch07_par_001", "2p", "CH07-PAR-001", "Skilt 372 (Parkering forbudt) med én strek", "Sammenligne skilt 372 som tillater kort av- og påstigning", "delt gateperspektiv", "Forveksling mellom skilt 370 og skilt 372", "bil og skilt 372", "bygate", "skilt 372 en strek", "parkering forbudt tillatt stans", "/api/assets/thumbs/thumb_vikeplikt_7_2a.jpg", "ch07_park_002")':
    '("ch07_par_001", "2p", "CH07-PAR-001", "Skilt 372 (Parkering forbudt) med én strek", "Sammenligne skilt 372 som tillater kort av- og påstigning", "delt gateperspektiv", "Forveksling mellom skilt 370 og skilt 372", "bil og skilt 372", "bygate", "skilt 372 en strek", "parkering forbudt tillatt stans", "/api/assets/studybook/skilt_372_parkering_forbudt.jpg", "ch07_park_002")',

    '("ch07_park_003", "3", "CH07-PARK-003", "Hvor er det alltid forbudt å stanse?", "Lære steder med generelt stansforbud: Gangfelt, kurve, tunnel, motorvei", "oversiktsperspektiv", "Tildekking av sikt ved gangfelt og kryss", "bil nær gangfelt", "bygate", "gangfelt og skilt", "generelle forbudssoner", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "")':
    '("ch07_park_003", "3", "CH07-PARK-003", "Hvor er det alltid forbudt å stanse?", "Lære steder med generelt stansforbud: Gangfelt, kurve, tunnel, motorvei", "oversiktsperspektiv", "Tildekking av sikt ved gangfelt og kryss", "bil nær gangfelt", "bygate", "gangfelt og skilt", "generelle forbudssoner", "/api/assets/studybook/bb_s122_forbud_stanse_a_d.png", "")',

    '("ch07_park_004", "4", "CH07-PARK-004", "Road Check stans og parkering", "Teste elevens kunnskap om parkeringsregler og skilt", "førerperspektiv", "Feilplassering som utløser bot og fare for myke trafikanter", "bil ved veikant", "bygate", "skilt og merking", "presis regelkontroll", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "")':
    '("ch07_park_004", "4", "CH07-PARK-004", "Road Check stans og parkering", "Teste elevens kunnskap om parkeringsregler og skilt", "førerperspektiv", "Feilplassering som utløser bot og fare for myke trafikanter", "bil ved veikant", "bygate", "skilt og merking", "presis regelkontroll", "/api/assets/studybook/bb_s123_forbud_stanse_parkere.png", "")',

    '("ch07_park_005", "5", "CH07-PARK-005", "5-metersregelen ved kryss og gangfelt", "Vise hvordan 5 meter måles fra kurvens startpunkt", "måleperspektiv", "Parkering for nær kryss som blokkerer sikten", "bil ved kryss", "kryss og gangfelt", "fortauskant og 5m markering", "5 metersregelen", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "ch07_par_002")':
    '("ch07_park_005", "5", "CH07-PARK-005", "5-metersregelen ved kryss og gangfelt", "Vise hvordan 5 meter måles fra kurvens startpunkt", "måleperspektiv", "Parkering for nær kryss som blokkerer sikten", "bil ved kryss", "kryss og gangfelt", "fortauskant og 5m markering", "5 metersregelen", "/api/assets/studybook/gangfelt_fem_meter.png", "ch07_par_002")',

    '("ch07_par_002", "5p", "CH07-PAR-002", "Korrekt måling av 5 meter fra kurve", "Presisere oppmåling fra der fortauskanten begynner å runde", "nært perspektiv", "Feilmåling som fører til trafikkfelle og bot", "oppmålingsgrafikk", "kryss", "oppmerket kurveradius", "korrekt 5m målepunkt", "/api/assets/thumbs/thumb_vikeplikt_7_2a.jpg", "ch07_park_005")':
    '("ch07_par_002", "5p", "CH07-PAR-002", "Korrekt måling av 5 meter fra kurve", "Presisere oppmåling fra der fortauskanten begynner å runde", "nært perspektiv", "Feilmåling som fører til trafikkfelle og bot", "oppmålingsgrafikk", "kryss", "oppmerket kurveradius", "korrekt 5m målepunkt", "/api/assets/studybook/bb_s124_fem_meters_regelen.png", "ch07_park_005")',

    '("ch07_park_006", "6", "CH07-PARK-006", "Oppsummering og trygg parkering", "Oppsummere stans- og parkeringsregler og feire fullført kapittel", "utendørsperspektiv", "Manglende sikring av bil mot rulling i bakke", "parkert bil", "parkeringsplass", "p-skilt og oppmerking", "trygg og lovlig parkering", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "")':
    '("ch07_park_006", "6", "CH07-PARK-006", "Oppsummering og trygg parkering", "Oppsummere stans- og parkeringsregler og feire fullført kapittel", "utendørsperspektiv", "Manglende sikring av bil mot rulling i bakke", "parkert bil", "parkeringsplass", "p-skilt og oppmerking", "trygg og lovlig parkering", "/api/assets/studybook/bb_s126_parkering_forkjorsvei.png", "")'
}

count = 0
for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new)
        count += 1
    else:
        print('Could not find:', old[:60])

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print(f'Done! Replaced {count} entries in {path}')
