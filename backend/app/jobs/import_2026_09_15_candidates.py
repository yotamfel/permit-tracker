"""
One-off stub creation for the 8 candidate destinations researched and
approved by the user on 2026-09-15 (see project memory) to fill real gaps
in the catalog: thin camping/diving/seasonal_nature_event categories, zero
coverage of Ecuador/Colombia/Antarctica/Norway/Bhutan, and only 1 existing
example each of single_operator_annual_quota/weekly_release mechanisms.

Classification here is a deliberately conservative starting guess for the
destination-researcher/reviewer pipeline to re-verify and correct, same as
every prior stub-import script. Never published automatically.

Run via: python -m app.jobs.import_2026_09_15_candidates (from backend/, venv active)
"""
from app.db import SessionLocal
from app.models.destination import Destination
from app.models.destination_source import DestinationSource

CANDIDATES = [
    dict(
        name="Galapagos Islands National Park",
        country="Ecuador",
        category="national_park_entry",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="government",
        competitiveness_level="low",
        research_note="All tourism inside GNPS-protected visitor sites requires a licensed naturalist guide. Source: https://galapagosislands.travel/planning/galapagos-entry-requirements-permits/ (citing official GNPS policy).",
    ),
    dict(
        name="Ciudad Perdida (Lost City) Trek",
        country="Colombia",
        category="trek",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="mixed",
        competitiveness_level="medium",
        research_note="Cannot be reached independently - only via ~5-9 licensed tour operators (e.g. Turcol, Wiwa Tours). Source: https://www.indietraveller.co/lost-city-trek-colombia/, corroborated by multiple operator sites.",
    ),
    dict(
        name="Antarctica Peninsula Landings",
        country="Antarctica",
        category="wildlife_safari",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="mixed",
        competitiveness_level="medium",
        research_note="Only IAATO-member operators may land; annual Ship Scheduler caps ships-per-site/day and max 100 passengers ashore at once. Source: https://iaato.org/faqs, https://iaato.org/system/files?file=2025-01%2FATCM28_ip090_e.pdf. Already cited by name in our own guides.js 'Operator Quotas Explained' article.",
    ),
    dict(
        name="Tubbataha Reefs Natural Park",
        country="Philippines",
        category="diving",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="government",
        competitiveness_level="high",
        research_note="Only 9 licensed liveaboards hold a permit, ~1,200 divers/year total, short season (Mar-Jun). Source: https://tubbatahareefs.org/permits-and-fees.",
    ),
    dict(
        name="Ostional Wildlife Refuge Turtle Arribada",
        country="Costa Rica",
        category="seasonal_nature_event",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="government",
        competitiveness_level="medium",
        research_note="Law requires an accredited guide, max 9 tourists/guide, during mass turtle-nesting arribadas. Source: https://mytanfeet.com/costa-rica-national-park/ostional-wildlife-refuge-protecting-turtles/, https://ticotimes.net/2026/06/29/what-is-an-arribada-costa-ricas-mass-turtle-nesting-event-explained.",
    ),
    dict(
        name="Zion Narrows Bottom-Up Backpacking Permit",
        country="USA",
        category="camping",
        mechanism_type="recurring_lottery",
        mechanism_config={"recurrence": "monthly", "application_day_of_month": 1},
        issuing_authority="government",
        competitiveness_level="medium",
        research_note="NPS runs an Advance Lottery plus a daily Last-Minute Drawing, same pattern as existing Half Dome/The Wave entries. Confirmed NOT a duplicate of the existing Angels Landing destination (separate short-hike lottery permit) - verified against DB before creating this stub. Source: https://nps.gov/zion/planyourvisit/narrowspermits.htm.",
    ),
    dict(
        name="Svalbard Off-Settlement Travel",
        country="Norway",
        category="wildlife_safari",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="government",
        competitiveness_level="low",
        research_note="Norwegian field safety regulation requires an approved Svalbard guide for any travel outside settlements, due to polar bear risk. Source: https://www.regjeringen.no/en/whats-new/nye-guidekrav-pa-svalbard/id3108103.",
    ),
    dict(
        name="Bhutan Tourism (Sustainable Development Fee)",
        country="Bhutan",
        category="tourist_attraction",
        mechanism_type="guided_tour_only",
        mechanism_config={},
        issuing_authority="government",
        competitiveness_level="low",
        research_note="All international tourists (except Indian/Bangladeshi/Maldivian nationals, who may enter independently at land borders) must book through a Tourism Council of Bhutan-licensed operator before a visa is issued, plus a $100/night Sustainable Development Fee confirmed through August 2027. Verified 2026-09-15 that the licensed-operator requirement is still in force despite a 2025 policy change some sources claimed removed it.",
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
