// Website Research Agent
// Usage: node analyze.js <URL> [oppdrag]
// Example: node analyze.js https://duolingo.com "klone appen"

const fs = require('fs');
const path = require('path');
const Anthropic = require('@anthropic-ai/sdk');

// Load .env
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  fs.readFileSync(envPath, 'utf8').split('\n').forEach(line => {
    const [key, ...vals] = line.trim().split('=');
    if (key && vals.length) process.env[key] = vals.join('=');
  });
}

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

async function scrapePage(url) {
  const puppeteer = require('puppeteer');
  let browser;
  try {
    browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36');
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await new Promise(r => setTimeout(r, 2000));

    const data = await page.evaluate(() => {
      // Get all text content
      const getText = (el) => el ? el.innerText || el.textContent || '' : '';

      // Meta tags
      const metas = {};
      document.querySelectorAll('meta').forEach(m => {
        const name = m.getAttribute('name') || m.getAttribute('property');
        const content = m.getAttribute('content');
        if (name && content) metas[name] = content;
      });

      // Links
      const links = [...document.querySelectorAll('a[href]')]
        .map(a => ({ text: a.innerText.trim(), href: a.href }))
        .filter(l => l.href && !l.href.startsWith('javascript') && l.text)
        .slice(0, 50);

      // Scripts (tech stack hints)
      const scripts = [...document.querySelectorAll('script[src]')]
        .map(s => s.src).filter(Boolean).slice(0, 30);

      // Forms
      const forms = [...document.querySelectorAll('form')].map(f => ({
        action: f.action,
        method: f.method,
        fields: [...f.querySelectorAll('input, textarea, select')].map(i => ({
          type: i.type, name: i.name, placeholder: i.placeholder
        }))
      }));

      // Headings
      const headings = [...document.querySelectorAll('h1,h2,h3')]
        .map(h => ({ tag: h.tagName, text: h.innerText.trim() }))
        .filter(h => h.text).slice(0, 30);

      // Main text
      const bodyText = document.body ? document.body.innerText.slice(0, 8000) : '';

      // Title
      const title = document.title;

      // Nav items
      const navItems = [...document.querySelectorAll('nav a, header a')]
        .map(a => a.innerText.trim()).filter(Boolean).slice(0, 20);

      return { title, metas, links, scripts, forms, headings, bodyText, navItems };
    });

    // Get page HTML for tech detection
    const html = await page.content();

    await browser.close();
    return { ...data, html: html.slice(0, 5000), url };
  } catch (err) {
    if (browser) await browser.close().catch(() => {});
    throw err;
  }
}

function detectTechStack(data) {
  const hints = [];
  const all = (data.html + data.scripts.join(' ')).toLowerCase();

  if (all.includes('react') || all.includes('_react')) hints.push('React');
  if (all.includes('vue') || all.includes('vuejs')) hints.push('Vue.js');
  if (all.includes('angular')) hints.push('Angular');
  if (all.includes('next.js') || all.includes('__next')) hints.push('Next.js');
  if (all.includes('nuxt')) hints.push('Nuxt.js');
  if (all.includes('svelte')) hints.push('Svelte');
  if (all.includes('tailwind')) hints.push('Tailwind CSS');
  if (all.includes('bootstrap')) hints.push('Bootstrap');
  if (all.includes('wordpress') || all.includes('wp-content')) hints.push('WordPress');
  if (all.includes('shopify')) hints.push('Shopify');
  if (all.includes('webflow')) hints.push('Webflow');
  if (all.includes('firebase')) hints.push('Firebase');
  if (all.includes('supabase')) hints.push('Supabase');
  if (all.includes('stripe')) hints.push('Stripe (betaling)');
  if (all.includes('apollo') || all.includes('graphql')) hints.push('GraphQL');
  if (all.includes('gsap')) hints.push('GSAP animasjoner');
  if (all.includes('framer')) hints.push('Framer Motion');
  if (all.includes('expo') || all.includes('react-native')) hints.push('React Native / Expo');

  return hints.length > 0 ? hints : ['Ikke oppdaget automatisk'];
}

async function analyzeWithClaude(data, oppdrag) {
  const techStack = detectTechStack(data);

  const prompt = `Du er en ekspert webutvikler og produktanalytiker. Analyser denne nettsiden grundig.

URL: ${data.url}
TITTEL: ${data.title}

META-INFO:
${JSON.stringify(data.metas, null, 2)}

NAVIGASJON:
${data.navItems.join(', ')}

OVERSKRIFTER PÅ SIDEN:
${data.headings.map(h => `${h.tag}: ${h.text}`).join('\n')}

TEKST FRA SIDEN (første 5000 tegn):
${data.bodyText}

SKJEMAER:
${JSON.stringify(data.forms, null, 2)}

TECH STACK (automatisk oppdaget):
${techStack.join(', ')}

SCRIPTS:
${data.scripts.slice(0, 15).join('\n')}

OPPDRAGET:
${oppdrag || 'Gi en full rapport om nettsiden'}

---

Lag en GRUNDIG rapport med disse seksjonene:

## 🌐 HVA ER DETTE?
Beskriv hva siden er, målgruppen, og hva den tilbyr.

## ✨ HOVEFUNKSJONER OG FEATURES
List alle funksjoner du kan se. Vær spesifikk.

## 🛠️ TECH STACK OG TEKNOLOGI
Hva bruker de? Frontend, backend, database, betalingsløsning, hosting?

## 👥 BRUKERFLYT
Hvordan bruker en typisk bruker siden? (Registrering → onboarding → kjernefunksjon → betaling etc.)

## 💰 FORRETNINGSMODELL
Gratis? Premium? Abonnement? Hva koster det?

## 🏗️ HVIS JEG SKAL BYGGE/KLONE DETTE
- Hva trenger jeg?
- Hvilke teknologier anbefaler du?
- Anslått tid og kompleksitet (enkel/middels/kompleks)
- De viktigste delene å fokusere på

## ⚡ UNIKE TING / DIFFERENTIATORER
Hva gjør denne siden spesiell? Hva er vanskelig å kopiere?

## 📋 KONKLUSJON OG ANBEFALING
Oppsummering og anbefaling for oppdraget.

Svar på norsk. Vær konkret og presis.`;

  const response = await client.messages.create({
    model: 'claude-opus-4-7',
    max_tokens: 4000,
    messages: [{ role: 'user', content: prompt }]
  });

  return response.content[0].text;
}

async function main() {
  const url = process.argv[2];
  const oppdrag = process.argv.slice(3).join(' ');

  if (!url) {
    console.log('Bruk: node analyze.js <URL> [oppdrag]');
    console.log('Eks:  node analyze.js https://duolingo.com "klone appen"');
    process.exit(1);
  }

  console.log(`\n🔍 Analyserer: ${url}`);
  if (oppdrag) console.log(`📋 Oppdrag: ${oppdrag}`);
  console.log('⏳ Laster inn siden...\n');

  let data;
  try {
    data = await scrapePage(url);
    console.log(`✅ Side lastet: "${data.title}"`);
  } catch (err) {
    console.error('❌ Feil ved lasting av siden:', err.message);
    process.exit(1);
  }

  console.log('🤖 Claude analyserer...\n');
  const rapport = await analyzeWithClaude(data, oppdrag);

  // Save report
  const filename = `rapport_${new Date().toISOString().slice(0,10)}_${url.replace(/[^a-z0-9]/gi,'_').slice(0,30)}.txt`;
  fs.writeFileSync(filename, `URL: ${url}\nDato: ${new Date().toLocaleString('no-NO')}\nOppdrag: ${oppdrag || 'Full rapport'}\n\n${rapport}`);

  console.log('═'.repeat(60));
  console.log(rapport);
  console.log('═'.repeat(60));
  console.log(`\n💾 Rapport lagret: ${filename}`);
}

main().catch(console.error);
