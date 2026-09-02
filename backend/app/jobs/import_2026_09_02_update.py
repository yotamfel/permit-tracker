"""
One-off import of new destinations found in the 2026-09-02 update to
docs/permits_worldwide_database.xlsx (122 rows total). Cross-checked every
row's normalized name against the 116 destinations already in the DB
(handling accented characters, "NP" vs "National Park", parentheticals,
etc.) - the vast majority of the sheet already matches an existing row.
Only 6 rows are genuinely new:

- GR20 (Corsica), France - hut-based trek, distinct from Tour du Mont Blanc.
- Denali NP camping (Wonder Lake / Teklanika), USA - distinct from the
  existing "Denali - Climber Registration" (summit permit vs. campground).
- McNeil River State Game Sanctuary bear viewing, USA (Alaska) - lottery.
- Katmai NP Brooks Falls bear viewing, USA (Alaska) - camping + lodge lottery.
- Skomer Island puffins, United Kingdom (Wales) - annual release date.
- San Ignacio Lagoon gray whales, Mexico - licensed panga operators only.

"Munro Bagging" is skipped again (no permit/registration exists, per the
sheet's own note - same call as the 2026-08-31 import). Everything else in
the sheet (Corcovado Sirena, Kalalau Trail, PCT, Laugavegur Trail, etc.)
was a false-negative from the fuzzy name match (abbreviations, diacritics)
and is already correctly represented in the DB - verified by hand, not
re-imported.

Classification here is hand-picked, not keyword-guessed - these are
deliberately conservative starting guesses (mechanism_type especially) for
the research pipeline to re-verify, same as every prior stub.

Never published automatically. Run via: python -m app.jobs.import_2026_09_02_update
"""
import openpyxl

from app.db import SessionLocal
from app.models.destination import Destination
from app.models.destination_source import DestinationSource

XLSX_PATH = "../docs/permits_worldwide_database.xlsx"

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

# sheet row name (as it appears in column C) -> (english name, country, category,
# mechanism_type, issuing_authority, competitiveness_level)
CLASSIFICATION = {
    "GR20 (קורסיקה)": (
        "GR20 (Corsica)", "France", "trek", "rolling_window", "mixed", "high",
    ),
    "Denali NP - קמפינג (Wonder Lake / Teklanika)": (
        "Denali NP Camping (Wonder Lake / Teklanika)", "USA", "camping", "rolling_window", "government", "medium",
    ),
    "McNeil River State Game Sanctuary - צפייה בדובים": (
        "McNeil River State Game Sanctuary - Bear Viewing", "USA (Alaska)", "wildlife_safari", "lottery", "government", "very_high",
    ),
    "Katmai NP - Brooks Falls (צפייה בדובים)": (
        "Katmai NP - Brooks Falls Bear Viewing", "USA (Alaska)", "wildlife_safari", "rolling_window", "mixed", "high",
    ),
    "Skomer Island - צפייה בפפינים": (
        "Skomer Island - Puffin Viewing", "United Kingdom", "wildlife_safari", "fixed_annual_date", "mixed", "high",
    ),
    "San Ignacio Lagoon - לווייתני אפור": (
        "San Ignacio Lagoon - Gray Whale Viewing", "Mexico", "wildlife_safari", "guided_tour_only", "government", "medium",
    ),
}

SKIPPED = {"Munro Bagging - רשימת ה-Munros הסקוטיים"}


def run() -> None:
    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb.worksheets[0]
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

            english_name, country_en, category, mechanism_type, issuer, competitiveness = CLASSIFICATION[name]
            research_notes = " | ".join(
                str(x) for x in (country_he, category_he, mechanism_he, notes, source_notes, issuer_he) if x
            )

            d = Destination(
                country=country_en,
                category=category,
                name=english_name,
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
