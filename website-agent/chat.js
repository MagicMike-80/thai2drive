// Website Research Chat Agent
// Usage: node chat.js <URL>

const fs = require('fs');
const path = require('path');
const readline = require('readline');
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
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36');
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await new Promise(r => setTimeout(r, 2000));

  const data = await page.evaluate(() => {
    const links = [...document.querySelectorAll('a[href]')]
      .map(a => ({ text: a.innerText.trim(), href: a.href }))
      .filter(l => l.text && l.href && !l.href.startsWith('javascript'))
      .slice(0, 60);

    const headings = [...document.querySelectorAll('h1,h2,h3')]
      .map(h => `${h.tagName}: ${h.innerText.trim()}`)
      .filter(Boolean).slice(0, 30);

    const buttons = [...document.querySelectorAll('button, .btn, [role="button"]')]
      .map(b => b.innerText?.trim()).filter(Boolean).slice(0, 20);

    const scripts = [...document.querySelectorAll('script[src]')]
      .map(s => s.src).filter(Boolean).slice(0, 20);

    return {
      title: document.title,
      url: window.location.href,
      bodyText: document.body?.innerText?.slice(0, 10000) || '',
      links, headings, buttons, scripts
    };
  });

  const html = await page.content();
  await browser.close();
  return { ...data, html: html.slice(0, 3000) };
}

function detectTech(data) {
  const all = (data.html + data.scripts.join(' ')).toLowerCase();
  const found = [];
  if (all.includes('react')) found.push('React');
  if (all.includes('next')) found.push('Next.js');
  if (all.includes('vue')) found.push('Vue.js');
  if (all.includes('angular')) found.push('Angular');
  if (all.includes('tailwind')) found.push('Tailwind CSS');
  if (all.includes('bootstrap')) found.push('Bootstrap');
  if (all.includes('stripe')) found.push('Stripe');
  if (all.includes('firebase')) found.push('Firebase');
  if (all.includes('supabase')) found.push('Supabase');
  if (all.includes('wordpress')) found.push('WordPress');
  if (all.includes('shopify')) found.push('Shopify');
  return found;
}

async function main() {
  const url = process.argv[2];

  if (!url) {
    console.log('\nBruk: node chat.js <URL>');
    console.log('Eks:  node chat.js https://duolingo.com\n');
    process.exit(1);
  }

  console.log('\n================================');
  console.log(' Website Research Chat');
  console.log('================================\n');
  console.log(`🔍 Laster inn: ${url}`);
  console.log('⏳ Vennligst vent...\n');

  let siteData;
  try {
    siteData = await scrapePage(url);
    console.log(`✅ Klar! Siden er lastet: "${siteData.title}"`);
    console.log(`🛠️  Tech: ${detectTech(siteData).join(', ') || 'ukjent'}`);
  } catch (err) {
    console.error('❌ Kunne ikke laste siden:', err.message);
    process.exit(1);
  }

  const tech = detectTech(siteData);
  const systemPrompt = `Du er en ekspert webutvikler og produktanalytiker. Du hjelper brukeren med å forstå og analysere nettsiden ${url}.

Her er alt du vet om siden:

TITTEL: ${siteData.title}
URL: ${siteData.url}
TECH STACK: ${tech.join(', ') || 'ikke oppdaget'}

OVERSKRIFTER:
${siteData.headings.join('\n')}

KNAPPER/CTA:
${siteData.buttons.join(', ')}

LENKER:
${siteData.links.map(l => `${l.text}: ${l.href}`).join('\n').slice(0, 2000)}

TEKST FRA SIDEN:
${siteData.bodyText}

Svar alltid på norsk. Vær konkret og presis. Hjelp brukeren med å forstå siden, sammenligne med Thai2Drive, eller planlegge å bygge noe lignende.`;

  const conversationHistory = [];

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  console.log('\n💬 Nå kan du chatte! Still spørsmål om siden.');
  console.log('   Skriv "avslutt" for å avslutte.\n');
  console.log('─'.repeat(50));

  const askQuestion = () => {
    rl.question('\nDu: ', async (input) => {
      input = input.trim();

      if (!input) {
        askQuestion();
        return;
      }

      if (input.toLowerCase() === 'avslutt' || input.toLowerCase() === 'quit' || input.toLowerCase() === 'exit') {
        console.log('\n👋 Ha det bra!\n');
        rl.close();
        return;
      }

      conversationHistory.push({ role: 'user', content: input });

      try {
        process.stdout.write('\nAgent: ');

        const stream = await client.messages.create({
          model: 'claude-opus-4-7',
          max_tokens: 1500,
          system: systemPrompt,
          messages: conversationHistory,
          stream: true
        });

        let fullResponse = '';
        for await (const event of stream) {
          if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
            process.stdout.write(event.delta.text);
            fullResponse += event.delta.text;
          }
        }

        console.log('\n');
        console.log('─'.repeat(50));

        conversationHistory.push({ role: 'assistant', content: fullResponse });

      } catch (err) {
        console.error('\n❌ Feil:', err.message);
      }

      askQuestion();
    });
  };

  askQuestion();
}

main().catch(console.error);
