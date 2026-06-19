// Deep UI/UX Structure Analyzer
// Usage: node deep-analyze.js <URL> [fokus]

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

async function scrapeDeep(startUrl) {
  const puppeteer = require('puppeteer');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,900']
  });

  const results = [];

  async function scrapePage(url, label) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36');

    try {
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
      await new Promise(r => setTimeout(r, 2000));

      // Take screenshot
      const screenshotPath = path.join(__dirname, `screenshot_${label}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: false });
      console.log(`📸 Screenshot: screenshot_${label}.png`);

      // Extract structure
      const data = await page.evaluate(() => {
        const headings = [...document.querySelectorAll('h1,h2,h3,h4')]
          .map(h => `${h.tagName}: ${h.innerText.trim()}`).filter(Boolean).slice(0, 40);

        const buttons = [...document.querySelectorAll('button, [role="button"], .btn, input[type="button"], input[type="submit"]')]
          .map(b => b.innerText?.trim() || b.value || b.getAttribute('aria-label') || '')
          .filter(Boolean).slice(0, 30);

        const links = [...document.querySelectorAll('nav a, header a, .menu a, .nav a')]
          .map(a => a.innerText.trim()).filter(Boolean).slice(0, 25);

        const forms = [...document.querySelectorAll('form')].map(f => ({
          fields: [...f.querySelectorAll('input,select,textarea')]
            .map(i => `${i.type || i.tagName}:${i.name || i.placeholder || i.id}`)
        }));

        // Quiz/question elements
        const questionLike = [...document.querySelectorAll('[class*="question"],[class*="quiz"],[class*="answer"],[class*="option"],[class*="sporsmal"],[class*="svar"]')]
          .map(el => ({
            tag: el.tagName,
            class: el.className,
            text: el.innerText?.trim().slice(0, 200)
          })).slice(0, 20);

        const bodyText = document.body?.innerText?.slice(0, 6000) || '';
        const title = document.title;
        const url = window.location.href;

        return { title, url, headings, buttons, links, forms, questionLike, bodyText };
      });

      // Read screenshot for Claude
      const screenshotBase64 = fs.readFileSync(screenshotPath).toString('base64');

      results.push({ label, ...data, screenshotBase64, screenshotPath });
      await page.close();
      return data;

    } catch (err) {
      console.log(`⚠️  Feil på ${url}: ${err.message}`);
      await page.close();
      return null;
    }
  }

  // Step 1: Main page
  console.log('\n📄 Laster hovedside...');
  const mainData = await scrapePage(startUrl, 'main');

  // Step 2: Find quiz/test links and follow them
  const page2 = await browser.newPage();
  await page2.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36');
  await page2.goto(startUrl, { waitUntil: 'networkidle2', timeout: 30000 });

  const subLinks = await page2.evaluate((baseUrl) => {
    const allLinks = [...document.querySelectorAll('a[href]')].map(a => ({
      text: a.innerText.trim(),
      href: a.href
    })).filter(l => l.href.startsWith(baseUrl) || l.href.startsWith('/'));

    // Prioritize quiz/test/pricing links
    const keywords = ['quiz','test','prøv','gratis','kjøp','pris','prøve','bil','mc','øv','start','logg','registrer','spørsmål','svar'];
    return allLinks
      .filter(l => keywords.some(k => l.text.toLowerCase().includes(k) || l.href.toLowerCase().includes(k)))
      .slice(0, 6);
  }, startUrl);

  await page2.close();

  console.log(`🔗 Fant ${subLinks.length} interessante undersider:`);
  subLinks.forEach(l => console.log(`   - ${l.text}: ${l.href}`));

  // Step 3: Visit sub-pages
  for (let i = 0; i < Math.min(subLinks.length, 4); i++) {
    const link = subLinks[i];
    const label = `sub${i+1}_${link.text.replace(/[^a-z0-9]/gi,'_').slice(0,20)}`;
    console.log(`\n📄 Besøker: ${link.text}...`);
    await scrapePage(link.href, label);
    await new Promise(r => setTimeout(r, 1000));
  }

  await browser.close();
  return results;
}

async function analyzeWithClaude(results, fokus) {
  const mainPage = results[0];
  const subPages = results.slice(1);

  // Build messages with screenshots
  const messages = [];

  // First message: text analysis request
  const textContent = results.map(r => `
=== SIDE: ${r.label} (${r.url}) ===
TITTEL: ${r.title}
NAVIGASJON: ${r.links?.join(' | ')}
OVERSKRIFTER: ${r.headings?.join(' | ')}
KNAPPER: ${r.buttons?.join(' | ')}
SKJEMAER: ${JSON.stringify(r.forms)}
QUIZ-ELEMENTER: ${JSON.stringify(r.questionLike?.slice(0,5))}
TEKST (utdrag): ${r.bodyText?.slice(0, 2000)}
`).join('\n\n');

  // Build content array with screenshots
  const content = [
    {
      type: 'text',
      text: `Du er en ekspert UI/UX-designer og webutvikler. Analyser disse skjermbildene og teksten fra nettsiden grundig.

FOKUS FOR ANALYSEN: ${fokus || 'UI/UX struktur og quiz/spørsmål-funksjonalitet'}

Her er tekstdata fra sidene:
${textContent}

Og her er skjermbildene (se nedenfor). Analyser GRUNDIG med disse seksjonene:

## 🎨 DESIGN OG LAYOUT
Farger, typografi, spacing, visuell hierarki. Hva er førsteinntrykket?

## 📱 QUIZ/SPØRSMÅL-STRUKTUR
Hvordan vises spørsmål? Alternativer? Tilbakemelding? Timer? Progress? Beskriv NØYAKTIG hvordan quiz-grensesnittet fungerer.

## 🔄 BRUKERFLYT
Steg-for-steg: hvordan kommer man fra forside til å svare på et spørsmål?

## 🧩 KOMPONENTER SOM KAN KOPIERES
List konkrete UI-komponenter (Quiz-card, Progress-bar, Timer, Score-display etc.) vi kan bygge i React/React Native.

## ✅ HVA ER BRA (ta inspirasjon)
Konkrete ting Thai2Drive bør kopiere/inspireres av.

## ❌ HVA ER DÅRLIG (gjør bedre)
Svakheter i deres UI/UX som Thai2Drive kan gjøre bedre.

## 🏗️ BYGGEPLAN
Hvilke React-komponenter trenger vi for å lage noe lignende eller bedre?

Svar på norsk. Vær VELDIG konkret og detaljert.`
    }
  ];

  // Add screenshots
  for (const r of results) {
    if (r.screenshotBase64) {
      content.push({
        type: 'text',
        text: `\n--- Skjermbilde: ${r.label} (${r.url}) ---`
      });
      content.push({
        type: 'image',
        source: {
          type: 'base64',
          media_type: 'image/png',
          data: r.screenshotBase64
        }
      });
    }
  }

  const response = await client.messages.create({
    model: 'claude-opus-4-7',
    max_tokens: 4000,
    messages: [{ role: 'user', content }]
  });

  return response.content[0].text;
}

async function main() {
  const url = process.argv[2];
  const fokus = process.argv.slice(3).join(' ');

  if (!url) {
    console.log('Bruk: node deep-analyze.js <URL> [fokus]');
    console.log('Eks:  node deep-analyze.js https://teoritentamen.no "quiz-struktur og UI"');
    process.exit(1);
  }

  console.log(`\n🔍 Deep analyse: ${url}`);
  if (fokus) console.log(`🎯 Fokus: ${fokus}`);

  const results = await scrapeDeep(url);
  console.log(`\n✅ Scraped ${results.length} sider`);

  console.log('\n🤖 Claude analyserer med skjermbilder...\n');
  const rapport = await analyzeWithClaude(results, fokus);

  const filename = `deep_rapport_${new Date().toISOString().slice(0,10)}_${url.replace(/[^a-z0-9]/gi,'_').slice(0,25)}.txt`;
  fs.writeFileSync(filename, `URL: ${url}\nDato: ${new Date().toLocaleString('no-NO')}\nFokus: ${fokus}\n\n${rapport}`);

  console.log('═'.repeat(60));
  console.log(rapport);
  console.log('═'.repeat(60));
  console.log(`\n💾 Rapport lagret: ${filename}`);
  console.log(`📸 Skjermbilder lagret i: ${__dirname}`);
}

main().catch(console.error);
