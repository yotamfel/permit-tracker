"""
Imports the remaining ~73 researched-but-not-MVP destinations from
docs/permits_worldwide_database.xlsx as unpublished stub rows (is_published=False),
per PROJECT_SPEC.md §10: "the rest can be added as unpublished stub rows later."

These stubs are intentionally lower-fidelity than the 29 hand-authored MVP
destinations in seed_data.py:
- mechanism_type / issuing_authority / competitiveness_level are inferred from the
  Hebrew free-text research notes with simple keyword heuristics, not hand-verified.
- mechanism_config is a structurally-valid placeholder for the inferred type, not
  researched exact numbers.
- source_url is left NULL rather than guessed (never fabricate a source URL).
- The original Hebrew research note is preserved verbatim as a `destination.description`
  translation row (locale=he) so no research is lost - an admin reviewing the stub in
  the admin panel has the real context to fill in accurate data before publishing.

Never published automatically. Run via: python -m app.jobs.stub_import
"""
import re

import openpyxl

from app.db import SessionLocal
from app.models.destination import Destination
from app.models.translation import Translation
from app.jobs.seed_data import DESTINATIONS as MVP_DESTINATIONS

XLSX_PATH = "../docs/permits_worldwide_database.xlsx"
SHEET_NAME = "היתרים ומכסות"

COUNTRY_HE_TO_EN = {
    "אוגנדה": "Uganda", "אוסטרליה": "Australia", "איטליה": "Italy",
    "איילנד אירי": "Ireland", "אינדונזיה": "Indonesia", "איסלנד": "Iceland",
    'ארה"ב': "USA", "אתיופיה": "Ethiopia", "ברזיל": "Brazil",
    "בריטניה": "United Kingdom", "גרמניה": "Germany", "דרום אפריקה": "South Africa",
    "הודו": "India", "הולנד": "Netherlands", "הרפובליקה הדומיניקנית": "Dominican Republic",
    "וייטנאם": "Vietnam", "טיבט/סין": "Tibet/China", "טנזניה": "Tanzania",
    "טנזניה/קניה": "Tanzania/Kenya", "יפן": "Japan", "ירדן": "Jordan",
    "מלזיה": "Malaysia", "מקסיקו": "Mexico", "ניו זילנד": "New Zealand",
    "נפאל": "Nepal", "סין": "China", "ספרד": "Spain", "ספרד/צרפת": "Spain/France",
    "סקוטלנד": "Scotland", "פלאו": "Palau", "פקיסטן": "Pakistan", "פרו": "Peru",
    "צ'ילה": "Chile", "צרפת": "France", "צרפת/איטליה/שוויץ": "France/Italy/Switzerland",
    "קוסטה ריקה": "Costa Rica", "קנדה": "Canada", "קניה": "Kenya", "רואנדה": "Rwanda",
}

CATEGORY_KEYWORDS = [
    ("צלילה", "diving"),
    ("ספארי", "wildlife_safari"),
    ("עדינה", "wildlife_safari"),  # צפייה בעדינה = wildlife viewing
    ("טרק", "trek"),
    ("מסלול מרחק ארוך", "thru_hike"),
    ("Thru-hike", "thru_hike"),
    ("קמפינג", "camping"),
    ("פארק לאומי", "national_park_entry"),
    ("אי/שמורה", "national_park_entry"),
    ("אירוע טבע עונתי", "seasonal_nature_event"),
    ("אתר תיירותי", "tourist_attraction"),
    ("טיפוס", "trek"),
    ("כניסה בזמן קבוע", "tourist_attraction"),
    ("כניסה", "national_park_entry"),
]

MECHANISM_KEYWORDS = [
    ("הגרלה", "lottery"),
    ("חלון נגלל", "rolling_window"),
    ("rolling", "rolling_window"),
    ("שבועי", "weekly_release"),
    ("תאריך פתיחה שנתי קבוע", "fixed_annual_date"),
    ("מכסה יומית", "fixed_daily_quota"),
    ("מכסת מבקרים יומית", "fixed_daily_quota"),
    ("מכסת אזור", "fixed_daily_quota"),
    ("ספק בלעדי", "single_operator_annual_quota"),
    ("מכסה שנתית קבועה", "single_operator_annual_quota"),
    ("permit + ליווי חובה", "guided_tour_only"),
    ("permit מיוחד + ליווי", "guided_tour_only"),
    ("אישור קבוצתי, לא ניתן לתייר עצמאי", "guided_tour_only"),
]

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

COMPETITIVENESS_KEYWORDS = [
    ("גבוהה מאוד", "very_high"),
    ("גבוהה", "high"),
    ("נמוכה-בינונית", "low"),
    ("בינונית-גבוהה", "high"),
    ("בינונית", "medium"),
    ("נמוכה", "low"),
]

ISSUER_KEYWORDS = [
    ("שבטי", "tribal"),
    ("מסחרי", "commercial"),
    ("מעורב", "mixed"),
    ("ממשלתי", "government"),
]


def classify(text: str | None, keywords: list[tuple[str, str]], default: str) -> str:
    if not text:
        return default
    for needle, value in keywords:
        if needle in text:
            return value
    return default


def already_in_mvp(name: str) -> bool:
    normalized = re.sub(r"[^a-zA-Z]", "", name).lower()
    for mvp in MVP_DESTINATIONS:
        mvp_normalized = re.sub(r"[^a-zA-Z]", "", mvp["name"]).lower()
        if normalized and (normalized in mvp_normalized or mvp_normalized in normalized):
            return True
    return False


def run() -> None:
    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb[SHEET_NAME]
    rows = list(ws.iter_rows(values_only=True))[1:]

    db = SessionLocal()
    created = 0
    skipped_dupe = 0
    try:
        for country_he, category_he, name, mechanism_he, notes, competitiveness_he, source_notes, issuer_he in rows:
            if not name:
                continue
            if already_in_mvp(str(name)):
                skipped_dupe += 1
                continue

            country_en = COUNTRY_HE_TO_EN.get(country_he, country_he or "Unknown")
            category = classify(category_he, CATEGORY_KEYWORDS, "tourist_attraction")
            mechanism_type = classify(mechanism_he, MECHANISM_KEYWORDS, "first_come_first_served")
            competitiveness = classify(competitiveness_he, COMPETITIVENESS_KEYWORDS, "medium")
            issuer = classify(issuer_he, ISSUER_KEYWORDS, "government")

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

            research_note = " | ".join(str(x) for x in (mechanism_he, notes, source_notes) if x)
            if research_note:
                db.add(
                    Translation(
                        entity_type="destination.description",
                        entity_id=d.id,
                        locale="he",
                        value=research_note,
                    )
                )
            created += 1

        db.commit()
    finally:
        db.close()

    print(f"Created {created} stub destinations, skipped {skipped_dupe} duplicates of MVP destinations.")


if __name__ == "__main__":
    run()
