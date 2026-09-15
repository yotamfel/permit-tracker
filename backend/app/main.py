from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - registers every model so cross-model relationships resolve regardless of route import order
from app.api import admin, auth, checkout, contact, destinations, feedback, subscriptions, user_files, watchlist, webhooks
from app.core.config import get_settings
from app.core.deps import get_db
from app.core.monitoring import init_sentry
from app.core.rate_limit import limiter
from app.models.destination import Destination

init_sentry()
settings = get_settings()

app = FastAPI(title="SlotScout API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# This is a pure JSON API (the frontend is a separate SPA on its own domain),
# so a strict CSP is safe everywhere except the auto-generated docs pages,
# which load their own scripts/styles from a CDN.
_DOCS_PATHS = {"/docs", "/redoc", "/openapi.json"}


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    if request.url.path not in _DOCS_PATHS:
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response


app.include_router(destinations.router)
app.include_router(auth.router)
app.include_router(auth.me_router)
app.include_router(checkout.router)
app.include_router(webhooks.router)
app.include_router(subscriptions.router)
app.include_router(contact.router)
app.include_router(admin.router)
app.include_router(feedback.router)
app.include_router(user_files.router)
app.include_router(watchlist.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


# Served from the frontend's own domain via a Vercel rewrite (see
# frontend/vercel.json) - a sitemap only counts for a domain when it's
# reachable at <that domain>/sitemap.xml, so this can't just live on the
# API's own Railway domain.
@app.get("/sitemap.xml")
def sitemap(db: Session = Depends(get_db)) -> Response:
    settings = get_settings()
    base = settings.frontend_url.rstrip("/")
    urls = [f"{base}{p}" for p in ["/", "/catalog", "/signup", "/contact", "/terms", "/privacy", "/methodology"]]
    published_ids = db.query(Destination.id).filter(Destination.is_published.is_(True)).all()
    urls += [f"{base}/destinations/{d_id}" for (d_id,) in published_ids]
    body = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>'
    return Response(content=xml, media_type="application/xml")
