from fastapi import APIRouter
from fastapi.responses import HTMLResponse

quiz_web_router = APIRouter()

QUIZ_HTML = """<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Thai2Drive – Quiz</title>
<style>
  :root {
    --bg: #0B1226;
    --card-bg: rgba(255,255,255,.04);
    --border: rgba(255,255,255,.08);
    --orange: #FF9933;
    --orange-dark: #e6891f;
    --text: #E2E8F0;
    --muted: #94A3B8;
    --green: #10B981;
    --red: #EF4444;
    --radius: 12px;
    --nav-h: 64px;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* ── NAV ── */
  nav {
    position: sticky;
    top: 0;
    z-index: 100;
    height: var(--nav-h);
    background: rgba(11,18,38,.88);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    padding: 0 24px;
    gap: 24px;
  }

  .nav-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    color: var(--text);
    font-weight: 700;
    font-size: 1.1rem;
    flex-shrink: 0;
  }

  .nav-brand img {
    width: 34px;
    height: 34px;
    border-radius: 8px;
  }

  .nav-brand span { color: var(--orange); }

  .nav-links {
    display: flex;
    gap: 6px;
    list-style: none;
    margin-left: 8px;
  }

  .nav-links a {
    color: var(--muted);
    text-decoration: none;
    font-size: .875rem;
    padding: 6px 12px;
    border-radius: 8px;
    transition: color .2s, background .2s;
  }

  .nav-links a:hover { color: var(--text); background: var(--card-bg); }

  .nav-spacer { flex: 1; }

  .lang-pills {
    display: flex;
    gap: 6px;
  }

  .lang-pill {
    padding: 5px 13px;
    border-radius: 20px;
    border: 1px solid var(--border);
    background: var(--card-bg);
    color: var(--muted);
    font-size: .78rem;
    font-weight: 600;
    cursor: pointer;
    transition: all .2s;
    white-space: nowrap;
  }

  .lang-pill:hover { border-color: var(--orange); color: var(--text); }
  .lang-pill.active { background: var(--orange); border-color: var(--orange); color: #000; }

  /* ── MAIN ── */
  main {
    flex: 1;
    padding: 32px 20px 48px;
    max-width: 1000px;
    width: 100%;
    margin: 0 auto;
  }

  /* ── PROGRESS ── */
  .quiz-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    gap: 12px;
    flex-wrap: wrap;
  }

  .progress-label {
    font-size: .85rem;
    color: var(--muted);
    white-space: nowrap;
  }

  .progress-bar-wrap {
    flex: 1;
    height: 6px;
    background: var(--card-bg);
    border-radius: 99px;
    overflow: hidden;
    min-width: 80px;
  }

  .progress-bar-fill {
    height: 100%;
    background: var(--orange);
    border-radius: 99px;
    transition: width .4s ease;
  }

  .score-badge {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: .85rem;
    color: var(--text);
    white-space: nowrap;
  }

  .score-badge span { color: var(--green); font-weight: 700; }

  /* ── QUIZ CARD ── */
  .quiz-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px;
    display: grid;
    grid-template-columns: 55% 45%;
    gap: 28px;
    align-items: start;
  }

  .q-left { display: flex; flex-direction: column; gap: 16px; }

  .q-image {
    width: 100%;
    max-height: 320px;
    object-fit: contain;
    border-radius: 10px;
    background: rgba(255,255,255,.03);
    display: block;
  }

  .q-image-placeholder { display: none; }

  .q-text {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1.5;
  }

  /* ── RIGHT COLUMN ── */
  .q-right { display: flex; flex-direction: column; gap: 12px; }

  .q-lang-row {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 4px;
  }

  .q-lang-pill {
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--muted);
    font-size: .75rem;
    font-weight: 600;
    cursor: pointer;
    transition: all .2s;
  }

  .q-lang-pill:hover { border-color: var(--orange); color: var(--text); }
  .q-lang-pill.active { background: rgba(255,153,51,.18); border-color: var(--orange); color: var(--orange); }

  /* ── ANSWER BUTTONS ── */
  .answers { display: flex; flex-direction: column; gap: 8px; }

  .answer-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    background: rgba(255,255,255,.03);
    border: 1px solid var(--border);
    border-radius: 10px;
    cursor: pointer;
    text-align: left;
    color: var(--text);
    font-size: .9rem;
    transition: border-color .2s, background .2s, transform .1s;
    width: 100%;
  }

  .answer-btn:hover:not(:disabled) {
    border-color: var(--orange);
    background: rgba(255,153,51,.08);
  }

  .answer-btn:active:not(:disabled) { transform: scale(.99); }

  .answer-btn:disabled { cursor: default; }

  .answer-btn.correct {
    border-color: var(--green);
    background: rgba(16,185,129,.12);
  }

  .answer-btn.wrong {
    border-color: var(--red);
    background: rgba(239,68,68,.12);
  }

  .answer-btn.reveal {
    border-color: var(--green);
    background: rgba(16,185,129,.07);
  }

  .letter-badge {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(255,153,51,.15);
    color: var(--orange);
    font-size: .75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    transition: background .2s, color .2s;
  }

  .answer-btn.correct .letter-badge { background: var(--green); color: #fff; }
  .answer-btn.wrong .letter-badge { background: var(--red); color: #fff; }
  .answer-btn.reveal .letter-badge { background: var(--green); color: #fff; }

  .answer-text { flex: 1; line-height: 1.4; }

  /* ── EXPLANATION ── */
  .explanation {
    display: none;
    background: rgba(255,153,51,.07);
    border: 1px solid rgba(255,153,51,.25);
    border-radius: 10px;
    padding: 12px 14px;
    font-size: .85rem;
    color: var(--text);
    line-height: 1.5;
    margin-top: 4px;
  }

  .explanation.visible { display: block; }
  .explanation strong { color: var(--orange); font-size: .75rem; text-transform: uppercase; letter-spacing: .04em; display: block; margin-bottom: 4px; }

  /* ── NEXT BUTTON ── */
  .next-btn {
    display: none;
    width: 100%;
    padding: 13px;
    background: var(--orange);
    color: #000;
    font-weight: 700;
    font-size: .95rem;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: background .2s, transform .1s;
    margin-top: 4px;
  }

  .next-btn:hover { background: var(--orange-dark); }
  .next-btn:active { transform: scale(.99); }
  .next-btn.visible { display: block; }

  /* ── END SCREEN ── */
  #end-screen {
    display: none;
    text-align: center;
    padding: 48px 20px;
  }

  #end-screen.visible { display: block; }

  .end-emoji { font-size: 4rem; margin-bottom: 16px; }

  .end-score {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--orange);
    margin-bottom: 8px;
  }

  .end-label {
    font-size: 1rem;
    color: var(--muted);
    margin-bottom: 32px;
  }

  .retry-btn {
    padding: 13px 32px;
    background: var(--orange);
    color: #000;
    font-weight: 700;
    font-size: 1rem;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: background .2s;
  }

  .retry-btn:hover { background: var(--orange-dark); }

  /* ── LOADING ── */
  #loading-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 20px;
    gap: 16px;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border);
    border-top-color: var(--orange);
    border-radius: 50%;
    animation: spin .8s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── RESPONSIVE ── */
  @media (max-width: 700px) {
    .quiz-card {
      grid-template-columns: 1fr;
      padding: 20px;
      gap: 20px;
    }

    .q-lang-row { display: none; }

    nav { padding: 0 16px; gap: 12px; }
    .nav-links { display: none; }
  }
</style>
</head>
<body>

<!-- NAV -->
<nav>
  <a href="/api/website" class="nav-brand">
    <img src="/api/assets/developer-icon-512.png" alt="T2D">
    Thai<span>2Drive</span>
  </a>
  <ul class="nav-links">
    <li><a href="/api/website#features">Funksjoner</a></li>
    <li><a href="/api/website#pricing">Priser</a></li>
    <li><a href="/api/website#guide">Guide</a></li>
  </ul>
  <div class="nav-spacer"></div>
  <div class="lang-pills" id="nav-lang">
    <button class="lang-pill" data-lang="th" onclick="setLang('th')">🇹🇭 TH</button>
    <button class="lang-pill active" data-lang="no" onclick="setLang('no')">🇳🇴 NO</button>
    <button class="lang-pill" data-lang="en" onclick="setLang('en')">🇬🇧 EN</button>
  </div>
</nav>

<!-- MAIN -->
<main>

  <!-- LOADING -->
  <div id="loading-screen">
    <div class="spinner"></div>
    <p style="color:var(--muted);font-size:.9rem;">Laster spørsmål…</p>
  </div>

  <!-- QUIZ -->
  <div id="quiz-screen" style="display:none">
    <!-- Header -->
    <div class="quiz-header">
      <span class="progress-label" id="progress-label">Spørsmål 1 av 10</span>
      <div class="progress-bar-wrap">
        <div class="progress-bar-fill" id="progress-fill" style="width:10%"></div>
      </div>
      <div class="score-badge">✓ <span id="score-val">0</span></div>
    </div>

    <!-- Card -->
    <div class="quiz-card">
      <!-- LEFT -->
      <div class="q-left">
        <img id="q-img" class="q-image q-image-placeholder" src="" alt="">
        <p id="q-text" class="q-text"></p>
      </div>

      <!-- RIGHT -->
      <div class="q-right">
        <div class="q-lang-row">
          <button class="q-lang-pill" data-lang="th" onclick="setLang('th')">🇹🇭 TH</button>
          <button class="q-lang-pill active" data-lang="no" onclick="setLang('no')">🇳🇴 NO</button>
          <button class="q-lang-pill" data-lang="en" onclick="setLang('en')">🇬🇧 EN</button>
        </div>

        <div class="answers" id="answers"></div>

        <div class="explanation" id="explanation">
          <strong>Forklaring</strong>
          <span id="explanation-text"></span>
        </div>

        <button class="next-btn" id="next-btn" onclick="nextQuestion()">
          Neste spørsmål →
        </button>
      </div>
    </div>
  </div>

  <!-- END -->
  <div id="end-screen">
    <div class="end-emoji" id="end-emoji">🎉</div>
    <div class="end-score" id="end-score">0 / 10</div>
    <p class="end-label" id="end-label">Bra jobbet!</p>
    <button class="retry-btn" onclick="startQuiz()">Prøv igjen</button>
  </div>

</main>

<script>
  let questions = [];
  let current = 0;
  let score = 0;
  let lang = 'no';
  let answered = false;

  const labels = {
    no: { progress: 'Spørsmål', of: 'av', explanation: 'Forklaring', next: 'Neste spørsmål →', retry: 'Prøv igjen', loading: 'Laster spørsmål…', end_label_good: 'Bra jobbet!', end_label_ok: 'Fortsett å øve!', end_label_bad: 'Ikke gi opp!' },
    th: { progress: 'คำถาม', of: 'จาก', explanation: 'คำอธิบาย', next: 'ถัดไป →', retry: 'ลองอีกครั้ง', loading: 'กำลังโหลด…', end_label_good: 'ยอดเยี่ยม!', end_label_ok: 'ฝึกต่อไป!', end_label_bad: 'อย่าท้อแท้!' },
    en: { progress: 'Question', of: 'of', explanation: 'Explanation', next: 'Next question →', retry: 'Try again', loading: 'Loading questions…', end_label_good: 'Well done!', end_label_ok: 'Keep practising!', end_label_bad: "Don't give up!" },
  };

  function setLang(l) {
    lang = l;
    // update all pill buttons
    document.querySelectorAll('[data-lang]').forEach(el => {
      el.classList.toggle('active', el.dataset.lang === l);
    });
    if (questions.length && current < questions.length) renderQuestion(current);
  }

  function getField(q, base) {
    return q[base + '_' + lang] || q[base + '_no'] || q[base + '_en'] || '';
  }

  async function startQuiz() {
    questions = [];
    current = 0;
    score = 0;
    answered = false;

    document.getElementById('end-screen').classList.remove('visible');
    document.getElementById('end-screen').style.display = 'none';
    document.getElementById('quiz-screen').style.display = 'none';
    document.getElementById('loading-screen').style.display = 'flex';

    try {
      const res = await fetch('/api/questions/random?limit=10');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      questions = await res.json();
    } catch (e) {
      document.getElementById('loading-screen').innerHTML = '<p style="color:var(--red)">Feil ved lasting av spørsmål. Prøv igjen.</p>';
      return;
    }

    document.getElementById('loading-screen').style.display = 'none';
    document.getElementById('quiz-screen').style.display = 'block';
    renderQuestion(0);
  }

  function renderQuestion(idx) {
    const q = questions[idx];
    answered = false;

    // Progress
    const total = questions.length;
    const num = idx + 1;
    const pct = (num / total) * 100;
    document.getElementById('progress-label').textContent = labels[lang].progress + ' ' + num + ' ' + labels[lang].of + ' ' + total;
    document.getElementById('progress-fill').style.width = pct + '%';
    document.getElementById('score-val').textContent = score;

    // Image — only show proper traffic sign images (not app screenshots)
    // Images that are base64 data URIs starting with a known small size are likely real signs.
    // For now, only show http(s) URLs (not base64 screenshots from old data).
    const img = document.getElementById('q-img');
    const url = q.image_url || '';
    const isRealImage = url.startsWith('http') && url.length < 500;
    if (isRealImage) {
      img.src = url;
      img.style.display = 'block';
      img.onerror = () => { img.style.display = 'none'; };
    } else {
      img.style.display = 'none';
      img.src = '';
    }

    // Question text
    document.getElementById('q-text').textContent = getField(q, 'question_text');

    // Answers
    const answersEl = document.getElementById('answers');
    answersEl.innerHTML = '';
    ['a', 'b', 'c', 'd'].forEach(letter => {
      const text = getField(q, 'answer_' + letter);
      if (!text) return;
      const btn = document.createElement('button');
      btn.className = 'answer-btn';
      btn.dataset.letter = letter;
      btn.innerHTML = '<span class="letter-badge">' + letter.toUpperCase() + '</span><span class="answer-text">' + escHtml(text) + '</span>';
      btn.addEventListener('click', () => selectAnswer(letter));
      answersEl.appendChild(btn);
    });

    // Explanation
    const expEl = document.getElementById('explanation');
    expEl.classList.remove('visible');
    document.getElementById('explanation-text').textContent = '';
    document.querySelector('#explanation strong').textContent = labels[lang].explanation;

    // Next btn
    const nextBtn = document.getElementById('next-btn');
    nextBtn.classList.remove('visible');
    nextBtn.textContent = idx + 1 < questions.length ? labels[lang].next : (lang === 'no' ? 'Se resultat →' : lang === 'th' ? 'ดูผล →' : 'See result →');
  }

  function selectAnswer(chosen) {
    if (answered) return;
    answered = true;

    const q = questions[current];
    const correct = q.correct_answer;
    const btns = document.querySelectorAll('.answer-btn');

    btns.forEach(btn => {
      btn.disabled = true;
      const l = btn.dataset.letter;
      if (l === correct && l === chosen) {
        btn.classList.add('correct');
      } else if (l === chosen && l !== correct) {
        btn.classList.add('wrong');
      } else if (l === correct) {
        btn.classList.add('reveal');
      }
    });

    if (chosen === correct) score++;
    document.getElementById('score-val').textContent = score;

    // Explanation
    const expText = getField(q, 'explanation');
    if (expText) {
      document.querySelector('#explanation strong').textContent = labels[lang].explanation;
      document.getElementById('explanation-text').textContent = expText;
      document.getElementById('explanation').classList.add('visible');
    }

    document.getElementById('next-btn').classList.add('visible');
  }

  function nextQuestion() {
    current++;
    if (current >= questions.length) {
      showEnd();
    } else {
      renderQuestion(current);
    }
  }

  function showEnd() {
    document.getElementById('quiz-screen').style.display = 'none';
    const endEl = document.getElementById('end-screen');
    endEl.style.display = 'block';
    endEl.classList.add('visible');

    const total = questions.length;
    const pct = score / total;

    document.getElementById('end-score').textContent = score + ' / ' + total;
    document.getElementById('end-emoji').textContent = pct >= .8 ? '🏆' : pct >= .5 ? '👍' : '💪';

    const lbl = labels[lang];
    document.getElementById('end-label').textContent = pct >= .8 ? lbl.end_label_good : pct >= .5 ? lbl.end_label_ok : lbl.end_label_bad;
    document.querySelector('.retry-btn').textContent = lbl.retry;
  }

  function escHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // Kick off
  startQuiz();
</script>
</body>
</html>"""


@quiz_web_router.get("/quiz", response_class=HTMLResponse)
async def quiz_web_page():
    return HTMLResponse(content=QUIZ_HTML)
