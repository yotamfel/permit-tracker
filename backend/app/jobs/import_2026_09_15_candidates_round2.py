"""
One-off stub creation for 10 more candidate destinations researched and
approved by the user on 2026-09-15 (second round, same day as the first
8-destination batch) - broad nature/adventure-tourism destinations with real
bureaucratic access requirements (permits, mandatory guides, daily quotas),
explicitly including unique landmark/government/historic sites (in the same
spirit as existing castle/palace entries like Neuschwanstein and Buckingham
Palace), but NOT races or plain museums per the user's explicit scope
clarification.

Classification here is a deliberately conservative starting guess for the
destination-researcher/reviewer pipeline (or direct manual fill, per this
session's established one-at-a-time approach) to re-verify and correct, same
as every prior stub-import script. Never published automatically.

Run via: python -m app.jobs.import_2026_09_15_candidates_round2 (from backend/, venv active)
"""
from app.db import SessionLocal
from app.models.destination import Destination
from app.models.destination_source import DestinationSource

CANDIDATES = [
    dict(
        name="Komodo National Park",
        country="Indonesia",
        category="wildlife_safari",
        mechanism_type="fixed_daily_quota",
        mechanism_config={"daily_quota": 1000, "booking_opens_days_before": 90},
        issuing_authority="government",
        competitiveness_level="medium",
        research_note="1,000 visitors/day cap park-wide (~400/day on peak trekking trails) starting April 1, 2026, mandatory online booking via the SiOra app plus a mandatory ranger guide. Source: komodoguide.org/travel-guide/fees-and-quota-2026/, komodoluxury.com/blog/komodo-national-park-entry-permit-2026/.",
    ),
    dict(
        name="Stromboli Volcano Summit",
        country="Italy",
        category="tourist_attraction",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="government",
        competitiveness_level="low",
        research_note="Above 290m altitude, a certified volcanological guide is legally required due to eruption hazard; authorized altitude/access limits change based on the Civil Protection Department's real-time volcanic alert level. Source: magmatrek.it, visitstromboli.com/travel-guides/stromboli-trekking/.",
    ),
    dict(
        name="Pacaya Volcano",
        country="Guatemala",
        category="tourist_attraction",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="government",
        competitiveness_level="low",
        research_note="Pacaya National Park legally requires a local guide for all visitors; access to lava-viewing areas restricted immediately during heightened seismic activity. Source: pacayavolcano.org/hours-and-fees/.",
    ),
    dict(
        name="Villarrica Volcano",
        country="Chile",
        category="tourist_attraction",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="government",
        competitiveness_level="low",
        research_note="Mandatory CONAF (Chile's National Forest Corporation) permit; non-professional climbers must summit with a certified mountain guide to obtain it. Source: multiple independent guide-company pages corroborating the CONAF requirement (e.g. volcanohiking.com/2026/03/14/villarrica/).",
    ),
    dict(
        name="Ijen Crater (Blue Fire)",
        country="Indonesia",
        category="tourist_attraction",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="government",
        competitiveness_level="medium",
        research_note="Strict daily quota (fills on weekends/holidays), mandatory online advance booking via the national AyoKeTamanNasional park-booking system, mandatory certified gas mask, and a health/medical certificate issued within 3 days of the hike. Likely actually fixed_daily_quota once the exact numeric cap is confirmed by research - left as guided_tour_only for now rather than guess a number. Source: backindo.com/ijen-crater-guide/.",
    ),
    dict(
        name="Snow Leopard Tracking - Hemis National Park",
        country="India",
        category="wildlife_safari",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="government",
        competitiveness_level="medium",
        research_note="Requires an electronic Inner Line Permit (protected border-zone area near Indo-China border) obtained through a registered Leh-based tour operator, plus a local guide. Source: wanderon.in/blogs/hemis-national-park-in-ladakh.",
    ),
    dict(
        name="Orangutan Trekking - Gunung Leuser National Park",
        country="Indonesia",
        category="wildlife_safari",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="government",
        competitiveness_level="low",
        research_note="Entrance permit plus a mandatory official park guide (independent/unguided entry not permitted) - the Bukit Lawang gateway area of Sumatra. Source: sumatra-ecotravel.com/about-us/where-we-are/guidelines-for-the-jungle/.",
    ),
    dict(
        name="White House Public Tour",
        country="USA",
        category="tourist_attraction",
        mechanism_type="rolling_window",
        mechanism_config={"days_before_travel_date": 21},
        issuing_authority="government",
        competitiveness_level="medium",
        research_note="US citizens must request through a Member of Congress's office (21-90 days ahead, first-come first-served, no guarantee); foreign nationals must request through their own country's embassy in Washington DC instead. Genuinely convoluted, two-track bureaucracy unlike almost anything else in the catalog. Source: whitehouse.gov/visit/, multiple congressional-office tour-request pages.",
    ),
    dict(
        name="Chernobyl Exclusion Zone",
        country="Ukraine",
        category="tourist_attraction",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="government",
        competitiveness_level="low",
        research_note="Independent access prohibited - requires an official state permit obtained through a licensed tour operator, 18+ minimum age, passport required, book 14+ days ahead. Flagged explicitly: access status is tied to the ongoing war in Ukraine and can change on short notice - verify current status carefully before building/publishing, not just at research time. Source: ukrainetravelguard.com, realchernobyl.com/en/rules.",
    ),
    dict(
        name="Vatican Necropolis (Scavi Tour)",
        country="Vatican City",
        category="tourist_attraction",
        mechanism_type="fixed_daily_quota",
        mechanism_config={"daily_quota": 250, "booking_opens_days_before": 180},
        issuing_authority="government",
        competitiveness_level="high",
        research_note="Only 250 visitors/day, groups capped at ~12, booking ONLY by email (scavi@fsp.va) 3-6 months ahead - no online ticketing system exists at all, unusual even among the site's existing guided-tour-only destinations. Age 15+. Source: multiple independent guide pages corroborating the email-only booking process (e.g. thecatholictraveler.com/guides/rome/scavi-tour/tickets/).",
    ),
]

db = SessionLocal()
created = 0
for c in CANDIDATES:
    existing = db.query(Destination).filter(Destination.name == c["name"]).first()
    if existing:
        print("SKIP (already exists):", c["name"])
        continue
    d = Destination(
        country=c["country"],
        category=c["category"],
        name=c["name"],
        mechanism_type=c["mechanism_type"],
        mechanism_config=c["mechanism_config"],
        issuing_authority=c["issuing_authority"],
        competitiveness_level=c["competitiveness_level"],
        source_url=None,
        is_published=False,
        price_usd=6.99,
    )
    db.add(d)
    db.flush()
    db.add(DestinationSource(destination_id=d.id, order_index=0, note=c["research_note"]))
    created += 1
    print("Created:", c["name"], d.id)

db.commit()
db.close()
print("Total created:", created)
