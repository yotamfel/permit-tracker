# Permit Tracker App — Project Specification

**Purpose of this document:** This is the build spec for Claude Code. It describes what to build, the data model, the architecture, and the MVP scope. Where a decision was deferred to a later phase, it is explicitly marked **[POST-MVP]** — do not build that part now.

---

## 1. Product Summary

A web application that tracks worldwide permits, quotas, lotteries, and fast-selling tickets for treks, national parks, camping, diving, and seasonal tourist attractions. Each destination has a known release *pattern* (see §5). Users browse destinations, see a checklist of what's needed to apply, and subscribe to email alerts before the release window opens. Some destinations are free to view; unlocking full detail/alerts for a destination is a one-time paid purchase **per destination**, not a site-wide subscription.

## 2. Tech Stack (fixed — do not deviate without asking)

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL via Neon
- **Frontend:** React (Vite), Tailwind CSS
- **Hosting:** Vercel (frontend) + Railway (backend/cron jobs) — matches existing setup
- **Payments:** Stripe (web only — see §9, no mobile IAP in this phase)
- **Email:** Resend or SendGrid (either is fine — pick one, note the choice in README)
- **i18n:** `react-i18next` on frontend; translatable content stored in DB (§4.3), static UI strings in locale JSON files
- **Auth:** Simple email/password or magic-link auth (Supabase Auth, Clerk, or a custom FastAPI JWT flow — pick the simplest reliable option, document the choice)

## 3. Explicit Non-Goals for This Phase — DO NOT BUILD

- ❌ Native mobile apps / App Store / Google Play submission / Capacitor wrapper
- ❌ In-App Purchase (IAP) integration of any kind
- ❌ WhatsApp, SMS, or push notifications — **email only**
- ❌ Automatic scraping-and-apply of content changes — monitoring only *flags* diffs for human review (§8), never auto-publishes
- ❌ Multi-currency pricing — USD only for now
- ❌ Social login (Google/Apple sign-in) — plain email auth is enough
- ❌ Admin analytics dashboards beyond a basic list view

If in doubt whether something is in scope, treat it as out of scope and flag it instead of building it.

## 4. Database Schema

Use SQLAlchemy models + Alembic migrations. All tables use UUID primary keys unless noted. All tables have `created_at`/`updated_at` timestamps (omitted below for brevity — include them everywhere).

### 4.1 `destinations`
Core record for each permit/quota destination.

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| country | text | e.g. "Peru" — store in English canonically, translate via §4.3 |
| category | enum | `trek`, `national_park_entry`, `camping`, `diving`, `wildlife_safari`, `thru_hike`, `tourist_attraction`, `seasonal_nature_event` |
| name | text | canonical English name, e.g. "Inca Trail" |
| mechanism_type | enum | `fixed_daily_quota`, `lottery`, `rolling_window`, `fixed_annual_date`, `weekly_release`, `guided_tour_only`, `single_operator_annual_quota`, `first_come_first_served` |
| mechanism_config | JSONB | structured config, shape depends on `mechanism_type` — see §5 |
| issuing_authority | enum | `government`, `tribal`, `commercial`, `mixed` |
| competitiveness_level | enum | `low`, `medium`, `high`, `very_high` |
| source_url | text | official source page |
| last_verified_at | timestamptz | set manually when a human confirms the data is current |
| is_published | boolean | default `false` — a destination is invisible to users until explicitly published |
| price_usd | numeric | one-time unlock price for this destination |

### 4.2 `checklist_items`
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| destination_id | UUID FK → destinations | |
| item_type | enum | `document`, `action`, `gear`, `payment` |
| order_index | integer | display order |
| is_required | boolean | |
| text_key | text | key into translation table, not raw text (see §4.3) |

### 4.3 `translations`
Generic translation table so any translatable field (destination name, description, checklist item text, instructions) can be localized without schema changes per table.

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| entity_type | text | e.g. `destination.name`, `destination.description`, `checklist_item.text`, `destination.instructions` |
| entity_id | UUID | id of the row being translated |
| locale | text | ISO code, e.g. `en`, `he`, `es` |
| value | text | translated content |

English (`en`) is the **source of truth / official language** — every entity must have an `en` row before publishing. Other locales are optional and fall back to English if missing.

### 4.4 `users`
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| email | text unique | |
| password_hash | text | nullable if using magic link |
| preferred_locale | text | default `en` |
| theme_preference | enum | `light`, `dark`, `system` — default `system` |

### 4.5 `purchases`
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| user_id | UUID FK | |
| destination_id | UUID FK | |
| platform | enum | `web` (only value used in this phase, but keep the enum extensible for `ios`/`android` later) |
| amount_usd | numeric | |
| stripe_payment_intent_id | text | |
| status | enum | `pending`, `completed`, `refunded`, `failed` |

A user "owns" a destination if there is a `completed` purchase row for that (user_id, destination_id) pair. No separate entitlements table needed — query purchases directly.

### 4.6 `alert_subscriptions`
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| user_id | UUID FK | |
| destination_id | UUID FK | |
| lead_time_days | integer | how many days before release to notify, default 7 |
| is_active | boolean | |

Only purchasable/owned destinations can have an active subscription — enforce this in the API layer, not just the UI.

### 4.7 `notification_log`
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| subscription_id | UUID FK | |
| sent_at | timestamptz | |
| channel | text | `email` (only value for now) |
| status | enum | `sent`, `failed` |

### 4.8 `monitoring_snapshots`
Stores a fetched snapshot of each destination's source page for diffing.

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| destination_id | UUID FK | |
| content_hash | text | hash of extracted text, for cheap comparison |
| raw_text_excerpt | text | truncated extracted text (not full HTML) |
| captured_at | timestamptz | |

### 4.9 `monitoring_diffs`
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| destination_id | UUID FK | |
| previous_snapshot_id | UUID FK | |
| new_snapshot_id | UUID FK | |
| diff_summary | text | |
| review_status | enum | `pending`, `approved`, `dismissed` |
| reviewed_at | timestamptz | nullable |

### 4.10 `admin_users`
Simple table for who can log into the admin panel (§7). Do not overbuild — a flat allow-list of emails checked at login is enough for MVP.

## 5. Mechanism Types — Config Shapes

`mechanism_config` (JSONB on `destinations`) shape depends on `mechanism_type`. Document these exact shapes in code comments and validate with Pydantic models — do not accept arbitrary JSON.

- **`fixed_daily_quota`**: `{ "daily_quota": int, "booking_opens_days_before": int }`
- **`lottery`**: `{ "application_window_start": "MM-DD", "application_window_end": "MM-DD", "results_date": "MM-DD" }` (annual recurring dates, month-day only, no year)
- **`rolling_window`**: `{ "days_before_travel_date": int }`
- **`fixed_annual_date`**: `{ "typical_release_date": "MM-DD", "release_time": "HH:MM", "timezone": "IANA tz string" }`
- **`weekly_release`**: `{ "release_weekday": "tuesday", "release_time": "HH:MM", "timezone": "...", "weeks_ahead": int }`
- **`guided_tour_only`**: `{ "note": "no self-service release date — booking depends on tour operator availability" }`
- **`single_operator_annual_quota`**: `{ "operator_name": str, "annual_quota": int, "typical_booking_lead_time_months": int }`
- **`first_come_first_served`**: `{ "typical_booking_lead_time_months": int }`

The 30 MVP destinations (§10) cover every one of these types — make sure the schema and UI both render each type correctly before considering the MVP done.

## 6. Internationalization (i18n)

- **Official/default language: English.** All source content is authored in English first.
- Site must support switching languages via a UI toggle (language switcher in header, persisted to `users.preferred_locale` for logged-in users, else `localStorage`).
- Ship with **English and Hebrew** as the two implemented locales for MVP; architecture must make adding a third locale trivial (just add translation rows, no code changes).
- Use `react-i18next` with namespace-based JSON files for static UI strings (`/locales/en/common.json`, `/locales/he/common.json`, etc.).
- Dynamic content (destination names, checklist items) is fetched from the `translations` table (§4.3) and falls back to English if the active locale has no row.
- Hebrew is RTL — the UI must flip layout direction correctly when Hebrew is active (`dir="rtl"` on `<html>`, and Tailwind RTL-aware utility usage or logical properties).

## 7. Theming (Light/Dark Mode)

- Implement via Tailwind's `dark:` class strategy (not the `media` strategy) so it can be toggled independently of OS settings.
- Toggle control in the header, three-state: light / dark / system.
- Persist choice to `users.theme_preference` for logged-in users, else `localStorage`.
- Apply the `dark` class to `<html>` on load before first paint (avoid flash of wrong theme — use a small inline script in `index.html`).

## 8. Monitoring Job (Human-in-the-loop, not autonomous)

- A scheduled job (Railway cron or GitHub Actions, runs weekly) iterates over all published destinations.
- For each, fetch the `source_url`, extract visible text, compute a hash, compare to the latest `monitoring_snapshots` row.
- If different: create a new snapshot row **and** a `monitoring_diffs` row with `review_status = pending`.
- **Never auto-update `destinations.mechanism_config` or checklist content from this job.** It only surfaces the diff.
- Build a minimal admin view (§ below) listing pending diffs with old/new text side by side, and an "approve" (mark reviewed, manually edit destination if needed) / "dismiss" action.

## 9. Payments (Web-Only, Per-Destination)

- Stripe Checkout (hosted page is fine — do not build a custom card form).
- Flow: user selects a destination → "Unlock for $X" → Stripe Checkout → on success webhook, create a `completed` row in `purchases`.
- Implement the Stripe webhook endpoint carefully (verify signature, handle idempotency — a webhook can fire more than once for the same event).
- **No subscription/recurring billing in this phase** — every purchase is a one-time payment for permanent access to that one destination's full detail + alerts.
- **[POST-MVP]** Mobile app + IAP + App Store/Play Store submission. Architecture should not block this later, but do not build it now.

## 10. MVP Destination Scope — 30 Destinations

Populate `destinations` with exactly these 30 to start (full detail, all 6 categories, all 9 mechanism types represented). Use English names; country field in English. A companion spreadsheet with fuller notes on all researched destinations (102 total) exists separately — only these 30 get full checklist content for MVP; the rest can be added as unpublished stub rows later.

**Fixed daily quota:** Inca Trail (Peru) · Mountain Gorilla Trekking – Volcanoes NP (Rwanda) · Sipadan (Malaysia) · Corcovado NP – Sirena Station (Costa Rica)

**Lottery:** Half Dome (USA) · Mount Whitney (USA) · Angels Landing (USA) · Grand Canyon Colorado River Rafting (USA) · The Wave / Coyote Buttes North (USA) · Wonderland Trail (USA) · Yellowstone Backcountry Permit (USA)

**Rolling window:** Machu Picchu entrance tickets (Peru) · Statue of Liberty Crown Access (USA) · Eiffel Tower Summit Access (France)

**Fixed annual date:** Havasupai Falls (USA) · West Coast Trail (Canada) · Milford Track (New Zealand) · Routeburn Track (New Zealand)

**Weekly release:** Anne Frank House (Netherlands)

**Registration + lottery (two-stage — treat as a `lottery` variant with two config windows, see note below):** PCT Long-distance Permit (USA) · John Muir Trail (USA)

**First-come-first-served / advance booking:** Torres del Paine W Circuit (Chile) · Otter Trail (South Africa) · Chirripó National Park (Costa Rica)

**Single operator annual quota:** Son Doong Cave (Vietnam)

**Guided tour only:** Antelope Canyon (USA) · Skellig Michael (Ireland) · Silver Bank Whale Swimming (Dominican Republic)

**Wildlife safari quota:** Tiger Reserve Safaris — Ranthambore/Corbett/Bandhavgarh (India)

> **Note on PCT/JMT:** these have two distinct dates users care about (registration window open, and the release/lottery day itself). If the `lottery` config shape in §5 doesn't cleanly express "two separate windows," extend it with an optional `registration_window` field rather than inventing a new mechanism_type — flag this to the user if it comes up during implementation.

## 11. Core User Flows

1. **Browse (no login required):** list/grid of all published destinations, filterable by country, category, mechanism type, competitiveness. Each card shows name, category icon, competitiveness badge, and "next known release" if computable from `mechanism_config`.
2. **Destination detail page (free preview):** shows destination name, mechanism explanation in plain language, competitiveness level. Checklist and exact dates are blurred/teased with an "Unlock for $X" CTA if not purchased.
3. **Purchase:** Stripe Checkout → on success, full checklist + precise mechanism details + alert subscription option unlock immediately.
4. **Subscribe to alert:** only available post-purchase; pick lead time (default 7 days before release); creates `alert_subscriptions` row.
5. **Email delivery:** a separate scheduled job checks active subscriptions against each destination's computed next release date and sends email at the configured lead time. (Computing "next release date" from `mechanism_config` is real logic — for `rolling_window` and `fixed_annual_date` types this is straightforward math; for `lottery` and `weekly_release` types use the recurring windows in the config directly; `guided_tour_only` and `first_come_first_served` types have no computable date — for those, the alert instead reminds the user "book as early as possible for your travel date," triggered relative to a travel date the user enters, not a fixed release.)
6. **Admin panel (behind `admin_users` allow-list):** CRUD on destinations, checklist items, translations; review queue for `monitoring_diffs`.

## 12. Suggested API Surface (adjust as needed, but keep it RESTful and documented via FastAPI's auto-generated OpenAPI docs)

```
GET    /api/destinations                 # list, filterable
GET    /api/destinations/{id}            # detail (respects ownership for gated fields)
GET    /api/destinations/{id}/checklist  # only returns content if owned
POST   /api/auth/signup
POST   /api/auth/login
GET    /api/me
PATCH  /api/me                           # update locale/theme preference
POST   /api/checkout/{destination_id}    # creates Stripe Checkout session
POST   /api/webhooks/stripe              # Stripe webhook receiver
GET    /api/me/purchases
POST   /api/subscriptions                # subscribe to alerts for an owned destination
DELETE /api/subscriptions/{id}
# Admin (all require admin auth):
GET    /admin/api/monitoring/diffs?status=pending
POST   /admin/api/monitoring/diffs/{id}/approve
POST   /admin/api/monitoring/diffs/{id}/dismiss
CRUD   /admin/api/destinations
CRUD   /admin/api/checklist-items
CRUD   /admin/api/translations
```

## 13. Suggested Repo Structure

```
/backend
  /app
    /models        # SQLAlchemy models
    /schemas        # Pydantic schemas
    /api            # route modules
    /services       # stripe, email, monitoring logic
    /jobs           # scheduled job entrypoints (monitoring, alert dispatch)
  /alembic          # migrations
/frontend
  /src
    /pages
    /components
    /locales        # en/, he/ JSON files
    /lib            # api client, theme/i18n context
README.md
PROJECT_SPEC.md      # this file
```

## 14. Environment Variables (document all of these in a `.env.example`)

```
DATABASE_URL=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PUBLISHABLE_KEY=
EMAIL_PROVIDER_API_KEY=
JWT_SECRET=
FRONTEND_URL=
```

## 15. Definition of Done for MVP

- [ ] All 6 categories and all 9 mechanism types render correctly on the frontend with real data from the 30 destinations
- [ ] User can sign up, log in, browse free previews, purchase a destination, see the unlocked checklist, and set an alert
- [ ] Stripe webhook reliably marks purchases complete (test with Stripe CLI test events, including duplicate delivery)
- [ ] Alert email actually sends at the correct computed time for at least one destination of each mechanism type
- [ ] Language switch (EN ⇄ HE) works site-wide, including RTL layout for Hebrew
- [ ] Light/dark/system theme toggle works and persists
- [ ] Admin can log in, edit a destination, and see/approve/dismiss a monitoring diff
- [ ] Monitoring job runs on schedule and creates diff rows without ever silently overwriting destination content

## 16. Open Questions to Flag Back to the User (do not silently decide these)

- Exact Stripe price per destination (flat $X for all 30, or does price vary by competitiveness level?)
- Which auth provider to use (Clerk/Supabase Auth/custom JWT) — pick the fastest to implement and confirm
- Which email provider (Resend vs SendGrid) — pick one and confirm
- Domain name / hosting URLs for Vercel + Railway once ready to deploy
