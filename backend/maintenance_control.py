"""Owner-controlled maintenance gate shared by the web UI and backend."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

OWNER_EMAIL = "michael.6lee@yahoo.com"
_ID = "customer_access"
_security = HTTPBearer(auto_error=False)

# Exact exceptions are deliberately narrow. Webhook handlers authenticate their
# own signatures and must remain available to keep subscriptions in sync.
_EXEMPT = {
    "/api/health", "/health", "/api/web/version", "/web/version",
    "/api/auth/login", "/api/auth/me", "/api/auth/forgot-password", "/api/auth/reset-password",
    "/api/stripe/webhook", "/api/webhooks/revenuecat", "/api/rc/webhook",
    "/api/create-checkout-session", "/api/checkout/status", "/api/billing/subscription", "/billing/subscription",
    "/api/maintenance/status", "/api/admin/maintenance",
    "/api/admin-panel", "/api/admin", "/admin", "/api/cms",
    "/service-worker.js", "/api/service-worker.js", "/favicon.ico",
}


def _app_shell(path):
    return path.rstrip("/") in {
        "/app", "/app/no", "/app/th", "/app/en",
        "/no/app", "/th/app", "/en/app", "/web", "/web/no",
        "/web/th", "/web/en", "/api/app", "/api/app/no",
        "/api/app/th", "/api/app/en", "/api/web", "/api/web/no",
        "/api/web/th", "/api/web/en", "/api/no/app", "/api/th/app", "/api/en/app",
    }


def _asset_request(method, path):
    # The browser cannot attach the bearer token to ordinary image/audio tags.
    # These existing public asset handlers keep their own access controls; this
    # does not exempt quiz, progress, book or teacher API endpoints.
    if method not in {"GET", "HEAD"}:
        return False
    if path.startswith(("/api/assets/", "/api/public_assets/", "/api/sign-images/", "/assets/", "/public_assets/")):
        return path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".mp3", ".m4a", ".mp4", ".wav", ".ogg", ".webm"))
    return path.startswith((
        "/api/media/files/", "/api/audio/", "/api/gridfs/", "/gridfs/", "/media/",
    ))


def _standalone_learning(path):
    return path.rstrip("/") in {"/no/flipp-flopp", "/th/flipp-flopp", "/en/flipp-flopp", "/bok"}


def standalone_guard_script(language, book=False):
    """Check open standalone pages and attach the existing token to game API calls."""
    language = language if language in {"no", "th", "en"} else "no"
    token_keys = "['authToken','t2d_token','admin_token']" if book else "['t2d_token','admin_token','authToken']"
    return ("<script>(function(){const nativeFetch=window.fetch.bind(window);let ownerToken='';"
            "function tokens(){try{return " + token_keys + ".map(k=>localStorage.getItem(k)).filter(Boolean)}catch(e){return []}}"
            "async function check(){try{const r=await nativeFetch('/api/maintenance/status',{cache:'no-store'});"
            "if(!r.ok)throw Error();const s=await r.json();if(!s.active){ownerToken='';return;}"
            "for(const t of tokens()){const x=await nativeFetch('/api/maintenance/status',{cache:'no-store',headers:{Authorization:'Bearer '+t}});"
            "if(x.ok&&(await x.json()).owner){ownerToken=t;return;}}"
            "}catch(e){} let l='" + language + "';try{const b=localStorage.getItem('bok_lang');"
            + ("if(['no','th','en'].includes(b))l=b;" if book else "") +
            "}catch(e){}location.replace('/app/'+l)} const ready=check();setInterval(check,15000);"
            "window.fetch=async function(input,init){const req=new Request(input,init);const u=new URL(req.url,location.href);"
            "if(u.origin===location.origin&&u.pathname.startsWith('/api/'))"
            "{await ready;const t=ownerToken||(!req.headers.has('Authorization')?tokens()[0]:'');if(t){const h=new Headers(req.headers);h.set('Authorization','Bearer '+t);return nativeFetch(new Request(req,{headers:h}))}}"
            "return nativeFetch(req)};})();</script>")


def create_maintenance(db, verify_token):
    router = APIRouter()

    async def owner(credentials):
        if not credentials or credentials.scheme.lower() != "bearer":
            return False
        payload = verify_token(credentials.credentials)
        if not payload or (payload.get("email") or "").strip().lower() != OWNER_EMAIL:
            return False
        user = await db.users.find_one({"id": payload.get("sub"), "email": OWNER_EMAIL},
                                       {"_id": 0, "disabled": 1, "deleted_at": 1})
        admin = await db.admin_users.find_one({"email": OWNER_EMAIL}, {"_id": 1})
        return bool(user and not user.get("disabled") and not user.get("deleted_at") and admin)

    async def require_owner(credentials: HTTPAuthorizationCredentials = Depends(_security)):
        if not await owner(credentials):
            raise HTTPException(status_code=403, detail="Owner access required")
        return True

    async def status():
        document = await db.system_settings.find_one({"_id": _ID}, {"active": 1})
        return bool(document and document.get("active") is True)

    @router.get("/api/maintenance/status")
    async def get_status(credentials: HTTPAuthorizationCredentials = Depends(_security)):
        try:
            active = await status()
            is_owner = await owner(credentials) if credentials else False
        except Exception:
            raise HTTPException(status_code=503, detail="Maintenance status unavailable")
        return JSONResponse({"active": active, "owner": is_owner}, headers={"Cache-Control": "no-store"})

    class Change(BaseModel):
        active: bool
        confirmed: bool = False

    @router.post("/api/admin/maintenance")
    async def change(body: Change, _: bool = Depends(require_owner)):
        if body.active and not body.confirmed:
            raise HTTPException(status_code=400, detail="Confirmation required")
        event = {"active": body.active, "at": datetime.now(timezone.utc).isoformat(), "actor": OWNER_EMAIL}
        await db.system_settings.update_one(
            {"_id": _ID}, {"$set": {"active": body.active},
                           "$push": {"events": {"$each": [event], "$slice": -1000}}}, upsert=True)
        return {"active": body.active}

    async def middleware(request: Request, call_next):
        path = request.url.path
        if path in _EXEMPT or _app_shell(path) or _asset_request(request.method, path) or request.method == "OPTIONS":
            return await call_next(request)
        # The public website and static UI assets stay available. API routes and
        # known non-API learner routes are blocked independently of client UI.
        protected = (_standalone_learning(path) or path == "/api" or path.startswith("/api/") or
                     path.startswith(("/quiz-app", "/user/", "/quiz/", "/gridfs/", "/media/", "/assets/", "/public_assets/",
                                      "/micro-lessons", "/lessons/", "/billing/")))
        if not protected:
            return await call_next(request)
        try:
            active = await status()
            authorization = request.headers.get("authorization", "")
            scheme, _, token = authorization.partition(" ")
            credentials = HTTPAuthorizationCredentials(scheme=scheme, credentials=token) if scheme and token else None
            is_owner = await owner(credentials) if active and credentials else False
        except Exception:
            return JSONResponse({"detail": "Maintenance status unavailable"}, status_code=503,
                                headers={"Cache-Control": "no-store"})
        if not active or is_owner:
            return await call_next(request)
        if _standalone_learning(path) and request.method == "GET" and not request.headers.get("authorization"):
            # Navigation cannot send a bearer token. Re-fetch for the owner from
            # the existing browser session; everyone else sees the app message.
            language = path.split('/')[1] if path.rstrip('/') != '/bok' else 'no'
            html = ("<!doctype html><meta charset='utf-8'><title>Thai2Drive</title>"
                    "<script>(async function(){const lang=localStorage.getItem('bok_lang');const back='/app/'+(['no','th','en'].includes(lang)&&location.pathname.replace(/\\/$/,'')==='/bok'?lang:'" + language + "');"
                    "try{for(const key of ['authToken','t2d_token','admin_token']){const token=localStorage.getItem(key);if(!token)continue;"
                    "const r=await fetch(location.pathname,{headers:{Authorization:'Bearer '+token},cache:'no-store'});"
                    "if(r.ok){const html=await r.text();document.open();document.write(html);document.close();return;}}"
                    "location.replace(back);"
                    "}catch(e){location.replace(back);}})();</script>")
            return HTMLResponse(html, headers={"Cache-Control": "no-store"})
        return JSONResponse({"detail": "maintenance", "maintenance": True}, status_code=503,
                            headers={"Cache-Control": "no-store", "Retry-After": "60"})

    return router, middleware
