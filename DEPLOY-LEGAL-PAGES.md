# Deploying the 3 Legal Pages to Your Live Netlify Site

**What I verified:** Your live site `thai2drive.no` is hosted on **Netlify** and uses a different design than `/app/website/`. So I rebuilt the 3 legal pages to match your live site's exact dark navy + orange (#ff982f) theme.

**Files ready in:** `/app/legal-pages-for-netlify/`
- `privacy.html` — 14 KB, trilingual NO/TH/EN, GDPR-compliant
- `terms.html` — 14 KB, trilingual, covers Google Play subscription rules
- `support.html` — 10 KB, trilingual, FAQ + email button
- `_redirects` — 254 B, makes `/privacy`, `/terms`, `/support` work as clean URLs

**Tested locally:** All 3 pages return HTTP 200, parse as valid HTML, and render correctly with working language switcher (NO/TH/EN).

---

## How to deploy (pick ONE method)

### Method A — Drag-and-drop on Netlify (fastest, 2 min)

1. Open https://app.netlify.com
2. Click your `thai2drive.no` site
3. Click **Deploys** → scroll down to **Drag and drop your site folder here**
4. **Important:** Don't drop just the legal folder. Find your CURRENT live deploy, download it (Netlify → Deploys → click latest deploy → "Download deploy" button), unzip, **add my 4 files into the same folder**, then drag the merged folder back.
5. Wait ~30 sec for deploy to finish
6. Test the URLs (see below)

> ⚠️ **Why merge?** A drag-and-drop deploy on Netlify REPLACES the entire site. If you drop just the 3 legal files, your landing page disappears. Always drop the FULL site contents.

### Method B — If your site is on Netlify via GitHub (cleaner)

1. Find which GitHub repo Netlify deploys from:
   - Netlify → your site → **Site settings** → **Build & deploy** → **Continuous deployment** → "Build settings" shows `Repository: github.com/.../...`
2. Tell me which repo it is, OR clone it locally:
   ```
   git clone <that-repo>
   cd <repo>
   ```
3. Copy my 4 files to the repo's deploy root (the same folder that has the existing `index.html`):
   ```
   cp /app/legal-pages-for-netlify/privacy.html .
   cp /app/legal-pages-for-netlify/terms.html .
   cp /app/legal-pages-for-netlify/support.html .
   cp /app/legal-pages-for-netlify/_redirects .
   ```
4. `git add . && git commit -m "Add legal pages for Play Store" && git push`
5. Netlify auto-deploys in ~60 sec.

---

## Verification checklist (run AFTER deploying)

These commands check the live site exactly the way Google Play review will:

```bash
# All three should return HTTP 200 (not 404, not 301):
curl -sI https://www.thai2drive.no/privacy | head -1
curl -sI https://www.thai2drive.no/terms   | head -1
curl -sI https://www.thai2drive.no/support | head -1

# Optional: also test apex domain (might 301 redirect to www, that's fine)
curl -sIL https://thai2drive.no/privacy | tail -5
```

Or in browser, open all 3:
- https://www.thai2drive.no/privacy
- https://www.thai2drive.no/terms
- https://www.thai2drive.no/support

Each should show:
- ✅ T2D logo in top-left header (horizontal layout, not stacked)
- ✅ Language switcher NO/TH/EN in top-right (clicking changes the body text)
- ✅ "← Tilbake" back link
- ✅ Headlines in current language
- ✅ Footer with cross-links to the other 2 pages

If any URL still returns 404, the `_redirects` file didn't deploy. Confirm it's in the same folder as your `index.html` on Netlify (case-sensitive, no `.txt` extension).

---

## After deploy succeeds, paste in chat

```
✓ https://www.thai2drive.no/privacy → 200 OK
✓ https://www.thai2drive.no/terms   → 200 OK
✓ https://www.thai2drive.no/support → 200 OK
✓ ready for Play Console privacy policy URL
```

Then we move on to Play Console Stage 1 in `PRODUCTION-SETUP.md`.

---

## What NOT to do

- ❌ Don't drag-and-drop just the 3 files — you'll wipe your landing page
- ❌ Don't rename `_redirects` → must be exact name, no extension
- ❌ Don't put files in a subfolder — they must be at the deploy root, same level as `index.html`
- ❌ Don't worry about the apex `thai2drive.no` vs `www.thai2drive.no` — Google Play accepts either as the privacy URL
