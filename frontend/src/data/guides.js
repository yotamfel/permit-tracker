// Topic-level guides (not tied to one destination) - deliberately kept
// separate from destination pages to avoid duplicating the mechanism/prep
// info already on each destination's own page. Linked contextually from
// DestinationDetail.jsx based on mechanismTypes, and listed at /guides.
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
          "Many permit lotteries let you apply as a group under one lead applicant, and the whole group wins or loses together. This matters two ways: if you're joining someone else's application, your odds are whatever the group's odds are, not your own separate entry. And if you're the lead applicant, some systems weight larger groups differently (occasionally worse odds, since a big group takes more of a limited quota) - check the specific rules rather than assuming.",
        ],
      },
      {
        heading: "What actually improves your odds",
        paragraphs: [
          "Since the draw itself is random, the only real lever you control is what you apply for. Off-peak dates, less popular routes or entry points, and smaller party sizes are typically less contested than the obvious peak-season, headline options - applying for those can mean meaningfully better odds for a trip that's still very much worth taking.",
          "Listing multiple acceptable date ranges, where the system allows it, also helps - you're effectively entering several smaller draws instead of one big one for a single popular date.",
        ],
      },
      {
        heading: "If you don't get in",
        paragraphs: [
          "A single lost draw isn't necessarily the end of the plan. Some systems run a second-chance or waitlist draw for slots that unclaimed winners forfeit, and applying again next season is always an option since the draw has no memory of past losses working against you.",
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
          "Operators typically apply for or bid on a slice of the annual quota ahead of each season, and the split can change year to year as licenses are renewed, added, or revoked. That's part of why the specific list of legitimate operators for a destination is worth rechecking each season rather than assuming last year's list still holds.",
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
          "Once an authority allocates you a permit, it's typically counted against that season's total quota - meaning your spot may not simply pass to someone else if you cancel, especially close to the date. That's the main reason most permit fees, once paid, are treated as final rather than a normal refundable reservation.",
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
          "Some (not all) systems allow rebooking an unused permit to a future date or season, sometimes for a fee, and occasionally allow transferring a named permit to a different person. None of this is universal - it depends entirely on the specific authority's rules, so it's worth checking the exact terms before assuming either option is available to you.",
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
          "Most general travel insurance policies are written for ordinary trip risks - lost luggage, flight delays, routine medical care - and explicitly exclude \"hazardous activities\" or trekking above a stated altitude, commonly somewhere in the 3,500-4,500m range depending on the insurer. A policy that would cover you perfectly well for a city trip can be worthless for the exact activity a remote permit is for.",
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
];

export function getGuide(slug) {
  return GUIDES.find((g) => g.slug === slug);
}

export function guidesForMechanismType(mechanismType, limit = 2) {
  const specific = GUIDES.filter((g) => Array.isArray(g.mechanismTypes) && g.mechanismTypes.includes(mechanismType));
  const general = GUIDES.filter((g) => g.mechanismTypes === "all");
  return [...specific, ...general].slice(0, limit);
}
