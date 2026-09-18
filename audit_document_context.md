# Fase 4 Audit: PDF-håndtering & Dokumentkontekst i Backend (TASK-007)

**Dato:** 18. september 2026  
**Repository:** `MagicMike-80/thai2drive`  
**Branch:** `audit/document-context`  
**Status:** Fullført (Ingen kildekode endret)

---

## Sammendrag & Hovedfunn

Denne rapporten kartlegger eksisterende backend-arkitektur og kodebase for å forberede innføring av elev-opplastede notater/PDF-er i Michael AI Chat.

| Område | Nåværende status i kodebasen | Merknader |
| :--- | :--- | :--- |
| **PDF-parsing (runtime)** | ❌ **Mangler fullstendig** | Ingen PDF-tekstekstraksjonsbiblioteker (`pypdf`, `pdfplumber`, `fitz`) i `requirements.txt`. |
| **Filopplasting** | ✅ **Delvis på plass** | `python-multipart` og `UploadFile` brukes i admin-ruter (`/api/admin/media/upload`). |
| **Dokumentlagring** | ⚠️ **Kun rå GridFS (admin)** | `media_storage.py` støtter `application/pdf` opptil 40 MB til GridFS, men kun for admin. Ingen elev-samlinger. |
| **Database-schema** | ❌ **Ingen elevdokument-schema** | Ingen `user_documents` eller `uploads`-samling i MongoDB. |
| **Pensumskille (RAG)** | ⚠️ **100 % lukket system** | All kontekst i `teacher_chat.py` forventes å stamme fra godkjente samlinger (`studiebok_chapters` etc.). |
| **Tester for elev-docs** | ❌ **Ingen tester** | Eksisterende tester dekker kun admin-media CRUD og mime-validering. |

---

## Detaljert Besvarelse av de 6 Punktene

### 1. Finnes det allerede et endepunkt eller modul for filopplasting / PDF-parsing i `backend/`?

- **Filopplasting (Multipart Upload):**
  - Ja, infrastrukturen for mottak av filer finnes via FastAPI og `python-multipart==0.0.24`.
  - Hovedendepunktet for opplasting er i dag begrenset til administratorer:
    - `POST /api/admin/media/upload` ([`server.py:5448`](file:///d:/thai2drive-main/work/thai2drive/backend/server.py#L5448)): Tar imot `file: UploadFile = File(...)` med `require_admin`.
    - Bruker hjelpefunksjonen `prepare_media_upload` fra [`media_storage.py:38`](file:///d:/thai2drive-main/work/thai2drive/backend/media_storage.py#L38).
    - Lagrer rå binærdata i MongoDB GridFS (`AsyncIOMotorGridFSBucket(db)`).
    - `ALLOWED_MEDIA_TYPES` i `media_storage.py` definerer allerede `"application/pdf": ("document", ".pdf", 40 * 1024 * 1024)`.
    - Offentlig streaming-endepunkt finnes: `GET /api/media/files/{file_id}`.
- **PDF-parsing (Tekstekstraksjon):**
  - **Nei, det finnes ingen runtime-modul eller endepunkt for PDF-parsing.**
  - `fitz` (PyMuPDF) er referert i to *offline utviklings-/migreringsskripter*:
    - `import_questions.py` (ekstraksjon av bilder fra lokal PDF-fil på hardkodet Windows-sti).
    - `scripts/generate_from_pdf.py` og `scripts/generate_from_pdf_smart.py` (offline spørsmålsgenerator).
  - Ingen av disse er eksponert via FastAPI eller operative i Railway-produksjon.

---

### 2. Finnes det et schema eller MongoDB-collection for lagring av brukerdokumenter (f.eks. `user_documents`, `uploads`)?

- **Nei.** Gjennomgang av alle MongoDB-kall i kildekoden viser at det verken eksisterer collections eller Pydantic-modeller for brukerdokumenter.
- Eksisterende dokument- og medielagring er strengt admin- og innholdskuratert:
  - `media_catalog` (kuraterte videoer, podcaster, illustrasjoner).
  - `michael_materials` (pedagogiske ressurser knyttet til læringsemner).
  - `fs.files` / `fs.chunks` (MongoDB GridFS for råfiler).
- Brukerspesifikke collections per i dag er kun:
  - `users`, `user_progress`, `user_mistakes`, `quiz_attempts`, `bookmarks`, `exam_simulations`, `teacher_chats`, `teacher_chat_logs`.
- For å støtte elevopplastede notater må det opprettes et nytt schema og collection (f.eks. `user_documents` med `user_id`, `device_id`, `filename`, `file_id`, `extracted_text`, `status`, `created_at`).

---

### 3. Hvordan skiller koden i dag mellom Thai2Drive sine egne pensumkilder (`studiebok_chapters`, `learning_glossary`) og eventuelle eksterne kilder?

- **Koden skiller i dag ikke mellom interne og eksterne kilder fordi systemet er 100 % lukket om autoritativt pensum.**
- I [`backend/teacher_chat.py`](file:///d:/thai2drive-main/work/thai2drive/backend/teacher_chat.py#L2358) henter `_get_curriculum_context(user_msg, lang)` kun data fra:
  - `studiebok_chapters` (kapitteltitler og innhold filtrert på aktivt språk).
  - `learning_glossary` (autoritative fagtermer og definisjoner).
  - `traffic_signs` (offisielle skiltnummer, navn og forklaringer).
  - `learning_videos` og `michael_materials`.
- Alt dette settes sammen til en flat tekstblokk merket:
  ```text
  === CURRICULUM KNOWLEDGE BASE (OFFICIAL NORWEGIAN DRIVING THEORY) ===
  Studybook Chapter {order}: {title}
  Content: {clean_content}
  ```
- System-instruksjonene for Michael instruerer eksplisitt om at han er en norsk trafikklærer som kun formidler fasit etter Vegtrafikkloven § 3 og offisielle regler.
- **Konklusjon:** Skal eksterne elevnotater innføres, må det etableres et krystallklart skille i prompten (f.eks. en adskilt `<student_notes>`-seksjon) slik at elevens egne notater aldri forveksles med eller overstyrer den offisielle teorifasiten.

---

### 4. Hvilke PDF- eller dokumentavhengigheter finnes i `requirements.txt`?

- **Ingen PDF-biblioteker finnes i `requirements.txt`.**
  - Verken `pypdf`, `pdfplumber`, `PyMuPDF` (`fitz`), `pypdf2` eller `pdfminer` er installert.
- Eksisterende relaterte biblioteker i `requirements.txt`:
  - `python-multipart==0.0.24` (nødvendig for FastAPI `UploadFile`)
  - `aiofiles==24.1.0` (asynkron lesing/skriving av filer)
  - `pillow==12.2.0` (bildehåndtering og konvertering)
  - `markdown-it-py==4.0.0` (markdown parsing)
- **Anbefaling for Fase 4:** Installere `pypdf` (ren Python, lettvektig, ingen C-kompileringsproblemer på Railway/Linux) for rask og sikker tekstekstraksjon.

---

### 5. Finnes det eksisterende tester for dokumenthåndtering?

- **Ja, men kun for administratoropplasting og mediekatalog:**
  - [`tests/test_media_storage.py`](file:///d:/thai2drive-main/work/thai2drive/tests/test_media_storage.py): Tester filstørrelsesvalidering, MIME-type deteksjon og formatgrenser i `prepare_media_upload` (inkludert PDF opptil 40 MB).
  - [`backend/tests/test_admin_media_crud.py`](file:///d:/thai2drive-main/work/thai2drive/backend/tests/test_admin_media_crud.py): Tester opplasting av mediefiler til GridFS via mocked bucket.
  - [`tests/test_michael_media_cards_contract.py`](file:///d:/thai2drive-main/work/thai2drive/tests/test_michael_media_cards_contract.py): Tester frontend-rendering for `media.type === 'document'`.
- **Nei for elev/PDF:**
  - Det finnes **ingen** tester for bruker-opplastede dokumenter.
  - Det finnes **ingen** tester for PDF-tekstekstraksjon.
  - Det finnes **ingen** tester for dokumentkontekst i elevchatten.

---

### 6. Hva er den minste trygge måten å utvide `TeacherChatRequest` på til å ta imot en valgfri `document_id` eller `document_context`?

I [`backend/teacher_chat.py:2822`](file:///d:/thai2drive-main/work/thai2drive/backend/teacher_chat.py#L2822) utvides `TeacherChatRequest` med to valgfrie felter med standardverdi `None`:

```python
class TeacherChatRequest(BaseModel):
    message: str = Field(..., max_length=2000)
    language: str = Field("no", pattern="^(no|th|en)$")
    session_id: Optional[str] = Field(default=None)
    conversation_id: Optional[str] = Field(default=None)
    device_id: Optional[str] = None
    user_id: Optional[str] = None
    mode: Literal["normal_chat", "quiz_coach"] = "normal_chat"
    # ── Fase 4: Valgfri dokumentkontekst ──
    document_id: Optional[str] = Field(default=None, max_length=64)
    document_context: Optional[str] = Field(default=None, max_length=4000)
```

#### Hvorfor dette er den minste og tryggeste løsningen:
1. **100 % bakoverkompatibelt:** Begge feltene er `Optional` med `default=None`. Ingen eksisterende kall fra web eller mobil brekker.
2. **Beskyttelse mot overbelastning:** `max_length=4000` på `document_context` forhindrer prompt-injection og token-exhaustion.
3. **Fleksibilitet:**
   - `document_id`: Backend kan slå opp ferdig parsede notater i MongoDB (med sjekk på at dokumentet tilhører gjeldende `user_id`/`device_id`).
   - `document_context`: Tillater direkte sending av en ren tekstsnutt fra en elev-notis eller forhåndsvisning.
4. **Skille i system-prompt:**
   I `teacher_chat()` pakkes teksten inn i en avgrenset XML-seksjon:
   ```xml
   <student_document_notes>
   {sanitized_text}
   </student_document_notes>
   ```
   og instruerer Michael:
   - *"Eleven har lagt ved egne notater/dokumenter. Forklar og svar på elevens spørsmål med utgangspunkt i notatene, men rett opp pedagogisk dersom notatene strider mot de offisielle trafikkreglene i pensum. Svar 100 % på elevens valgte språk."*
