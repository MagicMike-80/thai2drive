# 🌐 Custom Domain Setup — Thai2Drive (no redirect)

**Goal:** `https://thai2drive.no` and `https://www.thai2drive.no` both load the landing page **directly**, without redirect, with valid SSL.

---

## ✅ What the code already does

| Concern | Status |
|---|---|
| Backend accepts any Host header | ✅ No `TrustedHostMiddleware`, no host filter |
| No server redirect between www ↔ apex | ✅ No `RedirectResponse` for host |
| CORS open | ✅ `allow_origins=["*"]` |
| Landing page route | ✅ `/api/website` (FastAPI) |
| Diagnostic endpoint | ✅ `/api/_whoami` echoes back the Host it received |
| Env-configurable canonical URL | ✅ `PUBLIC_SITE_URL` in `/app/backend/.env` |

**No code changes are needed.** The remaining work is at the Emergent platform + DNS level.

---

## 📋 Step-by-step (one time)

### 1. Link both domains in the Emergent dashboard

Do this **twice** — once for each hostname. Do **not** use registrar URL forwarding (that's what made "www" unstable before).

1. Open your deployed app in the Emergent dashboard
2. Click **"Link domain"**
3. Enter `thai2drive.no`
4. Click **"Entri"** and follow the on-screen prompts
5. Wait for verification (5–15 min typically, up to 24 h for global DNS)
6. When step 1 is green ✅, repeat steps 2-5 for `www.thai2drive.no`

> Each domain is verified **independently**. Both will get their own SSL certificate via Let's Encrypt.

### 2. DNS records (what Entri will ask you to add at Domeneshop)

Entri usually auto-configures if your registrar is supported. If you have to add them manually, these are the shape — **Entri will give you the exact values**:

#### For `thai2drive.no` (apex)

| Type | Name | Value (from Entri) | TTL |
|---|---|---|---|
| **A** | `@` | `<IP shown in Entri>` | 3600 |
| **TXT** | `@` | `<verification token shown in Entri>` | 3600 |

> Domeneshop supports ALIAS at the apex. If Entri offers it, prefer ALIAS over A — the target IP can then change without you re-configuring DNS.

#### For `www.thai2drive.no`

| Type | Name | Value (from Entri) | TTL |
|---|---|---|---|
| **CNAME** | `www` | `<target shown in Entri>` | 3600 |
| **TXT** | `_verify.www` (if asked) | `<token>` | 3600 |

> ⚠️ **Critical per Emergent docs:** remove *any other existing A records* for `@` and `www` before linking — leftover A records (from a parked page, etc.) will break verification.

### 3. SSL — automatic

Once each domain is verified green ✅ in the dashboard, Emergent provisions a Let's Encrypt cert for that exact hostname. Both hostnames end up with their own valid cert — no cert-mismatch warnings for users.

### 4. **No URL forwarding / no 301 redirect** between the two

- ❌ Don't set "URL forwarding" on Domeneshop for `www.thai2drive.no` → `thai2drive.no`
- ❌ Don't add nginx rewrites or application-level redirects
- ✅ Both hostnames are first-class domains on the app — each serves content directly

---

## 🧪 Verify it worked

```bash
# Both must return HTTP/2 200 and show the Host header they saw
curl -s https://thai2drive.no/api/_whoami | jq
curl -s https://www.thai2drive.no/api/_whoami | jq

# Expected in each response:
# {
#   "ok": true,
#   "host": "thai2drive.no",              ← or www.thai2drive.no
#   "x-forwarded-host": "thai2drive.no",  ← or www.thai2drive.no
#   "scheme": "https"
# }

# SSL cert check
curl -vI https://thai2drive.no 2>&1      | grep -i "subject:"
curl -vI https://www.thai2drive.no 2>&1  | grep -i "subject:"
# Each should show the respective Common Name on the certificate.

# Landing page loads without redirect
curl -sI https://thai2drive.no/api/website | head -1
curl -sI https://www.thai2drive.no/api/website | head -1
# Both should be "HTTP/2 200" — not "HTTP/2 301" or "302"
```

---

## 🎨 Where the landing page lives on the custom domain

**Without any additional work**, after the domain is linked you'll have these URLs live:

| URL | What loads |
|---|---|
| `https://thai2drive.no/api/website` | The full marketing landing page |
| `https://thai2drive.no/api/privacy` | Privacy policy |
| `https://thai2drive.no/api/terms` | Terms |
| `https://thai2drive.no/api/support` | Support page |
| `https://thai2drive.no/api/sitemap.xml` | SEO sitemap |
| `https://thai2drive.no/api/robots.txt` | robots.txt |
| `https://thai2drive.no/` | The Expo web app home (currently the mobile-app UI on web) |

### Want a cleaner URL like `https://thai2drive.no/` → landing page directly?

Because Emergent's ingress sends `/api/*` → backend and everything else → the Expo frontend, there are two ways to put the landing page at root:

**Option A — Easiest:** ask Emergent support (support@emergent.sh) to add an ingress path rewrite for your custom domains:
> "For host `thai2drive.no` and `www.thai2drive.no`, rewrite root path `/` → `/api/website`."

This is a one-line nginx ingress annotation on their side. No code changes required.

**Option B — Pure code:** I can rebuild the landing page as an Expo web route (React components) so it naturally lives at the Expo root `/`. Larger change — tell me if you want this and I'll scope it.

For launch, I recommend **Option A**. Simpler and the landing page logic stays in one Python file.

---

## 🔧 After both domains are green

Update the site config to advertise the canonical domain (for SEO / Open Graph):

```env
# /app/backend/.env
PUBLIC_SITE_URL=https://thai2drive.no
```

Then restart:

```bash
sudo supervisorctl restart backend
```

This updates canonical URLs, `og:url`, sitemap entries, and the social share preview link — but **both** `thai2drive.no` and `www.thai2drive.no` continue to serve content. The canonical tag just tells Google which one to prefer in search results (no redirect needed).

---

## 🇳🇴 `.no` gotchas

- Norid requires Norwegian residency or org-number to hold a `.no` domain — you already handled this via Domeneshop.
- DNSSEC is optional but recommended for `.no` — Domeneshop offers a one-click toggle.
- DNS propagation on `.no` is typically fast (< 10 min) because Norid publishes frequently.

---

## 🔁 Multiple marketing domains?

If you also bought `thai2driveapp.no` and/or `thaiteori.no`, the cleanest pattern is:

- Primary brand: `thai2drive.no` → link directly in Emergent (as above)
- Secondaries: set up **server-side 301 redirects** at the registrar or via Cloudflare page rules → `thai2drive.no`

(Secondaries are the only place where a 301 redirect makes sense — primary + www must both serve content directly per your requirement.)
