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

## 3. Paddle (Merchant of Record - handles global VAT/sales tax for us)

1. Create a Paddle account at paddle.com and verify it as an Israel-based seller
   (Israel is a supported seller country). Start in **Sandbox** mode first - it's a
   separate environment from Production with its own keys/catalog, good for testing
   before real money moves. While in Sandbox, also set
   `PADDLE_API_BASE_URL=https://sandbox-api.paddle.com` (the app defaults to the
   production API URL).
2. Catalog → Products → create one product (e.g. "SlotScout destination unlock"),
   then add one **Price** to it: $6.99 USD, one-time (not recurring) - every
   destination on the site is the same price, so this single Price ID covers all of
   them. Copy the Price ID (`pri_...`).
3. Developer Tools → Authentication → create an **API key** (this is the server-side
   secret - keep it out of any client-side code) with exactly: Customers (Read +
   Write), Transactions (Write only) - nothing else. Also create a separate
   **client-side token** there (safe to expose in frontend code - it's what
   Paddle.js uses in the browser to open the checkout overlay).
4. Checkout → Checkout settings → **Default payment link** - required before any
   transaction/checkout can be created at all, even with a custom `checkout.url`.
   Set it to `https://myslotscout.com` (Sandbox accepts any domain, including
   localhost, but using the real domain here means one less thing to redo for
   Production later).
5. Checkout → Website Approval → Domain Approval → **Add a new domain** →
   `myslotscout.com` → Submit for Approval (Sandbox approves near-instantly;
   Production can take longer). A transaction's `checkout.url` 400s with
   `transaction_checkout_url_domain_is_not_approved` until this is done, even
   after the default payment link above is set - they're two separate checks.
6. Developer Tools → Notifications → add a destination:
   - URL: `https://<your-railway-backend-url>/api/webhooks/paddle`
   - Events: `transaction.completed`, `transaction.payment_failed`, `adjustment.updated`
   - Copy the **notification's own secret key** (starts `pdl_ntfset_...` in the UI,
     used as the webhook signing secret)
7. Give me the API key, client-side token, webhook secret, and Price ID (as
   `PADDLE_API_KEY`, `VITE_PADDLE_CLIENT_TOKEN`, `PADDLE_WEBHOOK_SECRET`,
   `PADDLE_PRICE_ID`).
8. When you're ready for real payments: Paddle requires a short account verification
   (business details, ~1-2 business days) before you can go live. Once approved,
   switch to **Production** in the Paddle dashboard, repeat steps 2-6 there (Sandbox
   and Production have entirely separate catalogs/keys/domain approvals), remove the
   `PADDLE_API_BASE_URL` override (or set it explicitly to `https://api.paddle.com`)
   so requests go to the live API, and set `VITE_PADDLE_ENVIRONMENT` to anything
   other than `sandbox` (or unset it) on the frontend.

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
