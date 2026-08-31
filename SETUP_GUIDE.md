# Setup Guide — accounts & deployment

This walks through the external accounts/resources this app needs. Per how we've done
this on other projects, you create these yourself (so they're under your own billing
and identity); once you hand me the resulting keys/URLs I'll wire them in and run
migrations/seeding/tests directly.

## 1. GitHub repo

1. Create a new empty repo (e.g. `permit-tracker`) at github.com/new - don't
   initialize with a README (this repo already has one).
2. Tell me the repo URL and I'll add the remote and push what's already committed
   locally.

## 2. Neon (Postgres database)

1. Create a project at neon.tech.
2. Copy the pooled connection string (the one with `-pooler` in the hostname is fine
   for the API; use the direct/unpooled one for Alembic migrations if Neon's pooler
   gives you trouble with DDL - usually not necessary).
3. Give me the connection string in the `postgresql+psycopg://...` form (Neon gives
   you a plain `postgresql://` string - just change the scheme prefix, everything
   after `://` stays the same) → I'll put it in `backend/.env` as `DATABASE_URL`,
   run the initial Alembic migration, and seed all the destination/requirement/
   translation data.

## 3. Stripe

1. Create/use a Stripe account, switch to **test mode** first.
2. Developers → API keys: copy the **Secret key** (`sk_test_...`) and
   **Publishable key** (`pk_test_...`).
3. Developers → Webhooks → Add endpoint:
   - URL: `https://<your-railway-backend-url>/api/webhooks/stripe` (use the Stripe
     CLI's `stripe listen --forward-to localhost:8000/api/webhooks/stripe` for local
     testing before you have a deployed URL)
   - Event: `checkout.session.completed`
   - Copy the **Signing secret** (`whsec_...`)
4. Give me the secret key, publishable key, and webhook signing secret.
5. When you're ready for real payments, flip to live mode and repeat steps 2-4 for
   the live keys.

## 4. Resend (email)

1. Create an account at resend.com.
2. Add and verify a sending domain (or use their shared testing domain while you set
   things up - real delivery needs a verified domain).
3. Create an API key, give it to me as `EMAIL_PROVIDER_API_KEY`.
4. Tell me the "from" address you want alert emails sent from (`EMAIL_FROM`) - must
   be on the verified domain.

## 5. Railway (backend hosting + cron jobs)

1. Create a new project at railway.app, connect it to the GitHub repo (root
   directory: `backend`).
2. Add all the backend env vars from `backend/.env.example` (Railway → Variables).
3. Railway auto-detects the `Procfile` for the web process.
4. Add **two Cron Job services** in the same project, both pointed at the same repo
   subdirectory:
   - `python -m app.jobs.monitor_destinations` — schedule: weekly (e.g. `0 6 * * 1`)
   - `python -m app.jobs.dispatch_alerts` — schedule: daily (e.g. `0 7 * * *`)
5. Give me the deployed backend URL (`https://....up.railway.app`) - I'll set it as
   `FRONTEND_URL`'s counterpart on the frontend side (`VITE_API_URL`).

## 6. Vercel (frontend hosting)

1. Import the GitHub repo at vercel.com/new, set root directory to `frontend`.
2. Add env var `VITE_API_URL` = your Railway backend URL.
3. Deploy. `frontend/vercel.json` already handles SPA client-side routing.
4. Give me the deployed frontend URL - I'll set it as `FRONTEND_URL` in the backend
   env (used for Stripe Checkout success/cancel redirect URLs and CORS).

## 7. Domain (optional)

If you want a custom domain, add it in Vercel's project settings (frontend) and
point your DNS per Vercel's instructions; the backend can stay on its Railway
subdomain or get its own custom domain too - just update `VITE_API_URL` /
`FRONTEND_URL` to match either way.

---

Once you've done steps 1-4 (accounts + keys), send them my way and I'll handle
everything else: migrations, seeding, local verification, and (once 5-6 are linked)
confirming the deployed app works end-to-end.
