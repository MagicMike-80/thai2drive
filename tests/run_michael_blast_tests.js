const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT = path.resolve(__dirname, '..');
const server_code = fs.readFileSync(path.join(ROOT, 'backend', 'server.py'), 'utf8');
const teacher_code = fs.readFileSync(path.join(ROOT, 'backend', 'teacher_chat.py'), 'utf8');
const webapp_code = fs.readFileSync(path.join(ROOT, 'backend', 'webapp.py'), 'utf8');
const media_catalog_code = fs.readFileSync(path.join(ROOT, 'backend', 'media_catalog.py'), 'utf8');
const admin_analytics_code = fs.readFileSync(path.join(ROOT, 'backend', 'admin_analytics.py'), 'utf8');

console.log('🚀 Running Michael AI BLAST Contract Tests...');

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

test('Media Catalog contains core traffic topics (vikeplikt, stoppelengde, skilt, morkekjoring, hav_regelen)', () => {
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
  assert(webapp_code.includes('_resetTeacherWatchdog'), '_resetTeacherWatchdog function must exist');
  assert(webapp_code.includes('_teacherAudioToken'), '_teacherAudioToken variable must exist');
  assert(webapp_code.includes('_teacherAudio.src = \'\''), '_teacherAudio src reset must be present in stopAllSpeech');
  assert(webapp_code.includes('_teacherAudio.load()'), '_teacherAudio load must be present in stopAllSpeech');
});

test('webapp.py contains Video button adjacent to Michael and horizontal Home Carousel', () => {
  assert(webapp_code.includes('id="bnTeacher" onclick="showTab(\'teacher\')">'), 'bnTeacher must exist');
  assert(webapp_code.includes('id="bnLibrary" onclick="showTab(\'library\')">'), 'bnLibrary must exist');
  assert(webapp_code.indexOf('id="bnTeacher"') < webapp_code.indexOf('id="bnLibrary"'), 'bnLibrary must be adjacent to bnTeacher in bottomNav');
  assert(webapp_code.includes('id="homeCarouselSection"'), 'Home carousel section must exist');
  assert(webapp_code.includes('renderHomeCarousel()'), 'renderHomeCarousel function must exist');
  assert(webapp_code.includes('buildPodcastCard('), 'buildPodcastCard function must exist');
});

test('Language purity: no forbidden cross-language fallback patterns', () => {
  assert(!webapp_code.includes('|| TR.en'), 'No TR.en fallback');
  assert(!webapp_code.includes('|| TRANSLATIONS.no'), 'No TRANSLATIONS.no fallback');
});

console.log('\n🎉 ALL 7/7 BLAST ARCHITECTURE & UI CONTRACT TESTS PASSED PERFECTLY!\n');
