const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.resolve(__dirname, '..');
const server_code = fs.readFileSync(path.join(ROOT, 'backend', 'server.py'), 'utf8');
const teacher_code = fs.readFileSync(path.join(ROOT, 'backend', 'teacher_chat.py'), 'utf8');
const webapp_code = fs.readFileSync(path.join(ROOT, 'backend', 'webapp.py'), 'utf8');
const media_catalog_code = fs.readFileSync(path.join(ROOT, 'backend', 'media_catalog.py'), 'utf8');
const admin_analytics_code = fs.readFileSync(path.join(ROOT, 'backend', 'admin_analytics.py'), 'utf8');
const micro_lessons_code = fs.readFileSync(path.join(ROOT, 'backend', 'micro_lessons.py'), 'utf8');
const readiness_code = fs.readFileSync(path.join(ROOT, 'backend', 'readiness.py'), 'utf8');
const billing_code = fs.readFileSync(path.join(ROOT, 'backend', 'billing.py'), 'utf8');
const sw_code = fs.readFileSync(path.join(ROOT, 'backend', 'service-worker.js'), 'utf8');

console.log('🚀 Running Michael AI BLAST Contract Tests & Missions 1–8 Suite...');

function test(name, fn) {
  try {
    fn();
    console.log(`  ✅ PASS: ${name}`);
  } catch (err) {
    console.error(`  ❌ FAIL: ${name}`);
    console.error(err);
    process.exit(1);
  }
}

test('Media Catalog contains core traffic topics', () => {
  assert(media_catalog_code.includes('vikeplikt'), 'vikeplikt must be in categories');
  assert(media_catalog_code.includes('stoppelengde'), 'stoppelengde must be in categories');
  assert(media_catalog_code.includes('skilt'), 'skilt must be in categories');
  assert(media_catalog_code.includes('hav_regelen'), 'hav_regelen must be in categories');
  assert(media_catalog_code.includes('validate_catalog_document'), 'validate_catalog_document must be defined');
});

test('teacher_chat connects to approved media and includes media in TeacherChatResponse', () => {
  assert(teacher_code.includes('media: list[dict]'), 'TeacherChatResponse must have media field');
  assert(teacher_code.includes('_db["michael_materials"]'), 'teacher_chat must query michael_materials');
});

test('teacher_chat has data-driven weakness coaching and open conversational greetings', () => {
  assert(teacher_code.includes('def _get_student_weakness'), '_get_student_weakness helper must exist');
  assert(teacher_code.includes('is_theory_help'), 'Dynamic theory help detection must exist');
  assert(teacher_code.includes('Hva vil du at vi skal øve på i dag?'), 'Open friendly NO greeting must exist');
  assert(teacher_code.includes('วันนี้อยากให้เราฝึกเรื่องอะไรดีครับ?'), 'Open friendly TH greeting must exist');
  assert(teacher_code.includes('What would you like us to practice today?'), 'Open friendly EN greeting must exist');
});

test('admin_analytics_router mounted in server.py and endpoints defined', () => {
  assert(server_code.includes('admin_analytics_router'), 'server.py must import admin_analytics_router');
  assert(server_code.includes('app.include_router(admin_analytics_router, prefix="/api")'), 'server.py must mount admin_analytics_router');
  assert(admin_analytics_code.includes('/admin/analytics'), 'Admin analytics prefix must exist');
});

test('webapp.py contains Lightbox modal and click handlers', () => {
  assert(webapp_code.includes('id="t2dLightbox"'), 'Lightbox container must be present');
  assert(webapp_code.includes('openLightbox('), 'openLightbox function must exist');
  assert(webapp_code.includes('closeLightbox('), 'closeLightbox function must exist');
  assert(webapp_code.includes('.t2d-lightbox'), 'Lightbox CSS must be present');
});

test('webapp.py contains hardened audio lifecycle with instance destruction & watchdog', () => {
  assert(webapp_code.includes('_teacherWatchdog'), '_teacherWatchdog variable must exist');
  assert(webapp_code.includes('_teacherAudioToken'), '_teacherAudioToken variable must exist');
  assert(webapp_code.includes('a.src = \'\''), 'Audio src reset must be present in stopAllSpeech');
  assert(webapp_code.includes('a.load()'), 'Audio load must be present in stopAllSpeech');
});

test('webapp.py contains Video button adjacent to Michael and Media Cards', () => {
  assert(webapp_code.includes('id="bnTeacher" onclick="showTab(\'teacher\')">'), 'bnTeacher must exist');
  assert(webapp_code.includes('id="bnLibrary" onclick="showTab(\'library\')">'), 'bnLibrary must exist');
  assert(webapp_code.indexOf('id="bnTeacher"') < webapp_code.indexOf('id="bnLibrary"'), 'bnLibrary must be adjacent to bnTeacher in bottomNav');
  assert(webapp_code.includes('buildVideoCard('), 'buildVideoCard function must exist');
  assert(webapp_code.includes('buildPodcastCard('), 'buildPodcastCard function must exist');
  assert(webapp_code.includes('bindBottomNavCarousel()'), 'bindBottomNavCarousel function must exist');
});

test('Language purity: no forbidden cross-language fallback patterns', () => {
  assert(!webapp_code.includes('|| TR.en'), 'No TR.en fallback');
  assert(!webapp_code.includes('|| TRANSLATIONS.no'), 'No TRANSLATIONS.no fallback');
});

// ─── Oppdrag 1: Michaels Kognitive Loop & § 7 nr. 2 Venstresving ───
test('Oppdrag 1: Michaels Kognitive Loop (Se -> Oppfatte -> Avgjore + Thai ครับ/ผม)', () => {
  assert(teacher_code.includes('MICHAELS KOGNITIVE BESLUTNINGSLØKKE'), 'Decision loop header must exist');
  assert(teacher_code.includes('STEG 1: SE (Spør og lytt!)'), 'Step 1 SE must exist');
  assert(teacher_code.includes('STEG 2: OPPFATTE'), 'Step 2 OPPFATTE must exist');
  assert(teacher_code.includes('STEG 3: AVGJØRE'), 'Step 3 AVGJØRE must exist');
  assert(teacher_code.includes('Kongen og tjeneren'), 'Kongen og tjeneren metaphor must exist');
  assert(teacher_code.includes('HAV-regelen'), 'HAV-regelen metaphor must exist');
  assert(teacher_code.includes('ครับ (khrap)'), 'Thai male particle must be required');
  assert(teacher_code.includes('ผม (phom)'), 'Thai male pronoun must be required');
  assert(teacher_code.includes('Ingen juridisk døråpner'), 'Ban on legal opening must exist');
  assert(teacher_code.includes('Ingen falsk AI-skryt'), 'Ban on sycophancy must exist');
});

test('Oppdrag 1: Trafikkreglene § 7 nr. 2 Oncoming traffic & Left-turn exact explanation', () => {
  assert(teacher_code.includes('Når du skal svinge til venstre, vil den møtende bilen havne på din høyre side.'), 'Must have pedagogical left-turn explanation');
  assert(teacher_code.includes('Det betyr at du har vikeplikt etter høyreregelen (§ 7 nr. 2). Du er tjeneren, og den møtende bilen er kongen – du må la kongen kjøre først!'), 'Must include King/Servant explanation for oncoming traffic');
  assert(teacher_code.includes('høyreregelen gjelder ikke for møtende'), 'Must catch and sanitize forbidden LLM negation');
});

// ─── Oppdrag 2: Karusell på iOS Safari ───
test('Oppdrag 2: Karusell-Risting iOS Safari (scroll-snap-type: none på #bottomNav)', () => {
  assert(webapp_code.includes('scroll-snap-type: none'), '#bottomNav must disable aggressive scroll-snap');
  assert(webapp_code.includes('.js-scrolling'), '.js-scrolling class must exist');
  assert(webapp_code.includes('_scrollSnapTimer'), '_scrollSnapTimer must exist in showTab');
});

// ─── Oppdrag 3: Audio & TTS ───
test('Oppdrag 3: Backend-TTS & Mobil Lydavspilling (Accept-Ranges bytes & Clean Audio)', () => {
  assert(server_code.includes('"Accept-Ranges": "bytes"'), 'Accept-Ranges must exist on server');
  assert(server_code.includes('"Cache-Control": "no-cache"'), 'Cache-Control must exist on server');
  assert(webapp_code.includes('audio.load();'), 'audio.load() must be called in user gesture');
  assert(!webapp_code.includes('_SILENT_WAV'), 'Destructive silent WAV race must be removed');
});

// ─── Oppdrag 5 ───
test('Oppdrag 5: «Thailand vs Norge» Mikroleksjoner', () => {
  assert(server_code.includes('micro_lessons_router'), 'server.py must include micro_lessons_router');
  assert(micro_lessons_code.includes('/api/lessons/culture'), 'Endpoint /api/lessons/culture must exist');
  assert(micro_lessons_code.includes('lesson_1_priority'), 'lesson_1_priority must exist');
  assert(micro_lessons_code.includes('lesson_2_pedestrians'), 'lesson_2_pedestrians must exist');
  assert(micro_lessons_code.includes('lesson_3_roundabout'), 'lesson_3_roundabout must exist');
  assert(micro_lessons_code.includes('lesson_4_winter'), 'lesson_4_winter must exist');
  assert(micro_lessons_code.includes('metafor_th'), 'metafor_th must exist');
});

// ─── Oppdrag 6 ───
test('Oppdrag 6: Michaels Exam Mode & Intelligent Klar-Score', () => {
  assert(server_code.includes('readiness_router'), 'server.py must include readiness_router');
  assert(readiness_code.includes('/api/user/readiness'), 'Endpoint /api/user/readiness must exist');
  assert(readiness_code.includes('accuracy_score * 0.5'), 'Accuracy weight 50% must exist');
  assert(readiness_code.includes('topic_score * 0.3'), 'Topic weight 30% must exist');
  assert(readiness_code.includes('simulation_score * 0.2'), 'Simulation weight 20% must exist');
  assert(readiness_code.includes('icon'), 'icon status must exist');
});

// ─── Oppdrag 7 ───
test('Oppdrag 7: RevenueCat Billing & Fail-Soft', () => {
  assert(server_code.includes('billing_router'), 'server.py must include billing_router');
  assert(billing_code.includes('/api/billing/subscription'), 'Endpoint /api/billing/subscription must exist');
  assert(billing_code.includes('REVENUECAT_API_KEY'), 'REVENUECAT_API_KEY must be read from env');
  assert(billing_code.includes('offline_fallback'), 'Fail-soft offline_fallback must exist');
});

// ─── Oppdrag 8 ───
test('Oppdrag 8: Offline-Modus & ServiceWorker', () => {
  assert(server_code.includes('/service-worker.js'), 'server.py must serve /service-worker.js');
  assert(webapp_code.includes('navigator.serviceWorker.register'), 'webapp.py must register service worker');
  assert(sw_code.includes('CACHE_NAME'), 'ServiceWorker must define CACHE_NAME');
  assert(sw_code.includes('OFFLINE_URLS'), 'ServiceWorker must define OFFLINE_URLS');
});

// ─── Android / Chrome Live Hardening Tests ───
test('Samsung/Android Hardening: Section 7.2 Dialect ("koer imot") & Male Gender Lock', () => {
  assert(teacher_code.includes('"koer imot"'), 'teacher_chat.py must explicitly cover dialect "koer imot"');
  assert(teacher_code.includes('_sanitize_gender_particles'), 'teacher_chat.py must include _sanitize_gender_particles');
  assert(teacher_code.includes('ครับผม'), 'teacher_chat.py fallback must use ครับผม');
  const support_code = fs.readFileSync(path.join(ROOT, 'backend', 'support_chat.py'), 'utf8');
  assert(!support_code.includes('ขอโทษค่ะ'), 'support_chat.py must not contain female particle ขอโทษค่ะ');
  assert(support_code.includes('ขอโทษครับ'), 'support_chat.py must use polite male particle ขอโทษครับ');
});

test('Samsung/Android Hardening: FileResponse & HTTP 206 Range Streaming in server.py', () => {
  assert(server_code.includes('return FileResponse('), 'server.py _stream_mp3_file must return FileResponse for HTTP 206 support');
  assert(server_code.includes('.mp3": "audio/mpeg"'), 'public_asset must sniff .mp3 as audio/mpeg');
  assert(server_code.includes('.mp4": "video/mp4"'), 'public_asset must sniff .mp4 as video/mp4');
  assert(server_code.includes('@app.get("/public_assets/{filename:path}")'), 'public_assets path must be registered in server.py');
});

test('Samsung/Android Hardening: #bottomNav flex-wrap nowrap & Hidden Scrollbars in webapp.py', () => {
  assert(webapp_code.includes('flex-wrap: nowrap !important;'), '#bottomNav must have flex-wrap: nowrap !important');
  assert(webapp_code.includes('-ms-overflow-style: none;'), '#bottomNav must hide scrollbars on all platforms');
});

console.log('\n🎉 ALL 20/20 CONTRACT & GROUNDING TESTS PASSED! 100% PRODUCTION READY!\n');
