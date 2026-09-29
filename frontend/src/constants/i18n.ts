/**
 * Språkrenhet — delte hjelpere (Fail-Stop).
 *
 * Grunnregelen i Thai2Drive er 100 % språkisolasjon: er thai valgt, skal
 * eleven aldri se norsk, engelsk eller rå databasestrenger. Derfor finnes
 * det ingen fallback-kjeder her (`x_th || x_no`). Mangler en oversettelse,
 * returnerer hjelperne `null`, og komponenten skal enten skjule elementet
 * eller vise `missingNotice(lang)` — som alltid er på elevens eget språk.
 */

export type Lang = 'no' | 'th' | 'en';

export const LANGS: Lang[] = ['no', 'th', 'en'];

/** Standardspråket i appen (`appStore.language` initialiseres til 'th'). */
export const DEFAULT_LANG: Lang = 'th';

/**
 * Snevrer `appStore.language` (typet som `string`) til en gyldig `Lang`.
 * Ukjente verdier faller til `DEFAULT_LANG` slik at vi aldri havner i en
 * tilstand der ingen ordbok finnes og UI-et renderer tomt.
 */
export function asLang(language: string | null | undefined): Lang {
  return LANGS.includes(language as Lang) ? (language as Lang) : DEFAULT_LANG;
}

/**
 * Nøytral feilmelding på elevens eget språk. Brukes når en tekst mangler
 * og elementet ikke kan skjules uten at layouten blir uforståelig.
 */
const MISSING_NOTICE: Record<Lang, string> = {
  no: 'Mangler norsk tekst her.',
  th: 'ยังไม่มีคำแปลภาษาไทยสำหรับส่วนนี้',
  en: 'No English text available here.',
};

export function missingNotice(lang: Lang): string {
  return MISSING_NOTICE[lang];
}

/**
 * Fail-Stop-oppslag i en oversettelsestabell.
 * Returnerer `null` — aldri nøkkelen, aldri et annet språk — når teksten
 * mangler eller er tom, slik at kalleren tar et bevisst valg.
 */
export function tr(dict: Record<string, string> | undefined, key: string): string | null {
  const value = dict?.[key];
  return typeof value === 'string' && value.trim().length > 0 ? value : null;
}

/**
 * Sant hvis teksten inneholder latinske bokstaver.
 *
 * Brukes som siste skanse på thai: rene thai-strenger inneholder kun
 * thai-tegn, tall, tegnsetting og emoji. Dukker det opp latinske bokstaver
 * i thai-modus, er det en lekkasje (typisk en rå kategori fra databasen
 * interpolert inn i en backend-generert setning), og teksten skal droppes.
 */
export function hasLatinLetters(text: string): boolean {
  return /[A-Za-zÆØÅæøå]/.test(text);
}

/** Sant hvis teksten inneholder thai-tegn. */
export function hasThaiLetters(text: string): boolean {
  return /[฀-๿]/.test(text);
}

/**
 * Sant hvis teksten er trygg å vise på det valgte språket.
 *
 * Vakten er symmetrisk på skriftsystem: thai avviser latinske bokstaver,
 * norsk og engelsk avviser thai-tegn. Norsk og engelsk deler alfabet og kan
 * ikke skilles fra hverandre på tegnnivå — der er ordbøkene eneste vern.
 */
export function isPureForLang(text: string, lang: Lang): boolean {
  return lang === 'th' ? !hasLatinLetters(text) : !hasThaiLetters(text);
}
