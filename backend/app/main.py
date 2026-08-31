from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, checkout, contact, destinations, subscriptions, webhooks
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Permit Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(destinations.router)
app.include_router(auth.router)
app.include_router(auth.me_router)
app.include_router(checkout.router)
app.include_router(webhooks.router)
app.include_router(subscriptions.router)
app.include_router(contact.router)
app.include_router(admin.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
