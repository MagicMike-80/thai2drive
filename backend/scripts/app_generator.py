"""
Thai2Drive - Generator App
Lokal web-app for å generere spørsmål fra bilder.
"""

import asyncio
import base64
import json
import os
import sys
import uuid
import threading
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import anthropic
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

load_dotenv(override=True)

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    with open(env_path) as f:
        for line in f:
            if line.startswith("ANTHROPIC_API_KEY="):
                api_key = line.strip().split("=", 1)[1]
                break

ai_client = anthropic.Anthropic(api_key=api_key)
LETTERS = ["A", "B", "C", "D"]

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

HTML = """<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Thai2Drive Generator</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0f0f1a; color: #e0e0f0; font-family: 'Segoe UI', sans-serif; min-height: 100vh; }
.header { background: #1a1a2e; padding: 16px 24px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #2a2a4a; }
.header h1 { font-size: 20px; color: #fff; }
.header span { font-size: 24px; }
.container { max-width: 900px; margin: 0 auto; padding: 24px; }
.drop-zone { border: 2px dashed #4a4a8a; border-radius: 16px; padding: 40px; text-align: center; cursor: pointer; transition: all 0.3s; background: #1a1a2e; margin-bottom: 24px; }
.drop-zone:hover, .drop-zone.drag-over { border-color: #6c63ff; background: #1e1e35; }
.drop-zone p { color: #8888aa; margin-top: 8px; font-size: 14px; }
.drop-zone .icon { font-size: 48px; margin-bottom: 8px; }
#imagePreview { display: none; margin-bottom: 24px; text-align: center; }
#imagePreview img { max-width: 100%; max-height: 400px; border-radius: 12px; border: 1px solid #2a2a4a; }
.btn { padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: 600; transition: all 0.2s; }
.btn-primary { background: #6c63ff; color: white; width: 100%; margin-bottom: 24px; font-size: 16px; padding: 16px; }
.btn-primary:hover { background: #5a52d5; }
.btn-primary:disabled { background: #3a3a5a; cursor: not-allowed; }
.btn-success { background: #22c55e; color: white; }
.btn-success:hover { background: #16a34a; }
.btn-download { background: #3b82f6; color: white; }
.btn-download:hover { background: #2563eb; }
.actions { display: flex; gap: 12px; margin-top: 24px; }
.actions .btn { flex: 1; }
.status { padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; font-size: 14px; display: none; }
.status.loading { background: #1e3a5f; border: 1px solid #3b82f6; color: #93c5fd; display: block; }
.status.success { background: #14532d; border: 1px solid #22c55e; color: #86efac; display: block; }
.status.error { background: #450a0a; border: 1px solid #ef4444; color: #fca5a5; display: block; }
.questions { display: none; }
.question-card { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
.question-card h3 { font-size: 13px; color: #6c63ff; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.question-text { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #fff; }
.options { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; }
.option { padding: 10px 14px; border-radius: 8px; font-size: 14px; background: #0f0f1a; border: 1px solid #2a2a4a; }
.option.correct { background: #14532d; border-color: #22c55e; color: #86efac; }
.difficulty { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.difficulty.easy { background: #14532d; color: #86efac; }
.difficulty.medium { background: #1e3a5f; color: #93c5fd; }
.difficulty.hard { background: #450a0a; color: #fca5a5; }
.meta { display: flex; gap: 8px; align-items: center; margin-bottom: 12px; }
.category { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 12px; background: #2a2a4a; color: #aaaacc; }
input[type=file] { display: none; }
.spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid #ffffff44; border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite; margin-right: 8px; vertical-align: middle; }
@keyframes spin { to { transform: rotate(360deg); } }
.count-badge { background: #6c63ff; color: white; border-radius: 20px; padding: 2px 10px; font-size: 13px; margin-left: 8px; }
</style>
</head>
<body>
<div class="header">
  <span>🚗</span>
  <h1>Thai2Drive Generator</h1>
</div>
<div class="container">
  <div class="drop-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
    <div class="icon">📸</div>
    <p><strong>Klikk eller dra et bilde hit</strong></p>
    <p>Støtter: jpg, jpeg, png, webp</p>
  </div>
  <input type="file" id="fileInput" accept=".jpg,.jpeg,.png,.webp">

  <div id="imagePreview">
    <img id="previewImg" src="" alt="Valgt bilde">
  </div>

  <div class="status" id="status"></div>

  <button class="btn btn-primary" id="generateBtn" onclick="generate()" disabled>
    ✨ Generer spørsmål fra bilde
  </button>

  <div class="questions" id="questions">
    <h2 style="margin-bottom:16px; color:#fff">Genererte spørsmål <span class="count-badge" id="countBadge">0</span></h2>
    <div id="questionList"></div>
    <div class="actions">
      <button class="btn btn-success" onclick="saveToDatabase()">💾 Lagre i database</button>
      <button class="btn btn-download" onclick="downloadJSON()">📥 Last ned til PC</button>
    </div>
  </div>
</div>

<script>
let currentImage = null;
let currentQuestions = [];

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});
fileInput.addEventListener('change', e => { if (e.target.files[0]) handleFile(e.target.files[0]); });

function handleFile(file) {
  const reader = new FileReader();
  reader.onload = e => {
    currentImage = { data: e.target.result, name: file.name, type: file.type };
    document.getElementById('previewImg').src = e.target.result;
    document.getElementById('imagePreview').style.display = 'block';
    document.getElementById('generateBtn').disabled = false;
    document.getElementById('questions').style.display = 'none';
    document.getElementById('status').style.display = 'none';
    currentQuestions = [];
  };
  reader.readAsDataURL(file);
}

async function generate() {
  if (!currentImage) return;

  const btn = document.getElementById('generateBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Claude analyserer bildet...';

  showStatus('loading', 'Claude analyserer bildet og genererer spørsmål...');

  const formData = new FormData();
  const blob = dataURLToBlob(currentImage.data);
  formData.append('file', blob, currentImage.name);

  try {
    const res = await fetch('/generate', { method: 'POST', body: formData });
    const data = await res.json();

    if (data.error) {
      showStatus('error', '❌ ' + data.error);
    } else if (data.questions.length === 0) {
      showStatus('error', '❌ Bildet er ikke egnet (kanskje et app-skjermbilde?). Prøv et bilde av en trafikksituasjon eller trafikkskilt.');
    } else {
      currentQuestions = data.questions;
      renderQuestions(data.questions);
      showStatus('success', '✅ ' + data.questions.length + ' spørsmål generert!');
    }
  } catch (err) {
    showStatus('error', '❌ Feil: ' + err.message);
  }

  btn.disabled = false;
  btn.innerHTML = '✨ Generer spørsmål fra bilde';
}

function renderQuestions(questions) {
  const list = document.getElementById('questionList');
  document.getElementById('countBadge').textContent = questions.length;
  list.innerHTML = questions.map((q, i) => {
    const opts = q.options.map(o =>
      `<div class="option ${o.id === q.correctOptionId ? 'correct' : ''}">
        <strong>${o.id}</strong> ${o.text.no} ${o.id === q.correctOptionId ? '✅' : ''}
      </div>`
    ).join('');
    const diff = q.difficulty || 'medium';
    return `<div class="question-card">
      <div class="meta">
        <h3>Spørsmål ${i+1}</h3>
        <span class="category">${q.category || 'Traffic'}</span>
        <span class="difficulty ${diff}">${diff}</span>
      </div>
      <div class="question-text">${q.question.no}</div>
      <div class="options">${opts}</div>
      <small style="color:#6666aa">🇹🇭 ${q.question.th}</small>
    </div>`;
  }).join('');
  document.getElementById('questions').style.display = 'block';
}

async function saveToDatabase() {
  if (!currentQuestions.length) return;
  showStatus('loading', 'Lagrer i database...');
  try {
    const res = await fetch('/save', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ questions: currentQuestions, imageData: currentImage.data })
    });
    const data = await res.json();
    showStatus('success', `✅ ${data.inserted} nye spørsmål lagret! Totalt i DB: ${data.total}`);
  } catch (err) {
    showStatus('error', '❌ Feil: ' + err.message);
  }
}

function downloadJSON() {
  if (!currentQuestions.length) return;
  const blob = new Blob([JSON.stringify(currentQuestions, null, 2)], {type: 'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'thai2drive_questions_' + Date.now() + '.json';
  a.click();
}

function showStatus(type, msg) {
  const el = document.getElementById('status');
  el.className = 'status ' + type;
  el.textContent = msg;
}

function dataURLToBlob(dataURL) {
  const arr = dataURL.split(',');
  const mime = arr[0].match(/:(.*?);/)[1];
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  while (n--) u8arr[n] = bstr.charCodeAt(n);
  return new Blob([u8arr], {type: mime});
}
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML


@app.post("/generate")
async def generate(file: UploadFile = File(...)):
    try:
        img_data = await file.read()
        img_b64 = base64.standard_b64encode(img_data).decode("utf-8")
        media_type = file.content_type or "image/jpeg"

        prompt = """Du er ekspert på norsk vegtrafikkloven og trafikkregler.

Se nøye på bildet og vurder hva det viser:
- Hvis bildet er et SKJERMBILDE av en app, nettside eller quiz → returner []
- Hvis bildet viser en TRAFIKKSITUASJON, trafikkskilt, vei → lag 5 spørsmål
- Hvis bildet er fra en bok med trafikkregler → lag 5 spørsmål

Lag 5 spørsmål til norsk teoriprøve (klasse B).
- Spørsmål MÅ stemme med norsk vegtrafikkloven
- 4 alternativer (A, B, C, D), kun ETT riktig
- VIKTIG: correctOptionId MÅ variere — bruk en blanding av A, B, C og D på tvers av spørsmålene. IKKE bruk samme bokstav på alle spørsmål!
- Bland rekkefølgen på alternativene slik at riktig svar ikke alltid er på samme plass
- Alle tekster på tre språk: norsk (no), thai (th), engelsk (en)
- Varier vanskelighetsgrad (easy/medium/hard)

Svar KUN med JSON-array (eller [] hvis bildet ikke er egnet):
[{"question":{"no":"...","th":"...","en":"..."},"options":[{"id":"A","text":{"no":"...","th":"...","en":"..."}},{"id":"B","text":{"no":"...","th":"...","en":"..."}},{"id":"C","text":{"no":"...","th":"...","en":"..."}},{"id":"D","text":{"no":"...","th":"...","en":"..."}}],"correctOptionId":"A","difficulty":"medium","category":"Traffic Signs","explanation":{"no":"...","th":"...","en":"..."}}]"""

        response = ai_client.messages.create(
            model="claude-opus-4-7",
            max_tokens=6000,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img_b64}},
                    {"type": "text", "text": prompt}
                ]
            }]
        )

        text = response.content[0].text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.rsplit("```", 1)[0]

        questions = json.loads(text.strip())
        return {"questions": questions}

    except Exception as e:
        return {"error": str(e), "questions": []}


@app.post("/save")
async def save(data: dict):
    try:
        questions = data.get("questions", [])
        image_data = data.get("imageData", "")

        mongo_url = os.environ.get("MONGO_URL")
        if not mongo_url:
            env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
            with open(env_path) as f:
                for line in f:
                    if line.startswith("MONGO_URL="):
                        mongo_url = line.strip().split("=", 1)[1].strip('"')

        db_client = AsyncIOMotorClient(mongo_url)
        db = db_client["thai2drive"]

        inserted = 0
        skipped = 0

        for q in questions:
            existing = await db.questions.find_one({"question.no": q["question"]["no"]})
            if existing:
                skipped += 1
                continue

            doc = {
                "id": str(uuid.uuid4()),
                "question": q["question"],
                "options": q["options"],
                "correctOptionId": q["correctOptionId"],
                "explanation": q.get("explanation", {}),
                "bildeUrl": None,
                "category": q.get("category", "Traffic Rules"),
                "difficulty": q.get("difficulty", "medium"),
                "active": True,
                "schema_version": 2,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "generated_by": "app_generator"
            }
            await db.questions.insert_one(doc)
            inserted += 1

        total = await db.questions.count_documents({})
        db_client.close()

        return {"inserted": inserted, "skipped": skipped, "total": total}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def open_browser():
    import time
    time.sleep(1.5)
    webbrowser.open("http://localhost:7788")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  Thai2Drive Generator App")
    print("="*50)
    print("  Åpner i nettleseren din...")
    print("  Trykk Ctrl+C for å avslutte")
    print("="*50 + "\n")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=7788, log_level="error")
