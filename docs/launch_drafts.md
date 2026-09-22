# Launch drafts - distribution/marketing copy

Prepared 2026-09-22, held for the launch that begins once Paddle Production
checkout is confirmed working (it is, as of this writing - see
`project_permit_tracker.md` memory). Facts (price $6.99 one-time, referral
$3.99, 141 destinations, feature list) pulled directly from `Pricing.jsx`/
`common.json` at time of writing - re-check destination count before using
if this sits unused for a while.

## Product Hunt

**Tagline** (<=60 chars):

> Stop losing bucket-list trips to missed permit deadlines

**Description:**

> SlotScout tracks application windows, quotas, and lotteries for 141 permits that sell out fast - Half Dome, Torres del Paine, Aconcagua, Antarctica, and more. Browsing, reading how each system works, and setting free email alerts costs nothing. Pay $6.99 (one-time, no subscription) only when you want the full prep checklist, exact documents, and direct application links for one destination.

**First comment (from the maker):**

> Hey! Built this solo after almost missing the Half Dome permit lottery window - the info was scattered across a government PDF, three forum threads, and a Facebook group. SlotScout puts the whole process (documents, fees, exact dates, an alert before the window opens) on one page per destination.
>
> It's free to browse and set alerts. You only pay when you actually want the prep checklist for a specific destination ($6.99 one-time, no subscription). Would love feedback, especially on which destinations are missing - always adding more.

## Reddit #1 - r/solotravel (personal story, broad audience)

**Title:** I almost missed the Half Dome permit lottery deadline, so I built a tracker for it (and 140 other permits)

**Body:**

> A couple months ago I nearly blew a Half Dome trip because I didn't realize the lottery application window had a hard closing date - found out from a random forum comment with like two days to spare.
>
> That turned into a bit of an obsession, so I built [SlotScout](http://myslotscout.com) - it tracks the application windows, quotas, and lotteries for 141 permits/trips that sell out fast (national parks, treks, a few "sells out in minutes" events too), and sends you an email alert before the window opens.
>
> Browsing and alerts are free. If you want the actual prep checklist (documents, fees, exact process) for a specific destination it's $6.99 one-time, no subscription.
>
> Not trying to be spammy about it - genuinely built it because I got burned, figured others here have too. Happy to answer questions, and if there's a destination missing I'd love to know.

## Reddit #2 - r/Ultralight or r/CampingandHiking (permit-savvy audience)

**Title:** Built a site that tracks permit windows for backcountry trips (Half Dome, JMT, Wonderland, etc.) so I stop missing them

**Body:**

> Permit season always sneaks up on me - different park, different portal, different exact date/time the window opens, usually buried in a PDF nobody reads until it's too late.
>
> Made [SlotScout](http://myslotscout.com) to fix that for myself, then kept adding destinations. It's currently tracking 141 permit systems (a lot of US/international backcountry permits, plus some non-hiking stuff like Torres del Paine and a few lotteries). Each one gets a plain-language explanation of exactly how the system works, a prep checklist, and an optional email alert before the window opens.
>
> Free to browse/set alerts; $6.99 one-time if you want the full checklist for a specific trip.
>
> Genuinely curious what permits people here fight with most that I might be missing - always looking to add more.

## Reddit #3 - r/SideProject (builder/solo-dev angle)

**Title:** Launched SlotScout - a solo-built tool tracking 141 hard-to-get travel permits/lotteries, $6.99 one-time per destination

**Body:**

> Been building this solo for a while - [SlotScout](http://myslotscout.com) tracks application windows/quotas/lotteries for 141 travel permits (national parks, treks, a few "sells out in minutes" events) and sends an alert before the window opens.
>
> Stack: FastAPI + Postgres backend, React/Vite frontend, deployed on Railway + Vercel, Paddle for payments (as Merchant of Record so I don't have to deal with global VAT/sales tax myself as a solo indie).
>
> Model: free to browse and set alerts, $6.99 one-time (no subscription) to unlock the full prep checklist for a specific destination. No ads, no affiliate links steering people to one operator over another.
>
> Would love feedback on the product itself, and happy to answer anything about the build/stack/payment setup for anyone tackling something similar.

## Facebook groups

Wikivoyage deprioritized (external links there are `rel="nofollow"` - no SEO
backlink value, and a fresh account posting a commercial link risks getting
flagged as spam; not worth the effort right now). Facebook groups are a
better bet: a warm, high-intent audience, and many groups explicitly allow
self-promo posts or have a regular self-promo thread. Claude has no Facebook
access, so these are drafts to paste in yourself once you've found/joined
relevant groups.

**Candidate groups to look for:** Yosemite Hiking / Backpacking groups (Half
Dome permits come up constantly), Pacific Crest Trail groups (e.g. "PCT
Class of [year]"), Torres del Paine / Patagonia trekking groups, Everest
Base Camp trekking groups, general backpacking/trip-planning groups (e.g.
"Backpacking Trip Planning", "Solo Female Travelers"), "National Park
Permits & Planning"-type groups if any exist. Check each group's rules
before posting - some ban self-promo outright, some only allow it in a
designated thread/day.

**Draft #1 - hiking/permit-specific groups (e.g. Yosemite, PCT, Patagonia):**

> Anyone else get caught out by a permit lottery deadline before? I nearly missed the Half Dome window because the closing date was buried in a PDF I didn't find until two days before it shut.
>
> Ended up building [SlotScout](http://myslotscout.com) to track this stuff - 141 permits/trips with hard windows (national parks, treks, a few lotteries), with a free email alert before each one opens. Free to browse and set alerts; $6.99 one-time if you want the full prep checklist for a specific trip.
>
> Figured this group would know exactly the pain I'm talking about. Happy to add a destination if it's missing, and would genuinely love feedback.

**Draft #2 - general travel-planning groups:**

> Sharing something I built after almost blowing a bucket-list trip - I nearly missed the application window for the Half Dome permit lottery because I found the deadline through a random forum comment, with two days to spare.
>
> Built [SlotScout](http://myslotscout.com) so that doesn't happen again - it tracks 141 permits/lotteries/quotas that sell out fast (national parks, treks, a few "opens for 10 minutes" events) and sends an alert before each window opens. Free to browse and set alerts; $6.99 one-time for the full checklist on a specific destination if you want it.
>
> Would love to know if there's a permit system that's burned you that I should add.

## Still to prepare

- Creator outreach list + pitch text
