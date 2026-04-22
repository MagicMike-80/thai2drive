"""
Public marketing website + legal pages for Thai2Drive.
All pages are styled in a unified dark theme matching the mobile app.
Mounted under /api/* so the k8s ingress routes them to the backend.
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

website_router = APIRouter()

# Shared brand assets URL (served by /api/assets)
ICON_URL = "/api/assets/developer-icon-512.png"
HEADER_URL = "/api/assets/developer-header-4096x2304.jpg"
FEATURE_URL = "/api/assets/feature-graphic-1024x500.jpg"

BRAND = "Thai2Drive"
CONTACT_EMAIL = "lexuz.zxc@gmail.com"
LAST_UPDATED = "2. juni 2025"


_BASE_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  background:#0B1226;color:#E2E8F0;line-height:1.6;
  -webkit-font-smoothing:antialiased;min-height:100vh;
}
a{color:#FF9933;text-decoration:none;transition:opacity .2s}
a:hover{opacity:.8}
.container{max-width:1120px;margin:0 auto;padding:0 24px}

/* Nav */
.nav{
  position:sticky;top:0;z-index:50;
  background:rgba(11,18,38,.85);backdrop-filter:blur(12px);
  border-bottom:1px solid rgba(255,255,255,.08);
}
.nav-inner{display:flex;align-items:center;justify-content:space-between;padding:14px 24px;max-width:1120px;margin:0 auto}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;color:#fff}
.brand img{width:36px;height:36px;border-radius:8px}
.brand .t2d{color:#FF9933}
.nav ul{list-style:none;display:flex;gap:24px;align-items:center}
.nav ul a{color:#CBD5E1;font-size:14px;font-weight:500}
.nav ul a:hover{color:#FF9933}
.nav-cta{
  background:#FF9933;color:#0F172A;padding:8px 16px;border-radius:8px;
  font-weight:700;font-size:14px;
}
.nav-cta:hover{opacity:.92}

/* Hero */
.hero{padding:90px 0 80px;text-align:center}
.hero-icon{width:112px;height:112px;border-radius:26px;box-shadow:0 30px 80px rgba(255,153,51,.2)}
.hero h1{
  font-size:clamp(36px,6vw,64px);font-weight:900;letter-spacing:-.02em;
  margin:24px 0 16px;line-height:1.05;color:#fff;
}
.hero h1 span{color:#FF9933}
.hero p{font-size:clamp(16px,2vw,20px);color:#94A3B8;max-width:640px;margin:0 auto}
.hero-badges{display:flex;justify-content:center;gap:16px;margin-top:28px;flex-wrap:wrap}
.badge{
  display:inline-flex;align-items:center;gap:8px;padding:8px 16px;
  background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);
  border-radius:999px;font-size:13px;color:#CBD5E1;
}
.badge .dot{width:8px;height:8px;background:#10B981;border-radius:50%}
.hero-cta{
  display:inline-flex;align-items:center;gap:10px;
  background:#FF9933;color:#0F172A;padding:16px 32px;border-radius:12px;
  font-weight:800;font-size:16px;margin-top:36px;
  box-shadow:0 20px 50px rgba(255,153,51,.25);
}
.hero-cta:hover{transform:translateY(-2px);transition:transform .15s}

/* Flag chips */
.flags{display:inline-flex;gap:10px;margin-top:24px}
.flag{width:40px;height:28px;border-radius:4px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,.3);display:flex;flex-direction:column}
.flag-th div:nth-child(1){background:#A51931;flex:1}
.flag-th div:nth-child(2){background:#F4F5F8;flex:1}
.flag-th div:nth-child(3){background:#2D2A4A;flex:2}
.flag-th div:nth-child(4){background:#F4F5F8;flex:1}
.flag-th div:nth-child(5){background:#A51931;flex:1}
.flag-no{background:#BA0C2F;position:relative}
.flag-no::before,.flag-no::after{content:'';position:absolute;background:#fff}
.flag-no::before{left:0;right:0;top:38%;height:22%}
.flag-no::after{left:22%;top:0;bottom:0;width:22%}
.flag-no .blue,.flag-no .bluev{position:absolute;background:#00205B}
.flag-no .blue{left:0;right:0;top:44%;height:10%}
.flag-no .bluev{left:26%;top:0;bottom:0;width:10%}
.flag-gb{background:#012169;position:relative}
.flag-gb::before,.flag-gb::after{content:'';position:absolute;background:#fff}
.flag-gb::before{left:0;right:0;top:40%;height:20%}
.flag-gb::after{left:40%;top:0;bottom:0;width:20%}
.flag-gb .r1,.flag-gb .r2{position:absolute;background:#C8102E}
.flag-gb .r1{left:0;right:0;top:45%;height:10%}
.flag-gb .r2{left:45%;top:0;bottom:0;width:10%}

/* Sections */
section{padding:72px 0}
.section-head{text-align:center;max-width:640px;margin:0 auto 48px}
.section-head h2{font-size:clamp(28px,4vw,40px);font-weight:800;color:#fff;margin-bottom:12px}
.section-head p{color:#94A3B8;font-size:16px}
.eyebrow{
  display:inline-block;color:#FF9933;font-weight:700;
  font-size:12px;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px;
}

/* Features grid */
.features{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}
.feature{
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);
  padding:28px;border-radius:16px;transition:all .2s;
}
.feature:hover{border-color:rgba(255,153,51,.4);background:rgba(255,153,51,.04);transform:translateY(-2px)}
.feature-icon{
  width:44px;height:44px;border-radius:10px;
  background:rgba(255,153,51,.15);color:#FF9933;
  display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:16px;
}
.feature h3{font-size:17px;font-weight:700;color:#fff;margin-bottom:6px}
.feature p{color:#94A3B8;font-size:14px;line-height:1.55}

/* Pricing */
.pricing{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;max-width:960px;margin:0 auto}
.plan{
  background:rgba(255,255,255,.03);border:1.5px solid rgba(255,255,255,.08);
  padding:28px;border-radius:16px;position:relative;
}
.plan.popular{border-color:#FF9933;background:rgba(255,153,51,.05)}
.ribbon{
  position:absolute;top:-10px;right:20px;background:#FF9933;color:#0F172A;
  font-size:11px;font-weight:800;padding:4px 12px;border-radius:6px;text-transform:uppercase;letter-spacing:.05em;
}
.plan h3{font-size:15px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:.05em}
.price{font-size:40px;font-weight:900;color:#fff;margin:10px 0 4px}
.price small{font-size:14px;color:#94A3B8;font-weight:500}
.plan ul{list-style:none;margin-top:18px}
.plan ul li{padding:6px 0;font-size:14px;color:#CBD5E1;display:flex;gap:8px;align-items:flex-start}
.plan ul li::before{content:'✓';color:#10B981;font-weight:900;flex-shrink:0}

/* CTA band */
.cta-band{
  background:linear-gradient(135deg,rgba(255,153,51,.08),rgba(255,153,51,.02));
  border-top:1px solid rgba(255,153,51,.2);border-bottom:1px solid rgba(255,153,51,.2);
  text-align:center;padding:64px 24px;
}
.cta-band h2{font-size:clamp(24px,3.5vw,36px);color:#fff;font-weight:800;margin-bottom:12px}
.cta-band p{color:#94A3B8;max-width:500px;margin:0 auto 24px}

/* Footer */
footer{padding:48px 0 32px;border-top:1px solid rgba(255,255,255,.06);margin-top:40px}
.footer-inner{display:flex;justify-content:space-between;flex-wrap:wrap;gap:24px;align-items:center}
footer p{color:#64748B;font-size:13px}
.footer-links{display:flex;gap:20px;flex-wrap:wrap}
.footer-links a{color:#94A3B8;font-size:13px}

/* Legal pages */
.legal{padding:60px 24px 80px;max-width:820px;margin:0 auto}
.legal h1{font-size:36px;color:#fff;font-weight:800;margin-bottom:8px}
.legal .meta{color:#64748B;margin-bottom:36px;font-size:13px}
.legal h2{font-size:20px;color:#FF9933;font-weight:700;margin:36px 0 12px}
.legal h3{font-size:16px;color:#fff;font-weight:700;margin:20px 0 8px}
.legal p,.legal li{color:#CBD5E1;margin:8px 0;font-size:15px;line-height:1.7}
.legal ul{margin-left:22px}
.legal strong{color:#fff}
.legal .box{
  background:rgba(255,153,51,.06);border:1px solid rgba(255,153,51,.2);
  padding:16px 20px;border-radius:10px;margin:20px 0;
}

@media (max-width:720px){
  .nav ul{gap:14px;font-size:13px}
  .nav ul li:not(:last-child){display:none}
  section{padding:52px 0}
  .hero{padding:60px 0 56px}
}
"""


def _nav(lang_links=True):
    return f"""
<nav class="nav">
  <div class="nav-inner">
    <a href="/api/website" class="brand">
      <img src="{ICON_URL}" alt="{BRAND}"/>
      <span>Thai<span class="t2d">2</span>Drive</span>
    </a>
    <ul>
      <li><a href="/api/website#features">Funksjoner</a></li>
      <li><a href="/api/website#pricing">Priser</a></li>
      <li><a href="/api/support">Support</a></li>
      <li><a href="/api/privacy">Personvern</a></li>
    </ul>
  </div>
</nav>
"""


def _footer():
    return f"""
<footer>
  <div class="container">
    <div class="footer-inner">
      <p>© 2025 {BRAND}. Alle rettigheter reservert.</p>
      <div class="footer-links">
        <a href="/api/website">Hjem</a>
        <a href="/api/privacy">Personvernregler</a>
        <a href="/api/terms">Vilkår</a>
        <a href="/api/support">Kontakt</a>
      </div>
    </div>
  </div>
</footer>
"""


def _page(title: str, body: str, description: str = ""):
    return f"""<!doctype html>
<html lang="no">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
<meta name="description" content="{description or 'Thai2Drive – Norsk teoriprøve på thai, norsk og engelsk. Laget for thai-folk i Norge.'}"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{description}"/>
<meta property="og:image" content="{HEADER_URL}"/>
<meta property="og:type" content="website"/>
<link rel="icon" type="image/png" href="{ICON_URL}"/>
<link rel="apple-touch-icon" href="{ICON_URL}"/>
<style>{_BASE_CSS}</style>
</head>
<body>
{_nav()}
{body}
{_footer()}
</body>
</html>"""


# ─────────────────────────── LANDING PAGE ───────────────────────────
@website_router.get("/website", response_class=HTMLResponse)
@website_router.get("/", response_class=HTMLResponse)  # fallback inside /api
def landing():
    body = f"""
<!-- HERO -->
<section class="hero container">
  <img src="{ICON_URL}" alt="{BRAND} app icon" class="hero-icon" loading="lazy"/>
  <h1>Bestå norsk teoriprøve<br/>på <span>ditt språk</span></h1>
  <p>Over 500 spørsmål på thai, norsk og engelsk med forklaringer – laget for thai-folk som bor i Norge.</p>

  <div class="flags" aria-label="Språk">
    <div class="flag flag-th"><div></div><div></div><div></div><div></div><div></div></div>
    <div class="flag flag-no"><div class="blue"></div><div class="bluev"></div></div>
    <div class="flag flag-gb"><div class="r1"></div><div class="r2"></div></div>
  </div>

  <div class="hero-badges">
    <span class="badge"><span class="dot"></span> 500+ spørsmål</span>
    <span class="badge">🇹🇭 Thai · 🇳🇴 Norsk · 🇬🇧 Engelsk</span>
    <span class="badge">🎯 Ekte eksamensformat</span>
  </div>

  <div><a href="#pricing" class="hero-cta">Kom i gang gratis →</a></div>
</section>

<!-- FEATURES -->
<section id="features" class="container">
  <div class="section-head">
    <span class="eyebrow">Hvorfor Thai2Drive</span>
    <h2>Alt du trenger for å bestå</h2>
    <p>Bygd sammen med thai-folk som har gjennomført den norske teoriprøven.</p>
  </div>
  <div class="features">
    <div class="feature">
      <div class="feature-icon">🌐</div>
      <h3>Tre språk samtidig</h3>
      <p>Les spørsmål og forklaringer på thai, norsk eller engelsk – bytt når som helst.</p>
    </div>
    <div class="feature">
      <div class="feature-icon">📚</div>
      <h3>500+ ekte spørsmål</h3>
      <p>Dekker alle kategoriene: vikeplikt, fartsgrenser, trafikkskilt, sikkerhet og mer.</p>
    </div>
    <div class="feature">
      <div class="feature-icon">🎯</div>
      <h3>Eksamensmodus</h3>
      <p>Øv med 45 spørsmål på 90 minutter – akkurat som den ekte teoriprøven.</p>
    </div>
    <div class="feature">
      <div class="feature-icon">💡</div>
      <h3>Forklaringer på alle svar</h3>
      <p>Forstå hvorfor et svar er riktig – ikke bare pugg.</p>
    </div>
    <div class="feature">
      <div class="feature-icon">🔁</div>
      <h3>Gjennomgang av feil</h3>
      <p>Øv ekstra på spørsmålene du svarte feil på.</p>
    </div>
    <div class="feature">
      <div class="feature-icon">🔥</div>
      <h3>Daglig rutine</h3>
      <p>Hold streak-en gående med 10 gratis spørsmål hver dag.</p>
    </div>
  </div>
</section>

<!-- PRICING -->
<section id="pricing" class="container">
  <div class="section-head">
    <span class="eyebrow">Priser</span>
    <h2>Start gratis – oppgrader når du er klar</h2>
    <p>Alle planer gir ubegrenset tilgang til hele spørsmåldatabasen og eksamen.</p>
  </div>
  <div class="pricing">
    <div class="plan">
      <h3>Gratis</h3>
      <div class="price">0 kr<small> / for alltid</small></div>
      <ul>
        <li>10 spørsmål per dag</li>
        <li>Dagens test</li>
        <li>Alle tre språk</li>
        <li>Fullt norsk grensesnitt</li>
      </ul>
    </div>
    <div class="plan">
      <h3>Månedlig</h3>
      <div class="price">199 kr<small> / mnd</small></div>
      <ul>
        <li>Ubegrenset spørsmål</li>
        <li>Full eksamensmodus</li>
        <li>Gjennomgang av feil</li>
        <li>Ingen annonser</li>
      </ul>
    </div>
    <div class="plan popular">
      <span class="ribbon">Beste verdi</span>
      <h3>3 måneder</h3>
      <div class="price">399 kr<small> / 3 mnd</small></div>
      <ul>
        <li>Alt i Månedlig</li>
        <li>Spar 34% vs. månedlig</li>
        <li>Perfekt frem til prøven</li>
        <li>Ingen annonser</li>
      </ul>
    </div>
    <div class="plan">
      <span class="ribbon" style="background:#6366F1;color:#fff">Livstid</span>
      <h3>Livstid</h3>
      <div class="price">699 kr<small> / engangsbetaling</small></div>
      <ul>
        <li>Betal én gang, bruk for alltid</li>
        <li>Alle fremtidige oppdateringer</li>
        <li>Perfekt hvis du skal kjøre flere prøver</li>
        <li>Ingen annonser</li>
      </ul>
    </div>
  </div>
</section>

<!-- CTA band -->
<section class="cta-band">
  <div class="container">
    <h2>Klar til å bestå?</h2>
    <p>Last ned {BRAND} og kom i gang på under ett minutt.</p>
    <a href="#" class="hero-cta">📱 Kommer snart på Google Play</a>
  </div>
</section>
"""
    return HTMLResponse(_page(
        f"{BRAND} – Norsk teoriprøve på thai, norsk og engelsk",
        body,
        description="Bestå den norske teoriprøven lettere – 500+ spørsmål med forklaringer på thai, norsk og engelsk. Laget for thai-folk i Norge.",
    ))


# ─────────────────────────── PRIVACY POLICY ───────────────────────────
@website_router.get("/privacy", response_class=HTMLResponse)
def privacy():
    body = f"""
<div class="legal">
  <h1>Personvernregler</h1>
  <p class="meta">Sist oppdatert: {LAST_UPDATED}</p>

  <div class="box">
    <strong>Kort oppsummert:</strong> Vi samler inn minst mulig data. Du kan bruke appen helt uten konto. Vi selger aldri data til tredjeparter.
  </div>

  <h2>1. Hvem vi er</h2>
  <p>{BRAND} («vi», «oss», «appen») er en mobilapplikasjon som hjelper brukere med å øve til den norske teoriprøven. Kontakt oss på <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> for personvernrelaterte spørsmål.</p>

  <h2>2. Hvilken informasjon vi samler inn</h2>

  <h3>a) Automatisk innsamlet (uten konto)</h3>
  <ul>
    <li><strong>Enhets-ID:</strong> En tilfeldig generert identifikator (ikke din telefon-ID) som brukes til å lagre fremgangen din lokalt og synkronisere med serveren.</li>
    <li><strong>Bruksdata:</strong> Hvilke spørsmål du har svart på, riktige/gale svar, studiestreak.</li>
    <li><strong>Språkvalg:</strong> Thai, norsk eller engelsk – lagret lokalt på enheten.</li>
  </ul>

  <h3>b) Hvis du oppretter konto</h3>
  <ul>
    <li><strong>E-postadresse</strong> (for innlogging og gjenoppretting av passord).</li>
    <li><strong>Kryptert passord</strong> (bcrypt – vi ser aldri klarteksten).</li>
  </ul>

  <h3>c) Hvis du kjøper Premium</h3>
  <ul>
    <li>Kjøpet behandles av <strong>RevenueCat + Google Play / Apple App Store</strong>. Vi mottar kun <em>om</em> du er Premium-bruker – ikke kortnummer eller adresse.</li>
  </ul>

  <h2>3. Hva vi IKKE samler inn</h2>
  <ul>
    <li>Ingen GPS/lokasjon</li>
    <li>Ingen kontakter eller telefonbok</li>
    <li>Ingen bilder eller kamera</li>
    <li>Ingen SMS eller samtaler</li>
    <li>Ingen reklame-sporing</li>
  </ul>

  <h2>4. Hvordan vi bruker dataen</h2>
  <ul>
    <li>For å la deg fortsette der du slapp</li>
    <li>For å synkronisere bokmerker og fremgang mellom enheter</li>
    <li>For å gi Premium-tilgang til betalende brukere</li>
    <li>For å forbedre spørsmålene og oversettelsene</li>
  </ul>

  <h2>5. Deling med tredjeparter</h2>
  <p>Vi deler data <strong>kun</strong> med følgende tjenester, og kun det som er strengt nødvendig:</p>
  <ul>
    <li><strong>MongoDB Atlas</strong> – skylagring av fremgang (EU-region).</li>
    <li><strong>RevenueCat</strong> – håndtering av abonnement/Premium-status.</li>
    <li><strong>Google Play Billing / Apple App Store</strong> – betalingshåndtering (vi ser aldri kortet ditt).</li>
  </ul>
  <p>Vi selger aldri data. Vi deler aldri data til annonsenettverk.</p>

  <h2>6. Dine rettigheter (GDPR)</h2>
  <p>Du har rett til å:</p>
  <ul>
    <li><strong>Få innsyn</strong> i hvilke data vi har om deg</li>
    <li><strong>Slette kontoen din</strong> og all tilhørende data</li>
    <li><strong>Eksportere</strong> dataen din</li>
    <li><strong>Trekke tilbake</strong> samtykket ditt</li>
  </ul>
  <p>Send en e-post til <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> med ønsket ditt – vi svarer innen 30 dager.</p>

  <h2>7. Barn</h2>
  <p>Appen er beregnet på brukere som er minst 16 år gamle og kan søke om førerkort i Norge. Vi samler ikke bevisst inn data fra barn.</p>

  <h2>8. Endringer i retningslinjene</h2>
  <p>Vi kan oppdatere disse retningslinjene. Vesentlige endringer varsles i appen.</p>

  <h2>9. Kontakt</h2>
  <p>Spørsmål? Skriv til <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>
</div>
"""
    return HTMLResponse(_page(
        f"Personvern – {BRAND}", body,
        description="Personvernregler for Thai2Drive. Vi samler inn minst mulig data og selger aldri til tredjeparter.",
    ))


# ─────────────────────────── TERMS OF SERVICE ───────────────────────────
@website_router.get("/terms", response_class=HTMLResponse)
def terms():
    body = f"""
<div class="legal">
  <h1>Brukervilkår</h1>
  <p class="meta">Sist oppdatert: {LAST_UPDATED}</p>

  <div class="box">
    <strong>Viktig:</strong> {BRAND} er et læringsverktøy og erstatter ikke offisiell undervisning fra Statens vegvesen eller godkjente trafikkskoler.
  </div>

  <h2>1. Aksept av vilkår</h2>
  <p>Ved å laste ned, installere eller bruke {BRAND} godtar du disse vilkårene. Hvis du ikke godtar, må du ikke bruke appen.</p>

  <h2>2. Tjenestebeskrivelse</h2>
  <p>{BRAND} tilbyr øvingsspørsmål til den norske teoriprøven på tre språk. Vi gir ingen garanti for at du vil bestå den offisielle prøven.</p>

  <h2>3. Brukerkonto</h2>
  <ul>
    <li>Du er ansvarlig for å holde passordet ditt sikkert.</li>
    <li>Du må ha minst 16 år for å opprette konto.</li>
    <li>Vi kan stenge kontoer som bryter vilkårene.</li>
  </ul>

  <h2>4. Premium-abonnement</h2>
  <ul>
    <li><strong>Fornyelse:</strong> Månedlig og 3-måneders abonnement fornyes automatisk via Google Play / App Store.</li>
    <li><strong>Oppsigelse:</strong> Du kan når som helst si opp i Google Play / App Store-innstillingene.</li>
    <li><strong>Refusjon:</strong> Refusjonsregler følger Google Plays og App Stores retningslinjer.</li>
    <li><strong>Livstid-kjøp:</strong> Gir tilgang så lenge appen eksisterer og støttes (minimum 3 år fra kjøp).</li>
    <li>Priser er i NOK og inkluderer norsk merverdiavgift.</li>
  </ul>

  <h2>5. Tillatt bruk</h2>
  <p>Du <strong>må ikke</strong>:</p>
  <ul>
    <li>Kopiere, videreselge eller publisere spørsmålene våre</li>
    <li>Forsøke å reversere appen</li>
    <li>Bruke appen til juks på offisielle prøver</li>
    <li>Omgå betalingsmurer eller geografiske begrensninger</li>
  </ul>

  <h2>6. Immaterielle rettigheter</h2>
  <p>Alt innhold (spørsmål, oversettelser, bilder, logo, kode) tilhører {BRAND} eller våre lisensgivere.</p>

  <h2>7. Ansvarsbegrensning</h2>
  <p>Appen leveres «som den er». Vi er ikke ansvarlig for:</p>
  <ul>
    <li>Om du består eller stryker på den offisielle prøven</li>
    <li>Feil eller unøyaktigheter i spørsmål (men meld fra så fikser vi dem!)</li>
    <li>Nedetid, datatap eller andre tekniske feil</li>
  </ul>

  <h2>8. Endringer</h2>
  <p>Vi kan endre disse vilkårene. Du varsles i appen ved vesentlige endringer.</p>

  <h2>9. Gjeldende lov</h2>
  <p>Norsk rett gjelder. Tvister behandles av norske domstoler.</p>

  <h2>10. Kontakt</h2>
  <p>Spørsmål om vilkår: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
</div>
"""
    return HTMLResponse(_page(
        f"Brukervilkår – {BRAND}", body,
        description="Brukervilkår for Thai2Drive.",
    ))


# ─────────────────────────── SUPPORT / CONTACT ───────────────────────────
@website_router.get("/support", response_class=HTMLResponse)
def support():
    body = f"""
<div class="legal">
  <h1>Support &amp; kontakt</h1>
  <p class="meta">Vi svarer vanligvis innen 1–2 virkedager.</p>

  <div class="box">
    <strong>📧 E-post:</strong> <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a><br/>
    Beskriv problemet ditt så godt du kan, og inkluder gjerne skjermbilde.
  </div>

  <h2>Vanlige spørsmål</h2>

  <h3>❓ Jeg kommer ikke inn på kontoen min</h3>
  <p>Send oss e-post med adressen du registrerte deg med, så hjelper vi deg med å tilbakestille passordet manuelt.</p>

  <h3>❓ Jeg kjøpte Premium, men det er ikke aktivert</h3>
  <p>Åpne appen, gå til Innstillinger → «Gjenopprett kjøp». Hvis det fortsatt ikke virker, send oss kvitteringen fra Google Play / App Store.</p>

  <h3>❓ Hvordan sier jeg opp abonnementet?</h3>
  <ul>
    <li><strong>Android:</strong> Google Play Store → Profil → Betalinger og abonnementer → Abonnementer → Thai2Drive → Si opp.</li>
    <li><strong>iPhone:</strong> Innstillinger → Apple ID → Abonnementer → Thai2Drive → Avbryt abonnement.</li>
  </ul>

  <h3>❓ Jeg fant en feil i et spørsmål</h3>
  <p>Send oss en e-post med spørsmålsteksten (eller skjermbilde), så korrigerer vi det raskt.</p>

  <h3>❓ Kan jeg bruke appen uten konto?</h3>
  <p>Ja! Du trenger ikke konto for å øve. Men da lagres fremgangen bare på den ene enheten.</p>

  <h3>❓ Hvilke språk støttes?</h3>
  <p>Thai 🇹🇭 · Norsk 🇳🇴 · Engelsk 🇬🇧 – du kan bytte når som helst i appen.</p>

  <h3>❓ Sletting av data / konto</h3>
  <p>Send e-post med emnefeltet «Slett konto» til <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>. Vi sletter kontoen og alle data innen 30 dager.</p>

  <h2>Forretningsinfo</h2>
  <p>
    {BRAND}<br/>
    E-post: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a><br/>
    Nettsted: <a href="/api/website">thai2drive.com</a>
  </p>
</div>
"""
    return HTMLResponse(_page(
        f"Support – {BRAND}", body,
        description="Trenger du hjelp? Kontakt Thai2Drive-supporten.",
    ))
