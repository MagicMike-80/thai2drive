# Thai2Drive — Marketing Website

Static site for `thai2drive.no`. **Completely separate from the Expo mobile app.**

## Files

```
/app/website/
├── index.html          ← Landing page
├── privacy.html        ← Privacy policy (NO / TH / EN)
├── terms.html          ← Terms of service (NO / TH / EN)
├── support.html        ← Support + FAQ + contact
├── styles.css          ← Shared CSS (dark navy + amber, mobile-first)
├── lang.js             ← Language switcher (saves to localStorage)
└── assets/
    ├── t2d-icon.png    ← Brand icon (512×512)
    └── favicon.png     ← Favicon (192×192)
```

**No build step.** Pure static HTML/CSS/JS. Loads in <40 KB.

## Recommended hosting — Cloudflare Pages (free, fast)

### 1. Push to a new GitHub repo (recommended)

```bash
cd /app/website
git init
git add .
git commit -m "Initial Thai2Drive marketing site"
git branch -M main
# Create a NEW, separate repo on GitHub (e.g. 'thai2drive-website')
git remote add origin https://github.com/YOUR-USERNAME/thai2drive-website.git
git push -u origin main
```

> Use a *separate* repo from the main `thai2drive` app repo. Website and app deploy independently.

### 2. Deploy to Cloudflare Pages

1. Go to https://dash.cloudflare.com → **Workers & Pages** → **Create → Pages → Connect to Git**
2. Select your `thai2drive-website` repo
3. **Build command:** leave blank (no build needed)
4. **Build output directory:** `/` (root)
5. Click **Save and Deploy**

You'll get a free subdomain like `thai2drive-website.pages.dev` within 30 seconds.

### 3. Point `thai2drive.no` at Cloudflare Pages

1. On Cloudflare Pages, click your new project → **Custom domains → Set up a custom domain**
2. Enter `thai2drive.no`
3. Cloudflare shows you DNS records to add. On **Domeneshop** → DNS for `thai2drive.no`:

| Type | Name | Value | TTL |
|---|---|---|---|
| **A** | `@` | *(the IP Cloudflare gives you)* | 3600 |
| **AAAA** | `@` | *(the IPv6 Cloudflare gives you)* | 3600 |
| **CNAME** | `www` | `thai2drive-website.pages.dev.` | 3600 |

> Some registrars support ALIAS at apex — if Domeneshop does, use ALIAS instead of A/AAAA.

4. Repeat the "custom domain" step with `www.thai2drive.no`.
5. Cloudflare auto-provisions SSL for both — live in ~5 minutes.

### 4. Verify

```bash
curl -sI https://thai2drive.no/          # → HTTP/2 200
curl -sI https://www.thai2drive.no/      # → HTTP/2 200
curl -sI https://thai2drive.no/privacy.html  # → HTTP/2 200
curl -sI https://thai2drive.no/terms.html    # → HTTP/2 200
curl -sI https://thai2drive.no/support.html  # → HTTP/2 200
```

## Alternatives (any of these works)

- **Netlify** — drag-and-drop the folder to https://app.netlify.com/drop, then add custom domain
- **Vercel** — `vercel --prod` from the folder, then add custom domain
- **GitHub Pages** — enable on the repo's Settings → Pages, set source to `main`/`/`
- **Self-hosted nginx** — just serve the directory

## Updating the Google Play link

When the app is live on Google Play, update one line in `lang.js`:

```js
const playUrl = 'https://play.google.com/store/apps/details?id=com.thai2drive.app';
```

Push to Git → Cloudflare auto-redeploys in ~30 seconds.

## Updating the iOS badge

When iOS is ready, find `iOS coming soon` in `index.html` and replace the `<span>` with an active App Store link:

```html
<a class="btn btn-secondary" href="https://apps.apple.com/app/idXXXXXXXXXX">
  ...App Store icon + label...
</a>
```

## Email

`support@thai2drive.no` is referenced throughout the site. Configure a mail forward on Domeneshop (or Google Workspace / Fastmail / Zoho) to your real inbox.

## Languages

Norwegian (default) / Thai / English. Language toggle in the top right persists via `localStorage`. All legal/support content is fully translated.

---

**This site does NOT touch the mobile app.** The app continues to run on the Emergent preview URL / EAS builds. These are independent deployments.
