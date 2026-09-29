/**
 * Kategorinavn — lokal ordbok for frontenden.
 *
 * Databasen lagrer kategorier som rå nøkler ('Right of Way',
 * 'fart_og_bremsing'). Slike strenger skal ALDRI vises til eleven. Alt som
 * rendres går gjennom `categoryLabel()`, som er Fail-Stop: finnes ingen
 * oversettelse på elevens språk, returneres `null` og kalleren skjuler
 * elementet. Ingen fallback til rå nøkkel, ingen fallback til norsk.
 *
 * Thai- og norsk-verdiene er hentet ordrett fra `app/categories.tsx` slik at
 * dashbordet viser nøyaktig samme navn som resten av appen.
 */

import { Lang, isPureForLang } from './i18n';

export const CATEGORY_LABELS: Record<string, Record<Lang, string>> = {
  'Speed Limits':             { no: 'Fartsgrenser',      th: 'ขีดจำกัดความเร็ว',   en: 'Speed Limits' },
  'Road Rules':               { no: 'Trafikkregler',     th: 'กฎจราจร',            en: 'Road Rules' },
  'Traffic Signs':            { no: 'Trafikkskilt',      th: 'ป้ายจราจร',          en: 'Traffic Signs' },
  'Right of Way':             { no: 'Vikeplikt',         th: 'การให้ทาง',          en: 'Right of Way' },
  'Traffic Rules':            { no: 'Grunnregler',       th: 'กฎพื้นฐาน',          en: 'Traffic Rules' },
  'Situations':               { no: 'Situasjoner',       th: 'สถานการณ์',          en: 'Situations' },
  'Safety':                   { no: 'Sikkerhet',         th: 'ความปลอดภัย',        en: 'Safety' },
  'Driving Conditions':       { no: 'Kjøreforhold',      th: 'สภาพการขับขี่',      en: 'Driving Conditions' },
  'Road Conditions':          { no: 'Veiforhold',        th: 'สภาพถนน',            en: 'Road Conditions' },
  'Pedestrians and Cyclists': { no: 'Gående/Syklister',  th: 'คนเดิน/จักรยาน',     en: 'Pedestrians & Cyclists' },
  'Vehicle Knowledge':        { no: 'Kjøretøy',          th: 'ความรู้รถ',          en: 'Vehicle Knowledge' },
  'Environment and Economy':  { no: 'Miljø/Økonomi',     th: 'สิ่งแวดล้อม',        en: 'Environment & Economy' },
  'Alcohol':                  { no: 'Rus',               th: 'แอลกอฮอล์',          en: 'Alcohol & Drugs' },
  'Highway':                  { no: 'Motorvei',          th: 'ทางหลวง',            en: 'Highway Driving' },
  'Overtaking':               { no: 'Forbikjøring',      th: 'การแซง',             en: 'Overtaking' },
  'Intersections':            { no: 'Kryss',             th: 'ทางแยก',             en: 'Intersections' },
  'Parking':                  { no: 'Parkering',         th: 'ที่จอดรถ',           en: 'Parking' },
  'Lights':                   { no: 'Lys',               th: 'ไฟ',                 en: 'Lights' },
  'Tires':                    { no: 'Dekk',              th: 'ยาง',                en: 'Tires' },
  'Pedestrians':              { no: 'Fotgjengere',       th: 'คนเดินเท้า',         en: 'Pedestrians' },
  'Environment':              { no: 'Miljø',             th: 'สิ่งแวดล้อม',        en: 'Environment' },
  // Snake_case-nøkler fra innholdspakkene (backend/content_packs/*)
  'fart_og_bremsing':         { no: 'Fart og bremsing',  th: 'ความเร็วและการเบรก', en: 'Speed and Braking' },
};

/**
 * Rå kategorinøkler sortert lengst først, slik at 'Environment and Economy'
 * treffer før 'Environment' når vi bytter ut navn inni en setning.
 */
const RAW_KEYS_BY_LENGTH = Object.keys(CATEGORY_LABELS).sort((a, b) => b.length - a.length);

function escapeForRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Oversetter én rå kategorinøkkel.
 * Fail-Stop: returnerer `null` for ukjent kategori eller manglende
 * oversettelse på `lang`. Kalleren skjuler da raden/kortet.
 */
export function categoryLabel(raw: string | null | undefined, lang: Lang): string | null {
  if (!raw) return null;
  const label = CATEGORY_LABELS[raw.trim()]?.[lang];
  return typeof label === 'string' && label.trim().length > 0 ? label : null;
}

/**
 * Bytter ut rå kategorinavn som backend har interpolert inn i en ferdig
 * setning (f.eks. coaching-meldingen «คุณยังอ่อนในหมวด: Right of Way»).
 *
 * Fail-Stop i to trinn:
 *   1. Nevnes en kategori fra `knownRawCategories` som vi ikke kan oversette,
 *      forkastes hele teksten (`null`).
 *   2. På thai forkastes teksten også hvis den fortsatt inneholder latinske
 *      bokstaver etter utbytting — da har noe annet lekket gjennom.
 */
export function localizeCategoryMentions(
  text: string,
  lang: Lang,
  knownRawCategories: string[] = [],
): string | null {
  if (typeof text !== 'string' || text.trim().length === 0) return null;

  let out = text;

  for (const raw of RAW_KEYS_BY_LENGTH) {
    if (!out.includes(raw)) continue;
    const label = categoryLabel(raw, lang);
    if (!label) return null;
    out = out.replace(new RegExp(escapeForRegExp(raw), 'g'), label);
  }

  // Kategorier som finnes i databasen, men ikke i ordboken over.
  // Nøkler vi kjenner er allerede byttet ut; står de igjen, er det fordi
  // etiketten er identisk med nøkkelen (engelsk: 'Right of Way'), og det er
  // helt riktig tekst — ikke en lekkasje.
  for (const raw of knownRawCategories) {
    if (!raw || CATEGORY_LABELS[raw.trim()]) continue;
    if (out.includes(raw)) return null;
  }

  return isPureForLang(out, lang) ? out : null;
}
