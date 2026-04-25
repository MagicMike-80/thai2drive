# Thai2Drive — Production Setup Checklist

**Goal:** Move from sandbox/preview build → real `.aab` on Google Play with working RevenueCat payments.

**Estimated time:** 4–6 hours of clicking + a 24–48 hour wait on Google Cloud service account propagation.

**What you do:** Steps 1–5 below.
**What main agent does (later):** Once you send the real `goog_...` key, the production EAS profile and `.aab` build will be wired up.

> 💡 The placeholder test key currently in your `frontend/.env` is fine to leave — production builds will read a different key from `eas.json`, not `.env`.

---

## STEP 1 — Google Play Console: app + listing

### 1.1 Pay developer fee (one-time, $25)
1. Go to https://play.google.com/console
2. Sign in with the Gmail you want as the **owner** account (this can NEVER be changed). Use a Gmail you control long-term — your business one ideally.
3. Pay the **$25 USD one-time** registration fee.
4. Fill identity verification (passport / ID).

### 1.2 Create the app
1. In Play Console → top-right **Create app**
2. Fill:
   - **App name:** `Thai2Drive`
   - **Default language:** `Norwegian (no-NO)`
   - **App type:** `App`
   - **Free or paid:** `Free` (we monetize via in-app purchases)
   - Tick the two declarations (developer policies + US export laws)
3. Click **Create app**

### 1.3 Complete the "Set up your app" tasks (mandatory before products work)
On the left sidebar → **Dashboard**, complete each of these green-checked tasks:

| Task | What to fill |
|---|---|
| App access | "All functionality is available without restrictions" (you have a free trial) |
| Ads | "No, my app does not contain ads" |
| Content rating | Run the questionnaire — driving theory app rates **PEGI 3 / Everyone** |
| Target audience | 13+ |
| News app | No |
| COVID-19 contact tracing | No |
| Data safety | Declare: collect email + auth token, NOT shared with 3rd parties (it's all on your backend) |
| Government app | No |
| Financial features | "App enables purchases of digital goods" (subscriptions + lifetime) |
| Health | No |
| Store listing | App description + 2 screenshots minimum + 512×512 icon + 1024×500 feature graphic |
| App category | `Education` |
| Tags | `educational`, `quiz`, `driving` |
| Privacy policy | **Required** — must be a public URL. Use your existing `thai2drive.no/privacy` static page |

> ⚠️ **You cannot create in-app products until "Set up your app" shows 100% complete.** This is the most common stuck point.

### 1.4 Pick the package name (CANNOT be changed later)
On **first APK upload** (later), Google locks the package name forever. Decide now:
- Use **`no.thai2drive.app`** ← what you asked for in chat

This must match `app.json android.package` and `app.json ios.bundleIdentifier`.

---

## STEP 2 — Google Play Console: create the 3 products

> 🚨 You can only do this after a **first signed AAB upload** to Internal Testing. Even an empty placeholder build works. Upload one before this step:
> 1. Run locally: `eas build --platform android --profile preview` (then promote to internal testing in Play Console → Testing → Internal testing → Create new release → upload the AAB)
> 2. Wait 5–10 min for Play to process it
> 3. Now product creation menus unlock

### 2.1 Subscription #1 — Monthly
**Play Console → Monetize → Products → Subscriptions → Create subscription**
- **Product ID:** `monthly_199` *(must match exactly — your code uses this)*
- **Name:** `Thai2Drive Premium – Månedlig`
- **Description:** `Ubegrenset tilgang til alle spørsmål, eksamen og forklaringer.`
- **Benefits (optional):** add bullets like "Ubegrenset spørsmål", "Eksamensmodus", "TTS på 3 språk"
- Click **Save**

Now add a **Base plan**:
- Click **Add base plan**
- **Base plan ID:** `monthly`
- **Type:** `Auto-renewing`
- **Billing period:** `1 month`
- **Renewal type:** Auto-renewing
- **Grace period:** 7 days (recommended)
- **Account hold:** 30 days
- **Pricing:** Click **Set prices** → Norway → **199.00 NOK** → Save → "Apply price to other countries" (auto-converts to other currencies if you expand later)
- **Activate**

### 2.2 Subscription #2 — 3 months
**Same flow as 2.1**, with:
- **Product ID:** `threemonth_399`
- **Name:** `Thai2Drive Premium – 3 måneder`
- Base plan ID: `quarterly`
- Billing period: **3 months**
- Price: **399.00 NOK**

### 2.3 One-time product — Lifetime
**Play Console → Monetize → Products → In-app products → Create product**
- **Product ID:** `lifetime_699`
- **Name:** `Thai2Drive Premium – Livstid`
- **Description:** `Engangskjøp – ubegrenset tilgang for alltid.`
- Click **Save**
- Click into the product → **Add purchase option**
  - **Purchase option ID:** `lifetime`
  - **Type:** `Buy` (NOT Rent)
  - **Price:** **699.00 NOK** (Norway) → Save
- **Activate**

### 2.4 Add yourself as a licensed test user (skip charges during testing)
**Play Console → Settings → License testing**
- Add your test Gmail address(es)
- License response: **`LICENSED`**
- Save

When you later test purchases on a phone signed into this Gmail, Google Play shows "Test card. Always approves" and **no real money is charged**. Without this, your test purchases will charge your real card.

---

## STEP 3 — RevenueCat account + project

### 3.1 Sign up
1. Go to https://app.revenuecat.com/signup
2. Use the same Gmail as Play Console (easier later)
3. Verify email

### 3.2 Create project
- **Name:** `Thai2Drive`
- **Currency:** `NOK`
- Click **Create**

### 3.3 Add the Android app inside the project
**RC Dashboard → Project Settings → Apps → + New**
- **Name:** `Thai2Drive Android`
- **Platform:** `Google Play`
- **App package name:** `no.thai2drive.app`
- Click **Save**

### 3.4 Define the entitlement
**Product Catalog → Entitlements → + New entitlement**
- **Identifier:** `pro` *(must be lowercase exactly — your code checks `entitlements.active.pro`)*
- **Display name:** `Premium`
- Save

We'll attach products to this entitlement in Step 4.6.

---

## STEP 4 — Connect Google Play to RevenueCat (the trickiest 30 minutes)

This part requires a **Google Cloud service account** so RevenueCat can read your Play Console product catalog and validate purchases.

### 4.1 Create the Google Cloud service account
1. Go to https://console.cloud.google.com
2. Top-left → create / select a project (use the same Gmail)
3. Sidebar → **IAM & Admin → Service Accounts → + Create Service Account**
   - Name: `revenuecat-play-billing`
   - ID: auto-fills
   - Click **Create and Continue**
4. Skip role assignment for now → **Done**
5. Click the new service account → **Keys → Add key → Create new key → JSON**
6. ⬇️ Download the JSON file. **Treat it like a password — don't commit it to git.**

### 4.2 Enable required Google APIs
In Google Cloud Console for the SAME project:
1. Sidebar → **APIs & Services → Library**
2. Enable: **Google Play Android Developer API** (search → Enable)
3. Enable: **Google Play Developer Reporting API**
4. Enable: **Pub/Sub API**

### 4.3 Grant the service account access to Play Console
1. Back in **Google Play Console → Setup → API access** (left sidebar)
2. Click **Link Google Cloud project** → pick the Cloud project from 4.1 → Confirm
3. Below, you'll see your service account listed → click **Grant access**
4. Permissions → check:
   - ✅ View app information and download bulk reports (read-only)
   - ✅ View financial data, orders, and cancellation survey responses
   - ✅ Manage orders and subscriptions
5. **Apply** → **Send invite**

> ⏰ **Wait 24–48 hours** for Google's permissions to propagate. Yes, really. RevenueCat docs confirm this. You can continue setting up steps 4.4–4.6 in parallel — but actual purchase events won't flow until the wait is over.

### 4.4 Upload the JSON to RevenueCat
1. RC Dashboard → **Project Settings → Apps → Thai2Drive Android**
2. Scroll to **Service account credentials JSON** → upload the JSON file from 4.1
3. Save

RC will now try to validate the connection. If it fails, it's almost always the 24–48h wait.

### 4.5 Import products from Google Play
1. RC Dashboard → **Product catalog → Products → + New** → **Import from Google Play**
2. RC pulls in your 3 products: `monthly_199:monthly`, `threemonth_399:quarterly`, `lifetime_699:lifetime`
3. Confirm import

> If "no products found", it's the 24–48h wait. Come back later.

### 4.6 Attach products to the `pro` entitlement
**Entitlements → pro → Attach products** → tick all 3 → Save.

### 4.7 Create the Offering
**Offerings → + New offering**
- **Identifier:** `default` (your code reads `offerings.current` which RC routes to whichever offering you mark current)
- Add 3 packages, mapping each to one product:
  - Package: `$rc_monthly` → product `monthly_199:monthly`
  - Package: `$rc_three_month` → product `threemonth_399:quarterly`
  - Package: `$rc_lifetime` → product `lifetime_699:lifetime`
- Mark this offering as **Current**

### 4.8 Set up Platform Server Notifications (auto-renewals work without this, but it's faster)
**Play Console → Monetize setup → Real-time developer notifications**
- Topic name: RC will give you one in dashboard → paste it
- Save

---

## STEP 5 — Get the `goog_...` API key

1. RC Dashboard → **Project Settings → API keys**
2. You'll see two columns: **Public app-specific keys** and **Secret API keys**
3. Under **Public app-specific keys**, find the row for **Thai2Drive Android**
4. The key starts with **`goog_`** followed by ~30 chars
5. Copy it — paste it into the chat with main agent

> 🔒 **Public ≠ unsafe.** This key can ship in your app binary. The "secret" key is for server-side calls only — you don't need that for MVP.

That key is what main agent will plug into:
- `eas.json` → `production.env.EXPO_PUBLIC_RC_API_KEY = goog_xxx...`
- Then `eas build --platform android --profile production` produces a signed `.aab`
- Upload `.aab` to Play Console → Production track → Review (1–3 days)
- App goes live

---

## What to send me when done

Just paste this in chat:
```
goog key: goog_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
package id confirmed: no.thai2drive.app
licensed test gmail: yourtest@gmail.com
ready for production .aab build
```

I'll then:
1. Update `eas.json` with the production profile that injects the real key
2. Update `app.json` package id if you switched to `no.thai2drive.app`
3. Bump `versionCode` to 2
4. Document the build + submit command
5. Confirm the `paymentsEnabled` guard flips to **true** once the real key + offering land

---

## Common gotchas (read before you start)

1. **"Products not appearing in RC"** → 99% of the time it's the 24–48h Cloud propagation. Wait.
2. **"Set up your app" tasks aren't all green** → product creation menus stay locked. Finish all 14 tasks first.
3. **Privacy policy URL** → required and Play Store reviewers WILL click it. Make sure `thai2drive.no/privacy` is live before submitting.
4. **First AAB upload must succeed before products can be activated** → upload a placeholder preview AAB to Internal Testing track first.
5. **Test purchases without losing money** → MUST add your Gmail to Play Console → Setup → License testing → LICENSED. Without this, every test buy is a real charge.
6. **`pro` is case-sensitive** → use exactly `pro`, not `Pro` or `PRO`.
7. **Don't change the package id after first upload** — Google locks it permanently.
8. **`goog_...` key vs `sk_...` key** → use the public `goog_...` key in the app. Never ship `sk_...`.

---

Total realistic timeline:
- Day 1: Steps 1–3 (~2 hours of clicks + content rating quiz)
- Day 1: Step 4.1–4.4 (~30 min) — kicks off Google's 24–48h wait
- Day 3: Step 4.5–4.8, Step 5 (~30 min)
- Day 3: send `goog_` key → main agent wires production EAS profile (~10 min)
- Day 3: first production `.aab` build (~15 min EAS build)
- Day 3: upload to Play Console Production track → Google review (1–3 days, usually 24h for established apps)

---

When stuck, paste the exact RC dashboard error or Play Console screenshot in chat and I'll triage.
