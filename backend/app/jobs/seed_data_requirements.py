"""
General requirements content (spec addendum §2.5) plus the destination attachments
that make up "Documents & Bureaucracy" section of each MVP destination's prep list.

English + Hebrew text is hand-authored here (Hebrew already required at MVP by the
original spec's §6). German/French/Spanish/Portuguese(BR) translations for these same
keys are added separately as machine-translated drafts (spec addendum §3) - see
app/jobs/seed_data_translations_i18n.py.
"""

GENERAL_REQUIREMENTS = [
    dict(
        key="passport_validity",
        requirement_type="passport_validity",
        is_general_default=True,
        title_en="Passport valid 6+ months",
        description_en="Your passport must remain valid for at least 6 months beyond your travel dates - many countries deny entry otherwise.",
        title_he="דרכון בתוקף ל-6 חודשים לפחות",
        description_he="הדרכון שלכם חייב להיות בתוקף לפחות 6 חודשים מעבר לתאריכי הנסיעה - מדינות רבות מסרבות לכניסה אחרת.",
    ),
    dict(
        key="travel_insurance_general",
        requirement_type="travel_insurance",
        is_general_default=True,
        title_en="Travel insurance",
        description_en="General travel insurance covering trip cancellation, medical emergencies, and evacuation.",
        title_he="ביטוח נסיעות",
        description_he="ביטוח נסיעות כללי המכסה ביטול נסיעה, מקרי חירום רפואיים ופינוי.",
    ),
    dict(
        key="travel_insurance_altitude",
        requirement_type="travel_insurance",
        is_general_default=False,
        title_en="High-altitude travel insurance",
        description_en="Standard travel insurance often excludes high-altitude trekking - confirm your policy explicitly covers activity above the relevant altitude threshold (usually 3,500-4,500m).",
        title_he="ביטוח נסיעות לרום גבוה",
        description_he="ביטוח נסיעות רגיל לרוב אינו מכסה טרקים ברום גבוה - ודאו שהפוליסה שלכם מכסה במפורש פעילות מעל סף הגובה הרלוונטי (בדרך כלל 3,500-4,500 מ').",
    ),
    dict(
        key="travel_insurance_diving",
        requirement_type="travel_insurance",
        is_general_default=False,
        title_en="Diving-specific travel insurance",
        description_en="Standard travel insurance often excludes scuba diving - a DAN (Divers Alert Network) policy or equivalent dive-specific coverage is strongly recommended.",
        title_he="ביטוח נסיעות ייעודי לצלילה",
        description_he="ביטוח נסיעות רגיל לרוב אינו מכסה צלילה - מומלץ מאוד פוליסת DAN (Divers Alert Network) או ביטוח ייעודי לצלילה.",
    ),
    dict(
        key="vaccination_yellow_fever",
        requirement_type="vaccination",
        is_general_default=False,
        title_en="Yellow fever vaccination certificate",
        description_en="An International Certificate of Vaccination (yellow fever) may be required for entry or is strongly recommended for this region.",
        title_he="תעודת חיסון קדחת צהובה",
        description_he="ייתכן שתידרש תעודת חיסון בינלאומית (קדחת צהובה) לכניסה, או שהיא מומלצת מאוד לאזור זה.",
    ),
    dict(
        key="fitness_certificate",
        requirement_type="fitness_certificate",
        is_general_default=False,
        title_en="Physical fitness / medical clearance",
        description_en="This activity is physically demanding - a recent medical checkup confirming fitness for strenuous exertion is strongly recommended.",
        title_he="אישור כושר גופני / רפואי",
        description_he="פעילות זו דורשת מאמץ גופני משמעותי - מומלץ מאוד בדיקה רפואית עדכנית המאשרת כושר למאמץ מתמשך.",
    ),
    dict(
        key="guide_booking_confirmation",
        requirement_type="other",
        is_general_default=False,
        title_en="Valid guide/agency booking confirmation",
        description_en="Independent access isn't permitted for this destination - keep your licensed guide or agency's booking confirmation with you.",
        title_he="אישור הזמנה בתוקף ממדריך/סוכנות",
        description_he="גישה עצמאית אינה מותרת ליעד זה - החזיקו עמכם את אישור ההזמנה מהמדריך המורשה או מהסוכנות.",
    ),
]

# (destination_name from seed_data.py, requirement_key, optional destination-specific note_en/note_he)
DESTINATION_REQUIREMENT_LINKS = [
    ("Mountain Gorilla Trekking – Volcanoes NP", "vaccination_yellow_fever",
     "Required for entry to Rwanda from a yellow-fever-endemic country - carry the certificate with your passport.",
     "נדרש לכניסה לרואנדה מארץ אנדמית לקדחת צהובה - החזיקו את התעודה יחד עם הדרכון."),
    ("Mountain Gorilla Trekking – Volcanoes NP", "fitness_certificate", None, None),
    ("Mountain Gorilla Trekking – Volcanoes NP", "guide_booking_confirmation", None, None),
    ("Inca Trail", "travel_insurance_altitude", "Dead Woman's Pass sits at 4,215m - confirm your policy covers this altitude.",
     "מעבר Dead Woman's Pass נמצא בגובה 4,215 מ' - ודאו שהפוליסה שלכם מכסה גובה זה."),
    ("Inca Trail", "fitness_certificate", None, None),
    ("Mount Whitney", "travel_insurance_altitude", "The summit sits at 4,421m - confirm your policy covers this altitude.",
     "הפסגה נמצאת בגובה 4,421 מ' - ודאו שהפוליסה שלכם מכסה גובה זה."),
    ("Mount Whitney", "fitness_certificate", None, None),
    ("John Muir Trail", "travel_insurance_altitude", None, None),
    ("John Muir Trail", "fitness_certificate", None, None),
    ("PCT Long-distance Permit", "travel_insurance_altitude", None, None),
    ("Sipadan", "travel_insurance_diving", None, None),
    ("Silver Bank Whale Swimming", "travel_insurance_diving", None, None),
    ("Silver Bank Whale Swimming", "guide_booking_confirmation", None, None),
    ("Son Doong Cave", "fitness_certificate", None, None),
    ("Son Doong Cave", "guide_booking_confirmation",
     "Oxalis Adventure is the only licensed operator - your booking confirmation doubles as your expedition permit.",
     "Oxalis Adventure הוא המפעיל המורשה היחיד - אישור ההזמנה שלכם משמש גם כהיתר המסע."),
    ("Corcovado NP – Sirena Station", "guide_booking_confirmation", None, None),
    ("Torres del Paine W Circuit", "fitness_certificate", None, None),
    ("Otter Trail", "fitness_certificate", None, None),
    ("Chirripó National Park", "fitness_certificate", None, None),
    ("Antelope Canyon", "guide_booking_confirmation", None, None),
    ("Skellig Michael", "guide_booking_confirmation", None, None),
]

# International (non-domestic-US) destinations that also get the two general-default
# requirements attached automatically. Domestic US destinations are excluded from
# passport_validity since most users of those are US residents traveling internally.
_NON_DOMESTIC_COUNTRIES = {
    "Peru", "Rwanda", "Malaysia", "Costa Rica", "France", "Netherlands", "Canada",
    "New Zealand", "Chile", "South Africa", "Vietnam", "Ireland", "Dominican Republic", "India",
}
