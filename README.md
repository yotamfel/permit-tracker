# Permit Tracker

A web app that tracks worldwide permits, quotas, lotteries and fast-selling tickets for treks,
national parks, camping, diving, safaris and seasonal tourist attractions. Users browse
destinations for free, unlock full detail (checklist + exact dates + alerts) with a one-time
per-destination payment, and get emailed before the release window opens.

Built from `PROJECT_SPEC.md` + `PROJECT_SPEC_ADDENDUM.md` (both in this repo's `docs/` folder are
the originals under `~/Downloads`; keep them as the source of truth for scope questions).

## Decisions made while building (per the spec's own "flag back to the user" list)

- **Pricing:** flat $4.99 per destination (not tiered by competitiveness).
- **Auth:** custom FastAPI JWT (email + password), not Clerk/Supabase Auth.
- **Email:** Resend.
- **Destination count:** the spec's §10 list is headed "30 MVP Destinations" but only names 29
  (counted explicitly - see `backend/app/jobs/seed_data.py` docstring). Built with the 29 named;
  a 30th can be added later via the admin panel if you have one in mind.
- **"9 mechanism types" / "6 categories":** the spec's prose says 9 mechanism types and 6
  categories, but the schema in §4.1 literally enumerates 8 of each. Built against the 8-value
  enums (the schema is authoritative), and the 29 seeded destinations cover all 8 of both. The
  PCT/John Muir two-stage process reuses `lottery` with an optional `registration_window` field,
  per the spec's own explicit instruction - it is not a 9th mechanism type.
- **Multilingual content (addendum §3): paused, English-only for now, at your request.** The
  `translations` table / `mechanism_config` API / react-i18next setup all already support arbitrary
  locales with no code changes needed later - only content and a couple of feature flags are
  paused. What's archived for when this resumes:
  - `future-i18n/frontend-locales/{he,de,fr,es,pt-BR}/common.json` - fully translated static UI
    strings for all 5 non-English locales (moved out of `frontend/src/locales/`, which now only
    has `en/`).
  - `he` destination names (`name_he` field in `backend/app/jobs/seed_data.py`) and `he`
    general-requirement title/description text (`backend/app/jobs/seed_data_requirements.py`) are
    still sitting in those files but the seed scripts no longer load them into the DB.
  - `backend/app/jobs/seed_i18n.py` is a ready loader for whenever a complete `seed_data_i18n.py`
    data file exists. A background agent's attempt to machine-generate one only got through 5 of
    the 29 destinations (and 0 general requirements) before it was stopped when you asked to pause
    this work - that partial draft is archived at
    `future-i18n/backend-drafts/seed_data_i18n.partial.py` as a starting point, not something to
    load as-is.
  - To resume: move the archived locale files back into `frontend/src/locales/`, re-add them to
    `frontend/src/lib/i18n.js`'s `resources` map and `SUPPORTED_LOCALES`, un-hide the switcher in
    `frontend/src/components/Header.jsx`, add locales back to `backend/app/core/config.py`'s
    `supported_locales`, and re-enable the commented-out `he`/other-locale inserts in `seed.py` /
    `seed_requirements.py`.
  - Hebrew RTL layout (original spec §6) was built and tested and can come back the same way -
    it's just currently unused rather than removed.
- **Stub destinations:** the extra ~73 destinations researched in
  `docs/permits_worldwide_database.xlsx` were imported as unpublished stub rows
  (`app/jobs/stub_import.py`) with inferred (not hand-verified) mechanism/category/competitiveness
  and no `source_url` (never fabricated). The original Hebrew research note is preserved as each
  stub's `he` description translation so no research is lost (this is original source research, not
  a UI translation, so it wasn't affected by the multilingual-content pause above).
- **Platform: website first (per your instruction).** The spec's own non-goals (§3) already exclude
  native mobile apps / IAP / app-store submission from this phase, so nothing app-specific has been
  built to archive. The one deliberately future-proofed spot is `purchases.platform`
  (`backend/app/models/enums.py`'s `Platform` enum), which already has `ios`/`android` values sitting
  unused alongside `web` - exactly as the spec asked, so a mobile client can reuse the same
  `purchases` table later without a schema change.

## Tech stack

- **Backend:** FastAPI + SQLAlchemy 2.0 + Alembic, Python 3.13
- **Database:** PostgreSQL (Neon)
- **Frontend:** React 18 + Vite + Tailwind CSS + react-i18next + react-router
- **Payments:** Stripe Checkout (hosted page, one-time payments)
- **Email:** Resend
- **Hosting:** Vercel (frontend), Railway (backend API + cron jobs)

## Repo layout

```
backend/
  app/
    models/       SQLAlchemy models (destinations, translations, purchases, general_requirements, ...)
    schemas/       Pydantic request/response schemas + mechanism_config validators (§5)
    api/            FastAPI route modules (destinations, auth, checkout, webhooks, subscriptions, admin)
    services/       stripe, email (Resend), i18n lookup, release-date math, monitoring
    jobs/           one-off/scheduled entrypoints: seed, stub_import, create_admin,
                     monitor_destinations (weekly cron), dispatch_alerts (daily cron)
  alembic/          migrations (generate the first one once DATABASE_URL is real - see SETUP_GUIDE.md)
frontend/
  src/
    pages/          Browse, DestinationDetail, Login, Signup, Account, Admin
    components/     Header (nav + theme toggle)
    locales/        en/common.json (static UI strings) - see future-i18n/ for the other 5
    lib/            api client, auth/theme context, i18n setup
docs/
  permits_worldwide_database.xlsx   the 102-destination research spreadsheet you provided
future-i18n/
  frontend-locales/  archived he/de/fr/es/pt-BR common.json translations (paused, not deleted)
```

## Local development

**Backend:**
```
cd backend
venv\Scripts\python.exe -m pip install -r requirements.txt   # already done once
copy .env.example .env   # fill in real values - see SETUP_GUIDE.md
venv\Scripts\python.exe -m alembic upgrade head
venv\Scripts\python.exe -m app.jobs.seed
venv\Scripts\python.exe -m app.jobs.seed_requirements
venv\Scripts\python.exe -m app.jobs.stub_import
venv\Scripts\python.exe -m app.jobs.create_admin you@example.com yourpassword
venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
API docs at `http://localhost:8000/docs` (FastAPI auto-generated OpenAPI UI - also useful for
managing checklist items / translations directly, since the admin frontend doesn't have dedicated
screens for those yet - see "Known gaps" below).

**Frontend:**
```
cd frontend
npm install   # already done once
copy .env.example .env.local
npm run dev
```
Runs at `http://localhost:5173`.

## Known gaps / next steps

- The admin **frontend** has full CRUD for destinations and the monitoring-diff review queue, but
  not dedicated screens for checklist items / translations / general-requirements yet - the
  backend API for all of those is complete and documented at `/docs`, so they're usable today via
  the OpenAPI UI or a script; a UI is the natural next increment.
- No automated test suite yet (not called for explicitly, but worth adding before real traffic).
- `source_url` values for the 29 MVP destinations are my best-knowledge real official links, not
  yet human-verified - `last_verified_at` is intentionally left null so an admin confirms each one
  in the admin panel before fully trusting it (the monitoring job's diff-review workflow exists
  exactly for this ongoing upkeep).
