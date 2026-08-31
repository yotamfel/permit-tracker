"""
One-off import of the 14 new destinations added in the 2026-08-31 update to
docs/permits_worldwide_database.xlsx (15 new rows minus "Munro Bagging",
which the spreadsheet's own research note flags as not fitting the model -
no permit/registration exists at all - so it's skipped).

Unlike stub_import.py, classification here is hand-picked per row (not
keyword-guessed) since there are only 14 rows and several needed a new
category ("endurance_event", for mass-participation registration events
like closed-road cycling sportives and multi-day walking marches - added to
Category enum alongside this import). The raw Hebrew research text is
stored in the new `research_notes` column (admin-only, not a fake
source_url) rather than a placeholder "he" description translation.

Never published automatically. Run via: python -m app.jobs.import_2026_08_31_update
"""
import openpyxl

from app.db import SessionLocal
from app.models.destination import Destination
from app.models.destination_source import DestinationSource

XLSX_PATH = "../docs/permits_worldwide_database.xlsx"
SHEET_NAME = "היתרים ומכסות"

MECHANISM_DEFAULT_CONFIG = {
    "fixed_daily_quota": {"daily_quota": 0, "booking_opens_days_before": 90},
    "lottery": {"application_window_start": "01-15", "application_window_end": "02-15", "results_date": "03-01"},
    "rolling_window": {"days_before_travel_date": 90},
    "fixed_annual_date": {"typical_release_date": "01-15", "release_time": "09:00", "timezone": "UTC"},
    "weekly_release": {"release_weekday": "tuesday", "release_time": "10:00", "timezone": "UTC", "weeks_ahead": 4},
    "guided_tour_only": {},
    "single_operator_annual_quota": {"operator_name": "TBD", "annual_quota": 0, "typical_booking_lead_time_months": 6},
    "first_come_first_served": {"typical_booking_lead_time_months": 6},
}

# name -> (country_en, category, mechanism_type, issuing_authority, competitiveness_level)
CLASSIFICATION = {
    "Aconcagua": ("Argentina", "trek", "fixed_daily_quota", "government", "medium"),
    "Conundrum Hot Springs (קולורדו)": ("USA", "camping", "rolling_window", "government", "high"),
    "Dragon's Back Race (וויילס)": ("United Kingdom", "endurance_event", "first_come_first_served", "commercial", "medium"),
    "Etape Loch Ness": ("United Kingdom", "endurance_event", "first_come_first_served", "commercial", "medium"),
    "Grand Canyon - Corridor Backcountry Permit (Phantom Ranch)": ("USA", "camping", "lottery", "government", "high"),
    "Kalalau Trail / Nāpali Coast (קאווואי, הוואי)": ("USA", "camping", "rolling_window", "government", "very_high"),
    "L'Étape du Tour": ("France", "endurance_event", "lottery", "commercial", "high"),
    "La Marmotte": ("France", "endurance_event", "first_come_first_served", "commercial", "high"),
    "Lake O'Hara (יוהו נפ״ל, קנדה)": ("Canada", "trek", "lottery", "government", "very_high"),
    "Nijmegen Four Days Marches (Vierdaagse)": ("Netherlands", "endurance_event", "lottery", "commercial", "high"),
    "TGO Challenge - חצייה רגלית של סקוטלנד מים לים": ("United Kingdom", "endurance_event", "first_come_first_served", "commercial", "high"),
    "The Enchantments (וושינגטון)": ("USA", "trek", "lottery", "government", "very_high"),
    "The Subway (זיון נפ״ל)": ("USA", "trek", "lottery", "government", "high"),
    "טרק שימפנזים (Kibale/Mahale)": ("Uganda/Tanzania", "wildlife_safari", "fixed_daily_quota", "government", "medium"),
}

SKIPPED = {"Munro Bagging - רשימת ה-Munros הסקוטיים"}


def run() -> None:
    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb[SHEET_NAME]
    rows = list(ws.iter_rows(values_only=True))[1:]

    db = SessionLocal()
    created = 0
    skipped = 0
    try:
        for country_he, category_he, name, mechanism_he, notes, competitiveness_he, source_notes, issuer_he in rows:
            if not name or name not in CLASSIFICATION:
                if name in SKIPPED:
                    skipped += 1
                continue

            country_en, category, mechanism_type, issuer, competitiveness = CLASSIFICATION[name]
            research_notes = " | ".join(
                str(x) for x in (country_he, category_he, mechanism_he, notes, source_notes, issuer_he) if x
            )

            d = Destination(
                country=country_en,
                category=category,
                name=str(name),
                mechanism_type=mechanism_type,
                mechanism_config=MECHANISM_DEFAULT_CONFIG[mechanism_type],
                issuing_authority=issuer,
                competitiveness_level=competitiveness,
                source_url=None,
                is_published=False,
                price_usd=4.99,
            )
            db.add(d)
            db.flush()
            db.add(DestinationSource(destination_id=d.id, order_index=0, note=research_notes))
            created += 1

        db.commit()
    finally:
        db.close()

    print(f"Created {created} destinations, skipped {skipped} (not a fit for the model).")
    missing = set(CLASSIFICATION) - {str(r[2]) for r in rows if r[2]}
    if missing:
        print(f"WARNING - not found in spreadsheet: {missing}")


if __name__ == "__main__":
    run()
