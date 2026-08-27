/* global __dirname */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const screens = ['teacher.tsx', 'quiz.tsx', 'book.tsx'].map((file) =>
  fs.readFileSync(path.join(root, 'app', file), 'utf8')
);
const apiSource = fs.readFileSync(path.join(root, 'src', 'services', 'api.ts'), 'utf8');

assert.equal(screens.filter((source) => source.includes('buildTtsUrl(')).length, 3);
assert.ok(screens.every((source) => !/EXPO_PUBLIC_BACKEND_URL[^\n]*\/api\/tts/.test(source)));
assert.ok(apiSource.includes("no: 'nb-NO'"));
assert.ok(apiSource.includes("th: 'th-TH'"));
assert.ok(apiSource.includes("en: 'en-US'"));
assert.ok(apiSource.includes('encodeURIComponent(locale)'));
assert.ok(apiSource.includes('encodeURIComponent(text)'));

console.log('TTS URL contract verified for Teacher, quiz, and book.');
