// Load .env manually to avoid dotenvx conflicts
const fs = require('fs');
const envContent = fs.readFileSync(__dirname + '/.env', 'utf8');
envContent.split('\n').forEach(line => {
  const [key, ...vals] = line.trim().split('=');
  if (key && vals.length) process.env[key] = vals.join('=');
});
const Anthropic = require('@anthropic-ai/sdk');
const nodemailer = require('nodemailer');

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

async function generatePosts() {
  const today = new Date().toLocaleDateString('no-NO', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  const response = await client.messages.create({
    model: 'claude-opus-4-7',
    max_tokens: 2000,
    messages: [{
      role: 'user',
      content: `Du er en markedsføringsekspert for appen Thai2Drive.

OM APPEN:
- Thai2Drive er en app for Thai-folk i Norge som skal ta teoriprøven
- Appen har spørsmål om norsk trafikk på thai-språk
- Laget av Michael Pisaiyavong, trafikklærer i Oslo siden 2010
- 10 gratis spørsmål, deretter premium
- Tilgjengelig på Google Play

LAG 3 INNLEGG for ${today}:

INNLEGG 1: Facebook (norsk + thai) - personlig historie fra Michael som trafikklærer
INNLEGG 2: Facebook (kort og fengende) - tips om teoriprøven i Norge
INNLEGG 3: Instagram caption - visuelt og engasjerende med emojis

FORMAT:
=== INNLEGG 1 - FACEBOOK LANG ===
[tekst her]

=== INNLEGG 2 - FACEBOOK KORT ===
[tekst her]

=== INNLEGG 3 - INSTAGRAM ===
[tekst her]

=== ANBEFALTE GRUPPER ===
- List 3 Facebook-grupper å poste i

=== VIDEO/BILDE IDÉ (30 sek video Michael kan lage) ===
- Beskriv én konkret video eller bilde Michael kan lage hjemme med telefonen
- Gi eksakt manus/script for videoen (hva han skal si på norsk og thai)
- Si hvilken plattform den passer best for

Gjør innleggene varierte, autentiske og engasjerende!`
    }]
  });

  return response.content[0].text;
}

async function sendEmail(posts) {
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_FROM,
      pass: process.env.EMAIL_APP_PASSWORD
    }
  });

  const today = new Date().toLocaleDateString('no-NO', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  const html = `
    <div style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto;">
      <div style="background: #1a73e8; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
        <h1 style="margin: 0;">🚗 Thai2Drive Marketing Agent</h1>
        <p style="margin: 5px 0 0 0;">${today}</p>
      </div>
      <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px;">
        <p>Hei Michael! Her er ukens innlegg klar for godkjenning:</p>
        <div style="background: white; padding: 20px; border-radius: 8px; white-space: pre-wrap; border-left: 4px solid #1a73e8;">
${posts}
        </div>
        <br>
        <p style="color: #666;">✅ Gjennomgå innleggene og post det du liker!</p>
        <p style="color: #666; font-size: 12px;">Generert automatisk av Thai2Drive Marketing Agent</p>
      </div>
    </div>
  `;

  await transporter.sendMail({
    from: `Thai2Drive Marketing <${process.env.EMAIL_FROM}>`,
    to: process.env.EMAIL_TO,
    subject: `📱 Thai2Drive - Innlegg klar for godkjenning (${today})`,
    html
  });

  console.log('✅ E-post sendt til', process.env.EMAIL_TO);
}

async function main() {
  console.log('🤖 Genererer innlegg...');
  const posts = await generatePosts();
  console.log('📧 Sender e-post...');
  await sendEmail(posts);
  console.log('✅ Ferdig!');
}

main().catch(console.error);
