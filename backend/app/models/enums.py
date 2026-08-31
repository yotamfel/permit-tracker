import enum


class Category(str, enum.Enum):
    trek = "trek"
    national_park_entry = "national_park_entry"
    camping = "camping"
    diving = "diving"
    wildlife_safari = "wildlife_safari"
    thru_hike = "thru_hike"
    tourist_attraction = "tourist_attraction"
    seasonal_nature_event = "seasonal_nature_event"
    # Mass-participation registration events (closed-road cycling sportives,
    # multi-day walking marches) - not a permit to visit a place, but a
    # capped-entry registration with the same "hard to get a spot" dynamic.
    endurance_event = "endurance_event"


class MechanismType(str, enum.Enum):
    fixed_daily_quota = "fixed_daily_quota"
    lottery = "lottery"
    rolling_window = "rolling_window"
    fixed_annual_date = "fixed_annual_date"
    weekly_release = "weekly_release"
    guided_tour_only = "guided_tour_only"
    single_operator_annual_quota = "single_operator_annual_quota"
    first_come_first_served = "first_come_first_served"


class IssuingAuthority(str, enum.Enum):
    government = "government"
    tribal = "tribal"
    commercial = "commercial"
    mixed = "mixed"


class CompetitivenessLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    very_high = "very_high"


class ChecklistItemType(str, enum.Enum):
    document = "document"
    action = "action"
    gear = "gear"
    payment = "payment"


class ChecklistItemSection(str, enum.Enum):
    # "Specific to this permit" - required for the actual permit/application itself.
    specific = "specific"
    # "Good to know" - useful but not strictly required for the permit application
    # (e.g. country-entry visa rules, health/safety notes for this destination).
    good_to_know = "good_to_know"


class Platform(str, enum.Enum):
    web = "web"
    ios = "ios"
    android = "android"


class PurchaseStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    refunded = "refunded"
    failed = "failed"


class NotificationStatus(str, enum.Enum):
    sent = "sent"
    failed = "failed"


class ReviewStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    dismissed = "dismissed"


class ThemePreference(str, enum.Enum):
    light = "light"
    dark = "dark"
    system = "system"


class ContactMessageStatus(str, enum.Enum):
    new = "new"
    read = "read"
    resolved = "resolved"


class RequirementType(str, enum.Enum):
    passport_validity = "passport_validity"
    visa = "visa"
    vaccination = "vaccination"
    travel_insurance = "travel_insurance"
    fitness_certificate = "fitness_certificate"
    other = "other"
