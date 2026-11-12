const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'backend', 'webapp.py'), 'utf8');
const globals = source.slice(source.indexOf('var _globalAudio = null;'),
  source.indexOf("window.addEventListener('pagehide', stopAllSpeech)"));
const teacher = source.slice(source.indexOf('function speakQ() {'),
  source.indexOf('function buildPodcastCard('));
assert.ok(globals && teacher);

function setup() {
  const timers = new Map(), rejections = [], spoken = [];
  let nextTimer = 0, cancellations = 0;
  const audio = {
    paused: true, volume: 1, currentTime: 0,
    load() {}, pause() { this.paused = true; },
    play() { return {catch(fn) { rejections.push(fn); }}; },
  };
  const context = {
    Audio: function() { return audio; }, appLang: 'th', ttsRate: 1, ttsVolume: 1,
    ttsPlaying: false, questions: [{question: 'Thai question'}], qIdx: 0,
    pickLang: text => text, pickField: () => '',
    document: {getElementById: () => null}, localeForLangKey: lang => lang,
    ttsStreamUrl: (text, lang) => `${lang}:${text}`,
    console: {warn() {}, error() {}},
    setTimeout(fn, ms) { timers.set(++nextTimer, {fn, ms}); return nextTimer; },
    clearTimeout(id) { timers.delete(id); },
    SpeechSynthesisUtterance: function(text) { this.text = text; },
  };
  context.window = {
    SpeechSynthesisUtterance: context.SpeechSynthesisUtterance,
    speechSynthesis: {cancel() { cancellations++; }, speak(utterance) { spoken.push(utterance); }},
  };
  vm.createContext(context);
  vm.runInContext(globals + teacher, context);
  return {context, audio, timers, rejections, spoken, get cancellations() { return cancellations; }};
}

test('Michael MP3 rejection starts browser fallback without a later timeout cancelling speech', () => {
  const s = setup();
  s.context.speakText('Thai reply');
  s.rejections[0](new Error('No supported audio source'));
  assert.equal(s.spoken.length, 1);
  assert.equal(s.spoken[0].lang, 'th');
  assert.equal(s.context._teacherTtsPlaying, true);
  const before = s.cancellations;
  for (const timer of s.timers.values()) timer.fn();
  assert.equal(s.cancellations, before);
  assert.equal(s.context._teacherTtsPlaying, true);
  s.spoken[0].onend();
  assert.equal(s.context._teacherTtsPlaying, false);
});

test('audio error event also removes the timeout before browser fallback', () => {
  const s = setup();
  s.context.speakText('Thai reply');
  s.audio.onerror();
  assert.equal(s.spoken.length, 1);
  assert.equal(s.timers.size, 0);
});

test('an old rejected play cannot consume or reset a new Michael reply', () => {
  const s = setup();
  s.context.speakText('Old reply');
  s.context.speakText('New reply');
  s.rejections[0](new Error('Old request aborted'));
  assert.equal(s.spoken.length, 0);
  assert.equal(s.context._teacherActiveText, 'New reply');
  assert.equal(s.context._pendingTtsFallback.text, 'New reply');
  s.rejections[1](new Error('Current MP3 failed'));
  assert.equal(s.spoken.length, 1);
  assert.equal(s.spoken[0].text, 'New reply');
});

test('stopping speech clears timers and late rejection cannot restart speech', () => {
  const s = setup();
  s.context.speakText('Thai reply');
  s.context.stopAllSpeech();
  s.rejections[0](new Error('Aborted'));
  assert.equal(s.spoken.length, 0);
  assert.equal(s.timers.size, 0);
  assert.equal(s.context._teacherTtsPlaying, false);
});

test('successful MP3 completion releases playback state and pending timers', () => {
  const s = setup();
  s.context.speakText('Thai reply');
  s.audio.paused = false;
  s.audio.onended();
  assert.equal(s.spoken.length, 0);
  assert.equal(s.timers.size, 0);
  assert.equal(s.context._teacherTtsPlaying, false);
});

test('same reply still toggles off and a current failed source releases state without speech support', () => {
  const s = setup();
  s.context.speakText('Thai reply');
  s.context.speakText('Thai reply');
  assert.equal(s.context._teacherTtsPlaying, false);
  delete s.context.window.speechSynthesis;
  s.context.speakText('Another reply');
  s.rejections[1](new Error('No supported audio source'));
  assert.equal(s.context._teacherTtsPlaying, false);
  assert.equal(s.spoken.length, 0);
});

test('shared cleanup also preserves browser speech for a quiz question', () => {
  const s = setup();
  s.context.speakQ();
  s.rejections[0](new Error('No supported audio source'));
  assert.equal(s.spoken[0].text, 'Thai question');
  assert.equal(s.context.ttsPlaying, true);
  assert.equal(s.timers.size, 0);
  s.spoken[0].onend();
  assert.equal(s.context.ttsPlaying, false);
});
