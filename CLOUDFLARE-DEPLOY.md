# Thai2Drive Website — Cloudflare Pages Deployment Guide

**Goal:** Deploy `/app/website/` to Cloudflare Pages → attach domain `thai2drive.no` → verify `/privacy`, `/terms`, `/support` all load clean for Play Store review.

**Time:** 15–30 minutes the first time.

---

## What you need before starting
- [ ] A Cloudflare account (free) — https://dash.cloudflare.com/sign-up
- [ ] Your domain `thai2drive.no` (already owned)
- [ ] DNS control at your registrar (wherever you bought `thai2drive.no` — probably Domeneshop, One.com, etc.)
- [ ] 10 minutes

---

## Path A — Deploy via GitHub (recommended, auto-updates on push)

This is best because every `git push` to the `/app/website/` folder will auto-republish the site.

### A1. Push `/app/website/` to GitHub

Your app's code is already on GitHub. You have two options:

**Option 1 — Same monorepo (easiest):**
1. Click **"Save to GitHub"** in Emergent chat now → this pushes all current changes (including `/app/website/`) to your existing `thai2drive` repo.
2. Note: Cloudflare Pages lets you pick a subfolder as the "build output" → we'll point it at `website/` in step A3.

**Option 2 — Separate `thai2drive-web` repo:**
Only do this if you want totally isolated deploy history. Skip unless you have a reason.

### A2. Connect Cloudflare Pages to your GitHub repo

1. Go to https://dash.cloudflare.com → top-left **Workers & Pages** → **Create** → **Pages** tab → **Connect to Git**
2. Click **Connect GitHub** → authorize Cloudflare's GitHub app
3. Pick your `thai2drive` repo
4. Click **Begin setup**

### A3. Configure the build

On the setup screen:

| Field | Value |
|---|---|
| Project name | `thai2drive-web` (or anything you like — this becomes `thai2drive-web.pages.dev` temporarily) |
| Production branch | `main` |
| Framework preset | **None** (static HTML) |
| Build command | **leave empty** |
| Build output directory | `website` |
| Root directory (advanced) | **leave empty** |

Click **Save and Deploy**.

Cloudflare will:
1. Clone your repo
2. Skip the build step (nothing to compile)
3. Upload the contents of `/website/` to its CDN

**First deploy takes ~60 seconds.** When done you'll see a green checkmark and a preview URL like `https://thai2drive-web.pages.dev`.

### A4. Test the preview URL

Open in browser:
- `https://thai2drive-web.pages.dev/` → should show your landing page
- `https://thai2drive-web.pages.dev/privacy` → Privacy page
- `https://thai2drive-web.pages.dev/terms` → Terms page
- `https://thai2drive-web.pages.dev/support` → Support page

If `/privacy` etc. show a 404, your `_redirects` file wasn't picked up — see **Troubleshooting** below.

### A5. Attach your custom domain `thai2drive.no`

1. In the Cloudflare Pages project → **Custom domains** tab → **Set up a custom domain**
2. Enter `thai2drive.no` → **Continue**
3. Cloudflare will check if `thai2drive.no` is already on Cloudflare's DNS:
   - ✅ If **yes** (you already moved the domain's nameservers to Cloudflare before): Cloudflare auto-adds the CNAME record. Done.
   - ❌ If **no**: Cloudflare shows you 2 nameservers like `xyz.ns.cloudflare.com`. Copy them.

### A6. (Only if A5 showed option ❌) Point your registrar's nameservers to Cloudflare

At your domain registrar (Domeneshop / One.com / wherever you bought `thai2drive.no`):
1. Log in
2. Find "Nameservers" / "Navneservere" for `thai2drive.no`
3. **Replace** the existing nameservers with the 2 Cloudflare ones
4. Save

**Propagation takes 1–24 hours**, usually ~30 minutes. You'll get an email from Cloudflare when done. After that, `https://thai2drive.no` and `https://www.thai2drive.no` both point to your Pages site.

### A7. Also add `www.thai2drive.no`

Back in Cloudflare Pages project → **Custom domains** → **Set up a custom domain** → enter `www.thai2drive.no` → **Continue**. Cloudflare adds the CNAME automatically.

---

## Path B — Direct drag-and-drop upload (no GitHub, one-shot)

Use this if you want a quick test deploy without touching GitHub.

1. On your PC, zip the entire `/app/website/` folder (or after `git pull`, find it locally at `thai2drive/website/`)
2. Cloudflare → **Workers & Pages** → **Create** → **Pages** → **Upload assets**
3. Project name: `thai2drive-web`
4. Drag & drop the `website/` folder
5. Click **Deploy**

Downside: no auto-deploy. Every update means another manual drag-and-drop.

If you use Path B, go straight to step A5 (custom domain).

---

## Testing checklist after deploy

Once the domain points to Cloudflare Pages, verify with your phone browser:

```
✓ https://thai2drive.no             → landing page loads
✓ https://thai2drive.no/privacy     → Privacy page, no 404
✓ https://thai2drive.no/terms       → Terms page, no 404
✓ https://thai2drive.no/support     → Support page, "support@thai2drive.no" button visible
✓ Click NO / TH / EN switcher on any page → text changes immediately
✓ Click ← Back on a legal page → returns to landing
```

Also test from Google Play Console:
- Open Play Console → your app → Store listing → Privacy policy URL field → paste `https://thai2drive.no/privacy` → **Save** → Google validates it loads a 200 response. If it says "URL not reachable", the DNS hasn't propagated yet — wait 30 min.

---

## Troubleshooting

### 🚫 `/privacy` returns 404 but `/privacy.html` works
The `_redirects` file wasn't included in the deploy. Check:
1. `/app/website/_redirects` exists (no `.txt` extension)
2. It's in the SAME folder as `index.html`, not in a subfolder
3. Re-deploy

Content of `_redirects` (for reference):
```
/privacy   /privacy.html  200
/terms     /terms.html    200
/support   /support.html  200
/privacy/  /privacy.html  200
/terms/    /terms.html    200
/support/  /support.html  200
```

### 🚫 Custom domain shows "SSL handshake failed"
Cloudflare's SSL cert usually takes 5–15 minutes to activate after the DNS change. Wait it out.

### 🚫 Cloudflare says "this domain is already connected to another account"
Your domain was previously on another Cloudflare account (maybe from an earlier experiment). Go to that account → remove the site → try A5 again. Or contact Cloudflare support to release the domain.

### 🚫 Deploy succeeds but `/styles.css` returns 404
Confirm the **Build output directory** in Pages settings is `website` (singular, no leading slash). If it's empty, Pages serves from the repo root and won't find the files.

### 🚫 Tom Norwegian characters (æ ø å) show as `???` on the live site
The HTML files already have `<meta charset="utf-8"/>` — this shouldn't happen. If it does, hard-refresh (Ctrl+Shift+R) to bust the CDN cache.

---

## What the final DNS config looks like

When everything's set up, your DNS in Cloudflare dashboard should show:

| Type | Name | Content | Proxied |
|---|---|---|---|
| CNAME | `thai2drive.no` (or `@`) | `thai2drive-web.pages.dev` | ✅ (orange cloud) |
| CNAME | `www` | `thai2drive-web.pages.dev` | ✅ |

Cloudflare auto-creates these when you attach the custom domain in step A5. You don't need to add them manually.

---

## When done

Send back in chat:
```
✓ deployed to thai2drive.no
✓ /privacy, /terms, /support all load
✓ ready to continue Play Console setup
```

Then we'll move to Google Play Console steps (Section 1 of `PRODUCTION-SETUP.md`).

---

## Optional: Updating the site later

After first deploy:
- **Path A (Git):** Edit files in `/app/website/`, `git commit && git push` → Cloudflare auto-redeploys in 60 seconds
- **Path B (drag-drop):** Open Cloudflare Pages → your project → **Create deployment** → upload new folder
