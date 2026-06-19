"""
retention_worker.py — sender e-postpåminnelse til brukere inaktive i 3+ dager.

Kjør manuelt:   cd thai2drive/backend && python scripts/retention_worker.py
Kjør som cron:  0 9 * * * cd /app && python scripts/retention_worker.py

Krav i .env:
  MONGO_URL
  SUPPORT_SMTP_HOST
  SUPPORT_SMTP_PORT
  SUPPORT_SMTP_USER
  SUPPORT_SMTP_PASS
"""

import asyncio
import os
import smtplib
import ssl
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from motor.motor_asyncio import AsyncIOMotorClient

# ── env loader ───────────────────────────────────────────────────────────────
def _load_env():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_env()

MONGO_URL     = os.environ["MONGO_URL"]
SMTP_HOST     = os.environ["SUPPORT_SMTP_HOST"]
SMTP_PORT     = int(os.environ["SUPPORT_SMTP_PORT"])
SMTP_USER     = os.environ["SUPPORT_SMTP_USER"]
SMTP_PASS     = os.environ["SUPPORT_SMTP_PASS"]
FROM_NAME     = "Michael Trafikklærer"
FROM_ADDR     = SMTP_USER
INACTIVITY_DAYS = 3
DB_NAME       = "thai2drive"

# ── email templates ──────────────────────────────────────────────────────────

SUBJECT = "Hei! Michael savner deg 🚗 | ไมเคิลคิดถึงคุณ"

HTML_BODY = """\
<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Thai2Drive påminnelse</title>
  <style>
    body {{ margin: 0; padding: 0; background: #0F172A; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    .wrap {{ max-width: 560px; margin: 32px auto; background: #1E293B; border-radius: 20px; overflow: hidden; }}
    .hero {{ background: linear-gradient(135deg, #1D4ED8 0%, #0F766E 100%); padding: 36px 32px 28px; text-align: center; }}
    .hero-icon {{ font-size: 48px; }}
    .hero h1 {{ color: #fff; font-size: 24px; font-weight: 800; margin: 12px 0 4px; }}
    .hero p {{ color: rgba(255,255,255,0.75); font-size: 14px; margin: 0; }}
    .body {{ padding: 28px 32px; }}
    .greeting {{ font-size: 17px; font-weight: 700; color: #F1F5F9; margin-bottom: 10px; }}
    .text {{ font-size: 15px; color: #94A3B8; line-height: 1.7; margin-bottom: 16px; }}
    .divider {{ border: none; border-top: 1px solid #334155; margin: 20px 0; }}
    .th {{ color: #CBD5E1; font-size: 14px; line-height: 1.75; margin-bottom: 20px; }}
    .cta {{ display: block; width: fit-content; margin: 0 auto 24px; background: #2563EB; color: #fff !important; text-decoration: none; font-size: 16px; font-weight: 700; padding: 14px 36px; border-radius: 12px; }}
    .tip {{ background: rgba(16,185,129,0.10); border: 1px solid rgba(16,185,129,0.25); border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; }}
    .tip-label {{ color: #10B981; font-size: 12px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 6px; }}
    .tip-text {{ color: #94A3B8; font-size: 14px; line-height: 1.6; }}
    .footer {{ padding: 16px 32px 24px; text-align: center; color: #475569; font-size: 12px; }}
    .footer a {{ color: #475569; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <div class="hero-icon">🚗</div>
      <h1>Thai2Drive</h1>
      <p>Norsk førerprøve for Thai-talende</p>
    </div>
    <div class="body">

      <p class="greeting">Hei {name}! 👋</p>
      <p class="text">
        Det er {days} dager siden du sist øvde på teoriprøven.<br>
        Michael savner deg — og lappen venter!
      </p>
      <p class="text">
        Bare 10 minutter om dagen holder deg i gang. Kom tilbake og ta
        der du slapp.
      </p>

      <hr class="divider">

      <p class="th">
        สวัสดี {name}! ผ่านมา {days} วันแล้วนับจากครั้งสุดท้ายที่คุณฝึกทำข้อสอบ<br>
        ไมเคิลคิดถึงคุณ — ใบขับขี่รออยู่นะ! ✨<br><br>
        แค่ 10 นาทีต่อวันก็พอ มาต่อจากที่ค้างไว้เลย
      </p>

      <a href="https://thai2drive.com" class="cta">กลับไปฝึก · Fortsett øvingen</a>

      <div class="tip">
        <div class="tip-label">💡 Tips fra Michael · เคล็ดลับจากไมเคิล</div>
        <div class="tip-text">
          Husker du høyreregelen? Ingen skilt i krysset = gi vikeplikt for trafikk fra høyre.<br>
          <span style="color:#94A3B8;font-size:13px;">
            จำกฎขวาได้ไหม? ถ้าไม่มีป้ายในสี่แยก ต้องให้ทางรถที่มาจากด้านขวา
          </span>
        </div>
      </div>

    </div>
    <div class="footer">
      Du får denne e-posten fordi du er registrert på Thai2Drive.<br>
      คุณได้รับอีเมลนี้เพราะลงทะเบียนไว้กับ Thai2Drive<br><br>
      <a href="https://thai2drive.com/settings">Avslutt e-postvarsler · ยกเลิกการแจ้งเตือนทางอีเมล</a>
    </div>
  </div>
</body>
</html>
"""

TEXT_BODY = """\
Hei {name}!

Det er {days} dager siden du sist øvde på teoriprøven.
Michael savner deg — kom tilbake og øv litt i dag!

สวัสดี {name}! ผ่านมา {days} วันแล้วนับจากครั้งสุดท้ายที่คุณฝึก
ไมเคิลคิดถึงคุณ มาฝึกต่อกันเลย!

https://thai2drive.com

--
Thai2Drive · Norsk førerprøve for Thai-talende
"""

# ── find inactive users ──────────────────────────────────────────────────────

async def find_inactive_users(db) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=INACTIVITY_DAYS)
    cutoff_iso = cutoff.isoformat()

    pipeline = [
        # Only registered users with email
        {"$match": {"email": {"$exists": True, "$ne": None, "$ne": ""}}},
        # Left-join latest UserProgress by device_id
        {"$lookup": {
            "from": "UserProgress",
            "localField": "device_id",
            "foreignField": "device_id",
            "as": "progress",
        }},
        {"$addFields": {
            "last_activity": {
                "$ifNull": [
                    {"$arrayElemAt": ["$progress.last_activity", 0]},
                    "$created_at",
                ]
            }
        }},
        # Keep only those inactive for >= INACTIVITY_DAYS
        {"$match": {"last_activity": {"$lte": cutoff_iso}}},
        {"$project": {"_id": 0, "id": 1, "email": 1, "name": 1, "last_activity": 1}},
    ]

    return await db["users"].aggregate(pipeline).to_list(length=None)


# ── SMTP send ─────────────────────────────────────────────────────────────────

def send_email(to_email: str, to_name: str, days: int) -> bool:
    name = to_name or "der"
    html = HTML_BODY.format(name=name, days=days)
    text = TEXT_BODY.format(name=name, days=days)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = SUBJECT
    msg["From"] = f"{FROM_NAME} <{FROM_ADDR}>"
    msg["To"] = to_email

    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_ADDR, to_email, msg.as_string())
        return True
    except Exception as exc:
        print(f"  SMTP error for {to_email}: {exc}")
        return False


# ── main ──────────────────────────────────────────────────────────────────────

async def main():
    print(f"[retention_worker] Starting — cutoff = {INACTIVITY_DAYS} days inactive")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    users = await find_inactive_users(db)
    print(f"[retention_worker] Found {len(users)} inactive user(s)")

    sent = failed = skipped = 0
    now = datetime.now(timezone.utc)

    for u in users:
        email = u.get("email", "")
        name  = u.get("name", "")
        last  = u.get("last_activity", "")
        if not email:
            skipped += 1
            continue

        # Calculate precise inactivity
        try:
            last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
            days_inactive = (now - last_dt).days
        except Exception:
            days_inactive = INACTIVITY_DAYS

        print(f"  → {email} ({days_inactive}d inactive)")
        ok = send_email(email, name, days_inactive)
        if ok:
            sent += 1
            print(f"    ✓ sent")
        else:
            failed += 1

    client.close()
    print(f"\n[retention_worker] Done — {sent} sent, {failed} failed, {skipped} skipped (no email)")


if __name__ == "__main__":
    asyncio.run(main())
