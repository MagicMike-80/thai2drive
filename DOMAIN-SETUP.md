# 🌐 Custom Domain Setup — Thai2Drive

This guide walks you through pointing a custom Norwegian domain (e.g. **thai2drive.no**, **thai2driveapp.no**, or **thaiteori.no**) at your Emergent-hosted app.

The code is **already domain-agnostic** — no hardcoded URLs. You just need to:
1. Buy the domain
2. Add the DNS records below
3. Flip one env var: `PUBLIC_SITE_URL`
4. (Optional) Add the domain in the Emergent deploy dashboard

---

## 🛒 1. Buy the domain

Recommended Norwegian registrars:

| Registrar | Notes |
|---|---|
| **Domeneshop.no** | Cheapest, in Norwegian, pays in NOK. ~99 kr/year for `.no` |
| **domene.shop** | Same as above (rebrand) |
| **UniteDomains / one.com** | Easier UI for beginners |
| **Cloudflare Registrar** | At-cost pricing, strongest DNS + free SSL, but requires passing Norid's residency check |

> ⚠️ **`.no` requirement:** Norid (the `.no` registry) requires a Norwegian organisation number OR a Norwegian-resident person to register a `.no` domain. If you don't qualify, use a `.com` / `.app` / `.site` alternative — the code works the same with any TLD.

**Best picks for this app:**
- `thai2drive.no` ← most brandable (preferred)
- `thaiteori.no` ← highest intent (Norwegians search "teori")
- `thai2driveapp.no` ← SEO-neutral backup

---

## 🧭 2. DNS records to add

After you buy the domain, go to your registrar's DNS control panel and add these records.

> The exact target values (**A record IP** and **CNAME target**) will be shown in your Emergent deploy dashboard once you add the custom domain there. The records below are the **shape** — replace `<...>` with what Emergent gives you.

### Option A — Apex (root) domain like `thai2drive.no`

| Type | Name | Value | TTL |
|---|---|---|---|
| **A** | `@` | `<IP-from-Emergent-dashboard>` | 3600 |
| **CNAME** | `www` | `thai2drive.no.` (or the Emergent subdomain) | 3600 |
| **TXT** | `@` | `<verification-token-from-Emergent>` | 3600 |
| **CAA** *(optional)* | `@` | `0 issue "letsencrypt.org"` | 3600 |

### Option B — Apex via ALIAS/ANAME (recommended if registrar supports it)

Some registrars (Cloudflare, Domeneshop) support ALIAS/ANAME/CNAME-flattening at the apex. Use this instead of a raw A record so the IP can change without you re-configuring DNS:

| Type | Name | Value | TTL |
|---|---|---|---|
| **ALIAS** (or **ANAME**) | `@` | `<your-app>.emergentagent.com.` | 3600 |
| **CNAME** | `www` | `<your-app>.emergentagent.com.` | 3600 |

### Option C — Subdomain only (simplest, e.g. `app.thai2drive.no`)

| Type | Name | Value | TTL |
|---|---|---|---|
| **CNAME** | `app` | `<your-app>.emergentagent.com.` | 3600 |

---

## ⚙️ 3. Flip the one env var

In `/app/backend/.env` add:

```
PUBLIC_SITE_URL=https://thai2drive.no
# Optional — drop the /api prefix from canonical URLs once custom domain
# routes / → backend. Keep unset on the Emergent preview.
# SITE_ROUTING_MODE=clean
```

Then restart the backend:

```bash
sudo supervisorctl restart backend
```

**What updates automatically:**
- `<link rel="canonical">` on every page
- `og:url` + Twitter card URLs (social previews)
- `/api/sitemap.xml` entries
- `/api/robots.txt` Sitemap line
- Support page "Nettsted" footer link

**Nothing else needs changing** — all internal page links are already relative, so they follow whatever host the user visited from.

---

## 🚀 4. Activate it on Emergent

In the Emergent deploy dashboard:

1. Go to your project → **Settings → Custom Domains**
2. Click **Add Domain** → enter `thai2drive.no`
3. Copy the **A record IP / CNAME target / verification TXT** shown
4. Paste those into your registrar's DNS panel (step 2 above)
5. Click **Verify** in Emergent — usually takes **5 min – 24 h** for DNS to propagate
6. Emergent auto-provisions a **Let's Encrypt SSL certificate** once verification succeeds

> ✅ Once verified, `https://thai2drive.no` will serve your app. The preview URL `https://norge-quiz-app.preview.emergentagent.com` will keep working side-by-side unless you explicitly disable it.

---

## ✅ 5. Verify it worked

```bash
# From any machine
curl -I https://thai2drive.no           # expect HTTP/2 200
curl -s https://thai2drive.no/api/robots.txt
curl -s https://thai2drive.no/api/sitemap.xml | head
```

And check meta tags render correctly:
```bash
curl -s https://thai2drive.no/api/website | grep -E 'canonical|og:url'
# Should print:
# <link rel="canonical" href="https://thai2drive.no/"/>
# <meta property="og:url" content="https://thai2drive.no/"/>
```

---

## 🔁 Buying multiple domains (all → same site)

If you buy `thai2drive.no`, `thai2driveapp.no`, and `thaiteori.no`, pick **one** as primary (e.g. `thai2drive.no`) and set up 301 redirects on the other two so Google doesn't split SEO juice:

**Option 1 — Registrar-level redirect** (simplest)
Most registrars (Domeneshop, Cloudflare, one.com) have a "URL forwarding" feature. Set:
- `thai2driveapp.no` → `301 → https://thai2drive.no`
- `thaiteori.no` → `301 → https://thai2drive.no`

**Option 2 — Cloudflare Page Rules** (free)
1. Put all 3 domains behind Cloudflare
2. For each non-primary, create a Page Rule: `*.thaiteori.no/*` → `301 → https://thai2drive.no/$1`

---

## 🧪 Current state

Without `PUBLIC_SITE_URL` set, the site keeps using the preview URL and everything continues to work. Verified:

```
$ curl -s http://localhost:8001/api/sitemap.xml | grep loc
<loc>https://norge-quiz-app.preview.emergentagent.com/</loc>
<loc>https://norge-quiz-app.preview.emergentagent.com/privacy</loc>
<loc>https://norge-quiz-app.preview.emergentagent.com/terms</loc>
<loc>https://norge-quiz-app.preview.emergentagent.com/support</loc>
```

---

## 📧 For the mobile app (future)

The mobile app already uses its own `EXPO_PUBLIC_BACKEND_URL` env var for API calls, independent of the website domain. When you're ready to point the app at the custom API:

```
EXPO_PUBLIC_BACKEND_URL=https://thai2drive.no
```

(then rebuild with `eas build`). But you don't need to do this — the app can keep using the Emergent preview URL for API calls while the website runs on `thai2drive.no`.
