// Topic-level guides (not tied to one destination) - deliberately kept
// separate from destination pages to avoid duplicating the mechanism/prep
// info already on each destination's own page. Linked contextually from
// DestinationDetail.jsx based on mechanismTypes, and listed at /guides.

// Bump whenever guide content is substantively edited - used for the
// Article JSON-LD dateModified. Keep in sync with GUIDES_LAST_MODIFIED in
// backend/app/main.py (used for the sitemap's <lastmod>).
export const GUIDES_LAST_UPDATED = "2026-09-22";

export const GUIDES = [
  {
    slug: "how-permit-lotteries-work",
    title: "How Permit Lotteries Actually Work",
    description:
      "How random-draw permit lotteries are actually run, what group applications mean for your odds, and what happens if you win.",
    mechanismTypes: ["lottery"],
    sections: [
      {
        heading: "Why lotteries exist at all",
        paragraphs: [
          "When far more people want a spot than there are spots available, a first-come-first-served rush just rewards whoever has the fastest internet connection and the most free time to sit refreshing a booking page. A lottery is the alternative: everyone who applies within a window has an equal shot, regardless of when exactly they hit submit.",
        ],
      },
      {
        heading: "How the draw usually works",
        paragraphs: [
          "You submit an application within a defined window - sometimes weeks long, sometimes just a few days. After the window closes, a random draw selects winners from the full applicant pool. Being first to apply on day one gives you no advantage over applying an hour before the deadline; the timing that actually matters is getting your application in before the window closes at all.",
          "Most systems notify everyone - winners and non-winners - by email within a few weeks of the draw, and give winners a short, firm deadline (often just days) to accept and pay before the spot passes to someone else.",
        ],
      },
      {
        heading: "Group applications",
        paragraphs: [
          "Many permit lotteries let you apply as a group under one lead applicant, and the whole group wins or loses together. If you're joining someone else's application, your odds are whatever the group's odds are, not a separate entry of your own. Whether group size itself affects your odds varies by system - some weight larger groups differently, but plenty of lotteries draw applications at random with no group-size adjustment at all. Don't assume either way; the specific rules for that lottery will say.",
        ],
      },
      {
        heading: "What actually improves your odds",
        paragraphs: [
          "Since the draw itself is random, the only real lever you control is what you apply for. Off-peak dates and less popular routes or entry points are typically far less contested than the obvious peak-season, headline options - sometimes dramatically so. A well-known example: the lottery for The Wave (Coyote Buttes North, USA) runs at roughly 2-3% odds in peak spring and fall months, but odds rise substantially in the off-season - the exact same permit, just a much better bet outside peak demand.",
          "Listing multiple acceptable date ranges, where the system allows it, also helps - you're effectively entering several smaller draws instead of one big one for a single popular date.",
        ],
      },
      {
        heading: "If you don't get in",
        paragraphs: [
          "A single lost draw isn't necessarily the end of the plan. Many systems run a separate, smaller \"second-chance\" or daily lottery for slots that unclaimed winners forfeit or that weren't allocated in the main draw - both Half Dome (Yosemite) and The Wave run exactly this kind of daily backup lottery alongside their main seasonal one. Applying again next season is always an option too, since the draw has no memory of past losses working against you.",
        ],
      },
      {
        heading: "In practice: how a real lottery runs",
        paragraphs: [
          "Yosemite's Half Dome permit lottery is a useful concrete example of the whole cycle: the preseason application window runs through March, results come out in mid-April, and winners get a short window of roughly two weeks to accept and pay before the permit is released. Applicants who don't win the preseason lottery - or who decide to go later - can also try the separate daily lottery, which opens a couple of days ahead of each hiking date for whatever capacity remains.",
        ],
      },
    ],
  },
  {
    slug: "operator-quotas-explained",
    title: "Operator Quotas Explained",
    description:
      "Why some permits are never sold directly to travelers, how the quota gets divided among tour operators, and what to check before booking one.",
    mechanismTypes: ["guided_tour_only", "single_operator_annual_quota"],
    sections: [
      {
        heading: "Why some permits aren't sold directly to you",
        paragraphs: [
          "For some destinations - typically ones that are remote, physically demanding, or ecologically sensitive - the issuing authority doesn't run a public booking system at all. Instead, it caps total annual visitor numbers and licenses a limited set of tour operators to manage bookings, guiding, and safety within that cap. The logic is usually a mix of safety oversight (a licensed guide is responsible for the group) and simpler enforcement (fewer parties to monitor than thousands of individual travelers).",
        ],
      },
      {
        heading: "How the quota gets divided",
        paragraphs: [
          "The details vary a lot by destination, but the general pattern is that licensed operators coordinate through a shared booking system or governing body rather than each just claiming spots independently - and that coordination is what actually enforces the cap. A well-documented real example is Antarctica: member operators of IAATO (the industry's own association, working within the Antarctic Treaty System) schedule every landing site visit for the entire season into one shared database, with per-site visitor caps enforced across all operators at once, precisely to prevent any single site from being overwhelmed regardless of how many different companies are running trips there.",
          "Licenses, allocations, and even which sites are open at all can also be revised between seasons as guidelines are updated - part of why the specific list of legitimate operators and what they're permitted to do is worth rechecking each season rather than assuming last year's list still holds.",
        ],
      },
      {
        heading: "What this means for booking",
        paragraphs: [
          "You're generally paying two separate things: the operator's own service fee (guiding, logistics, sometimes gear and permits handling) and the government permit/park fee itself, which the operator usually collects and passes through. Prices between operators can vary quite a bit even for what looks like the same trip - that difference is almost always about service level and group size, not about who has a \"better\" permit, since the permit terms are typically set by the authority, not the operator.",
          "Because a fixed number of operators are splitting a fixed quota, popular seasons book out through operators well before the season itself - sometimes 6-12 months ahead for the most sought-after windows.",
        ],
      },
      {
        heading: "Red flags to watch for",
        paragraphs: [
          "Only book through operators that are actually on the destination's official licensed list - resellers or unlicensed \"agents\" offering a shortcut are a common scam pattern for exactly this kind of restricted-access destination. It's also worth asking the operator directly about their own cancellation and refund policy, separate from the permit's own refund rules (see our guide on permit deposits) - the two aren't always the same.",
        ],
      },
    ],
  },
  {
    slug: "avoid-losing-your-permit-deposit",
    title: "How to Avoid Losing Your Permit Deposit",
    description:
      "Why permit fees are usually non-refundable, the most common ways people lose their deposit anyway, and practical steps to protect yourself.",
    mechanismTypes: "all",
    sections: [
      {
        heading: "Why permit deposits are usually non-refundable",
        paragraphs: [
          "Once an authority allocates you a permit, it's typically counted against that season's total quota - meaning your spot may not simply pass to someone else if you cancel, especially close to the date. That's the main reason most permit fees, once paid, are treated as final rather than a normal refundable reservation. This isn't a niche policy either: non-refundable permit or application fees, usually in the modest $6-$20 range for entry-level cases, are standard practice at Yosemite (Half Dome), Sequoia & Kings Canyon, Olympic, and Glacier National Parks, among many others.",
        ],
      },
      {
        heading: "Common ways people lose their deposit anyway",
        paragraphs: [
          "It's rarely simple cancellation that costs people their money - it's usually a missed secondary requirement tied to the permit: a required document (passport validity, visa, medical certificate) not submitted by its own separate deadline, insurance that doesn't meet the permit's specific coverage minimums, or simply not completing a linked registration step in time. Group permits add another failure mode: one member missing a requirement can occasionally affect the whole group's booking.",
        ],
      },
      {
        heading: "What you can usually do if plans change",
        paragraphs: [
          "Free date changes are the exception, not the rule. Most systems that do offer any flexibility work by cancelling your existing reservation and having you pay again for a new date, rather than transferring the original payment - that's the standard approach at parks like Glacier and Olympic. Some go further and rule it out explicitly: several U.S. Forest Service permit systems state outright that fees are non-transferable with no rain checks for weather, illness, or any other change of plans. None of this is universal, so always check the exact terms for the specific permit before assuming any flexibility exists.",
        ],
      },
      {
        heading: "Practical steps to protect yourself",
        paragraphs: [
          "Buy trip cancellation/interruption insurance as a separate product from the permit itself - it's the one thing that can actually get you money back if your own plans fall through, since the permit fee generally won't. Read the specific refund and rebooking terms before paying, not after. And treat every secondary deadline tied to the permit (insurance proof, document uploads, final payment) as seriously as the permit deadline itself - calendar reminders for each one are worth the two minutes they take to set.",
        ],
      },
    ],
  },
  {
    slug: "lottery-vs-fcfs-vs-fixed-date",
    title: "Lottery vs. First-Come-First-Served vs. Fixed-Date Release",
    description:
      "How to tell which permit system you're dealing with, and why the winning strategy is completely different for each one.",
    mechanismTypes: ["lottery", "first_come_first_served", "fixed_annual_date", "weekly_release", "fixed_daily_quota"],
    sections: [
      {
        heading: "Three different games, three different strategies",
        paragraphs: [
          "The single biggest mistake people make with permits is applying the wrong strategy to the wrong system - showing up early for a lottery (which does nothing) or casually checking back later for a fixed-date release (which can mean missing it entirely). Knowing which of these three systems you're dealing with changes what you should actually do.",
        ],
      },
      {
        heading: "Fixed-date release: speed matters",
        paragraphs: [
          "A specific, publicly announced date and time when booking opens, after which spots go to whoever books first - sometimes within minutes for the most popular destinations. This is the one system where being online early, having your account and payment details ready in advance, and setting an actual alarm (not just \"I'll remember\") genuinely matters.",
        ],
      },
      {
        heading: "First-come-first-served (rolling): plan your window early",
        paragraphs: [
          "No single release date - booking simply opens some fixed number of days or months ahead of your travel date, on a rolling basis. There's no single moment of high competition to prepare for, but there is a specific day your own personal booking window opens, and popular dates within that window can still fill up over the following days or weeks. The move here is knowing exactly when your window opens and booking promptly once it does, not waiting.",
        ],
      },
      {
        heading: "Lottery: luck and date choice matter more than speed",
        paragraphs: [
          "A random draw among everyone who applies within an open window - see our full guide on how permit lotteries work for more detail. Applying an hour before the deadline is exactly as good as applying the moment the window opens. What actually matters is which dates and options you request, since less popular choices are typically less contested.",
        ],
      },
      {
        heading: "How to tell which one you're dealing with",
        paragraphs: [
          "The issuing authority's own official page for the permit will state this directly, usually under a heading like \"how to apply\" or \"reservation system.\" Each destination page on SlotScout also tags the mechanism type directly, precisely so you don't have to dig through an official site to figure out which strategy applies.",
        ],
      },
      {
        heading: "In practice: the same park can run all three at once",
        paragraphs: [
          "Yosemite's wilderness permit system is a good real-world illustration of why this distinction matters: roughly 60% of permits for a given trailhead are released months ahead through a lottery, while the remaining permits are held back and released on a rolling first-come-first-served basis a set number of days before each date. Two people hiking the exact same trail on the exact same day can be going through completely different processes - one who planned early and won a lottery slot, one who booked on a rolling window a few days out - and each needed a different strategy to get there.",
        ],
      },
    ],
  },
  {
    slug: "travel-insurance-for-remote-permits",
    title: "Travel Insurance for High-Altitude & Remote Permits",
    description:
      "Why standard travel insurance often doesn't cover high-altitude trekking or remote evacuation, and exactly what to check before you rely on a policy.",
    mechanismTypes: "all",
    sections: [
      {
        heading: "Why standard travel insurance often isn't enough",
        paragraphs: [
          "Most general travel insurance policies are written for ordinary trip risks - lost luggage, flight delays, routine medical care - and explicitly exclude \"hazardous activities\" or trekking above a stated altitude. Standard and mid-tier policies commonly cut off somewhere in the 3,000-5,000m range depending on the insurer, which already excludes plenty of popular trekking routes - dedicated high-altitude or mountaineering tiers exist specifically to extend that ceiling, sometimes as high as 6,000-8,000m, but usually cost more and have to be selected deliberately rather than assumed. A policy that covers you perfectly well for a city trip can be worthless for the exact activity a remote permit is for.",
        ],
      },
      {
        heading: "What to specifically check for",
        paragraphs: [
          "Confirm the policy's altitude ceiling actually covers your highest planned point, not just your general destination - a policy covering trekking to 4,000m doesn't help on a route with a 5,500m pass. Separately confirm emergency evacuation and search-and-rescue coverage, ideally including helicopter evacuation where relevant, since this is often excluded or capped even on policies that do cover the altitude itself. Check the medical coverage limit is realistic for the region (evacuation and treatment costs in remote areas can run far higher than a standard travel-medical limit assumes), and whether trip cancellation/interruption is included as a separate line item.",
        ],
      },
      {
        heading: "Permit-specific requirements",
        paragraphs: [
          "Some permits legally require proof of insurance meeting specific minimums - a coverage amount, a named type of evacuation coverage, or both - before you can even complete registration. This requirement, when it applies, is usually listed directly in that destination's prep checklist rather than buried in general guidance, so check there first.",
        ],
      },
      {
        heading: "How to actually verify a policy covers you",
        paragraphs: [
          "Marketing copy on an insurer's website is not the same as a confirmed answer. Before relying on a policy, contact the insurer directly (email is best, since it leaves a written record) and describe your specific activity and maximum altitude, and ask them to confirm in writing that it's covered - not just that the policy \"includes adventure sports\" as a general category.",
        ],
      },
    ],
  },
  {
    slug: "141-permits-by-the-numbers",
    title: "141 Permits, By the Numbers",
    description:
      "We pulled real statistics from our own catalog of 141 tracked destinations to see what 'hard to get' actually looks like in aggregate - which mechanisms dominate, who really runs these systems, and which single numbers are the most extreme in the whole catalog.",
    mechanismTypes: "all",
    sections: [
      {
        heading: "The most common mechanism isn't a lottery",
        paragraphs: [
          "Across the 141 destinations we currently track, the single most common access mechanism is plain first-come-first-served booking (28% of the catalog), narrowly ahead of guided-tour-only access (27%) - destinations where there's no individual permit to apply for at all, only a licensed operator who handles it. True lotteries, the mechanism most people probably picture first when they think \"hard to get permit,\" account for just 8.5% of the catalog on their own, or 11.3% including the smaller recurring-lottery category (a lottery that runs on a repeating weekly or monthly cycle instead of once a year). Fixed-annual-date releases (a single announced date and time when booking opens, first-come after that) make up 12.8%, and rolling-window bookings (opening a fixed number of days ahead of your travel date, on a rolling basis) another 11.3%.",
          "The practical takeaway: for most destinations in this catalog, the actual obstacle isn't luck, it's process - knowing exactly when a window opens, or which of a small set of licensed operators to book through - rather than winning a random draw.",
        ],
      },
      {
        heading: "Treks dominate the catalog, but not everything is a hiking trail",
        paragraphs: [
          "Multi-day treks make up 39% of the catalog (55 of 141 destinations) - by far the largest single category - followed by tourist attractions like palaces, castles, and iconic buildings at 22% (31 destinations). The remaining 39% spans wildlife safaris (16), national park entries (8), camping (7), thru-hikes (7), endurance events (6), diving (6), and seasonal nature events like mass turtle nestings or wildlife migrations (5). The catalog has deliberately grown beyond \"outdoor permits\" into any destination where getting in requires navigating a genuine access mechanism - a government building tour with a multi-week request process is, bureaucratically, not that different from a trekking permit.",
        ],
      },
      {
        heading: "Government still runs three-quarters of these systems",
        paragraphs: [
          "74% of tracked destinations (105 of 141) are issued directly by a government body - a national park service, a ministry, a park authority. Another 14% (20 destinations) are what we classify as \"mixed\" authority - typically a government agency operating jointly with an indigenous community or a treaty organization, as with Ciudad Perdida in Colombia (Colombian park authority plus the Kogi and Wiwa communities whose territory the trek crosses) or Antarctica (the international Antarctic Treaty System, self-regulated in practice by IAATO, the operators' own association). Purely commercial issuers - a private company or attraction operator, with no government permit layer at all - make up just 9% (13 destinations), and tribal-only authorities (indigenous governance with no government co-issuer) are the rarest at 2% (3 destinations).",
        ],
      },
      {
        heading: "Nepal is where the mechanism itself changes",
        paragraphs: [
          "Break the catalog down by country and one pattern jumps out immediately: of the 12 Nepal treks we track, 9 are guided-tour-only - Manaslu Circuit, Nar Phu Valley, Tsum Valley, Upper Dolpo, Upper Mustang, Kanchenjunga Base Camp, Langtang Valley, Makalu Base Camp, and the Annapurna Circuit - the highest concentration of that mechanism for any country in the catalog with a meaningful number of destinations. That's not a quirk of how we list them; Nepal's government legally requires a licensed local agency for foreigners entering most of these restricted areas, so there's no individual application to walk through the way there is for, say, a US national park permit - the actual process is choosing and booking with an agency, not filling out a government form yourself. Only three Nepal destinations we track can still be arranged independently: Everest Base Camp, the Everest summit climbing permit itself, and Rara Lake.",
        ],
      },
      {
        heading: "The most exclusive number in the catalog",
        paragraphs: [
          "Among destinations with a fixed daily numeric quota, the smallest are Fernando de Noronha (Brazil) and Mountain Gorilla Trekking in Rwanda's Volcanoes National Park, tied at 96 people admitted per day - a genuinely tiny number for what are both major, world-famous destinations. For comparison, Komodo National Park's new 2026 quota system (1,000 visitors/day across the whole park) looks positively generous by contrast, even though it's still a hard cap.",
        ],
      },
      {
        heading: "Some places want a full year's notice",
        paragraphs: [
          "Rwanda's gorilla trekking permits can be booked up to 365 days ahead of a travel date - the longest advance-booking window in the entire catalog. A cluster of other destinations (the Vatican Necropolis, the Statue of Liberty's Crown, Sipadan, Bwindi's gorilla trekking, the High Sierra Trail, and both Corcovado and Chirripó in Costa Rica) all sit at a 180-day (roughly 6-month) window. If a destination on your list allows booking this far out, the practical lesson is straightforward: the booking window opening is often the real event to plan around, well before the trip itself.",
        ],
      },
      {
        heading: "The most paperwork-heavy destination we track",
        paragraphs: [
          "Across the whole catalog, the average destination's prep checklist runs 10.2 items (1,442 checklist items across 141 destinations). The single most demanding is the Green and Yampa Rivers in Dinosaur National Monument (USA) at 24 checklist items - a multi-day, self-guided river-permit system with an unusually long list of gear, registration, and safety requirements even by the standards of self-guided wilderness permits. Next come Three Capes Track (20 items) and Overland Track (19) in Tasmania, then La Marmotte, the French Alpine cycling sportive (18), and a three-way tie at 17 between Berg Lake Trail in British Columbia, GR20 in Corsica, and the self-guided Grand Canyon Colorado River permit. Four of those five are multi-day treks or self-guided expeditions with their own hut, campsite, or permit-stacking layered on top of the base checklist - the outlier is La Marmotte, whose length comes from race logistics (medical certificate, timing chip, bike specifications) rather than wilderness permitting.",
        ],
      },
      {
        heading: "When there's no single official way to book",
        paragraphs: [
          "28 of the 141 destinations - about 1 in 5 - have no single official booking link at all, because multiple legitimate, independent operators are licensed to run the same permitted access (Ciudad Perdida's licensed trek operators, or the several IAATO-member ships running Antarctic Peninsula landings, are typical examples). For these, we list several verified operators directly rather than picking one to link to - the actual access mechanism is \"book with any licensed operator,\" not \"go to this one website,\" and pretending otherwise would misrepresent how the system actually works.",
        ],
      },
      {
        heading: "26 destinations we rate 'very high' competitiveness",
        paragraphs: [
          "18% of the catalog (26 destinations) carries our most competitive rating, meaning demand consistently and significantly outstrips supply - not just \"book ahead,\" but a real chance of missing out even with reasonable planning. The list spans very different mechanisms: lotteries with famously long odds (the Inca Trail, Havasupai Falls), fixed-date releases that sell out in minutes (L'Étape du Tour), and guided-access destinations where the operators themselves are booked solid a year out (Sipadan, Milford Track). The common thread isn't the mechanism - it's that no amount of understanding the system removes the underlying scarcity.",
        ],
      },
    ],
  },
];

export function getGuide(slug) {
  return GUIDES.find((g) => g.slug === slug);
}

export function guidesForMechanismType(mechanismType, limit = 2) {
  const specific = GUIDES.filter((g) => Array.isArray(g.mechanismTypes) && g.mechanismTypes.includes(mechanismType));
  const general = GUIDES.filter((g) => g.mechanismTypes === "all");
  return [...specific, ...general].slice(0, limit);
}
