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

> Hey! Built SlotScout to fix a problem I kept running into: permit and lottery info for popular trips and attractions is scattered across government PDFs, forum threads, and random posts, and it's easy to miss the actual application window. SlotScout puts the whole thing - documents, fees, exact dates, and an alert before the window opens - on one page per destination, currently covering 141 destinations worldwide. Would love feedback, especially on which destinations are missing.

(Earlier draft claimed a specific "almost missed the Half Dome lottery" incident - dropped per explicit user correction, 2026-09-23: not a real story, don't fabricate one. Also dropped pricing/money from this comment entirely per the same correction - the listing's own price field already covers that, no need to restate it here.)

**Note (2026-09-23):** the drafts below were rewritten to drop the "I almost missed the Half Dome lottery" anecdote - not a real incident, per explicit user correction - and to cut back on pricing detail to a single short clause rather than dwelling on it. Same fix as the Product Hunt first comment above.

## Product Hunt engagement log (pre-launch account warm-up)

**Lightmeter** (https://www.producthunt.com/products/lightmeter-2, film camera + light meter iOS app, "no AI, no account, nothing leaves your phone"):

> Don't even have an iPhone so can't actually try this, but I really like the positioning - "no AI, no account, nothing leaves your phone" cuts through a lot of noise right now. I'm building in a completely different space (travel/permits) and went a similar route in spirit - keeping it simple and honest instead of bolting on AI everywhere just because it's trendy. Upvoted, good luck with the launch.

## Product Hunt forum engagement (pre-launch account warm-up)

Reply drafted for an active PH forum thread - "Do solo makers need a UI/UX
designer?" (https://www.producthunt.com/p/runevr/do-solo-makers-need-a-ui-ux-designer,
468 upvotes/235 comments at time of writing). Purpose: genuine engagement to
warm up the account before the 2026-09-29 launch, not self-promotion (no
link to SlotScout in it).

> built SlotScout solo, mostly with AI helping on both code and design. honestly gets you pretty far fast. but the stuff AI won't catch is the stuff you only notice by actually using your own product like a stranger would.
>
> had destination pages where the description was just one giant block of text. looked "fine" until I actually sat and read it instead of just glancing at it while building. splitting it into paragraphs was a 2-line fix but the page felt completely different after.
>
> so for me it's less "AI vs designer" and more - you still have to be the one who slows down and actually looks at your own stuff critically. AI won't do that part for you.

## Reddit #1 - r/solotravel (broad audience)

**Title:** Built a tracker for permit/lottery deadlines on 141 bucket-list trips (Half Dome, Torres del Paine, Antarctica, etc.)

**Body:**

> Permit and lottery systems for popular trips are a mess to keep track of - different park, different portal, an application window that's easy to miss because it's buried in a government PDF or a random forum thread.
>
> Built [SlotScout](http://myslotscout.com) to put that in one place: 141 destinations worldwide, each with a plain-language explanation of how the system actually works, a prep checklist, and an optional email alert before the window opens. Free to browse and set alerts.
>
> Happy to answer questions, and if there's a destination missing I'd love to know.

## Reddit #2 - r/Ultralight or r/CampingandHiking (permit-savvy audience)

**Title:** Built a site that tracks permit windows for backcountry trips (Half Dome, JMT, Wonderland, etc.) so I stop missing them

**Body:**

> Permit season always sneaks up on me - different park, different portal, different exact date/time the window opens, usually buried in a PDF nobody reads until it's too late.
>
> Built [SlotScout](http://myslotscout.com) to fix that, then kept adding destinations - it's currently tracking 141 permit systems (a lot of US/international backcountry permits, plus some non-hiking stuff like Torres del Paine and a few lotteries). Each one gets a plain-language explanation of exactly how the system works, a prep checklist, and an optional email alert before the window opens. Free to browse and set alerts.
>
> Genuinely curious what permits people here fight with most that I might be missing - always looking to add more.

## Reddit #3 - r/SideProject (builder/solo-dev angle)

**Title:** Launched SlotScout - a solo-built tool tracking 141 hard-to-get travel permits/lotteries

**Body:**

> [SlotScout](http://myslotscout.com) tracks application windows/quotas/lotteries for 141 travel permits (national parks, treks, a few "sells out in minutes" events) and sends an alert before the window opens - built solo.
>
> Stack: FastAPI + Postgres backend, React/Vite frontend, deployed on Railway + Vercel, Paddle for payments (as Merchant of Record so I don't have to deal with global VAT/sales tax myself as a solo indie).
>
> Free to browse and set alerts. No ads, no affiliate links steering people to one operator over another.
>
> Would love feedback on the product itself, and happy to answer anything about the build/stack for anyone tackling something similar.

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

> Anyone else find permit lottery deadlines a pain to keep track of? Different park, different portal, and the actual closing date is usually buried in a government PDF nobody reads until it's too late.
>
> Built [SlotScout](http://myslotscout.com) to track this stuff - 141 permits/trips with hard windows (national parks, treks, a few lotteries), with a free email alert before each one opens. Free to browse and set alerts.
>
> Figured this group would know exactly the pain I'm talking about. Happy to add a destination if it's missing, and would genuinely love feedback.

**Draft #2 - general travel-planning groups:**

> Sharing something I built - permit and lottery systems for popular trips are scattered across government sites and forum threads, and it's easy to miss the actual application window.
>
> Built [SlotScout](http://myslotscout.com) to put it all in one place - it tracks 141 permits/lotteries/quotas that sell out fast (national parks, treks, a few "opens for 10 minutes" events) and sends an alert before each window opens. Free to browse and set alerts.
>
> Would love to know if there's a permit system that's burned you that I should add.

## Still to prepare

- **Creator outreach list + pitch text** - deferred to a future session. This session hit its WebSearch budget (200/200) before finding real creators, and deliberately did not fabricate names/channels (matches the project's "never fabricate a link" rule used throughout the destination-researcher/reviewer pipeline). Next session: search for real YouTubers/bloggers covering Yosemite/Half Dome, PCT, Patagonia/Torres del Paine, national park permits generally, then draft the pitch text once real names are in hand.
