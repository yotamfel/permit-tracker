# Permit Tracker App — Spec Addendum (Consolidated)

**This document extends `PROJECT_SPEC.md`. It does not replace it.** Everything below is additive or a scope update on top of the original spec. Where something here conflicts with the original, this document wins. This consolidated file replaces the three earlier addenda (v2, v3, v4) that were sent separately — treat this single file as the current, complete set of changes.

---

## 1. Positioning Change

The original spec framed this as an **alert/notification tool** for permit release dates. That framing is too narrow and overlaps heavily with existing single-purpose competitors (e.g. Campnab, Schnerp, and similar cancellation-scanning services that already cover US/Canada camping and NZ Great Walks in depth).

**Updated positioning: this is a pre-trip preparation assistant, not just an alert scanner.** Its value is:

1. **Breadth** — one place covering every category and country (treks, camping, diving, wildlife safaris, thru-hikes, tourist attractions, seasonal nature events) instead of five different niche single-country tools.
2. **Preparation, not just timing** — helping the user assemble everything needed to actually apply (documents, bureaucracy, gear, steps), not only telling them when a booking window opens.
3. Alerts (§8–9 of the original spec) remain a real feature, but they are **one part of the product, not the whole product.**

This changes nothing about the tech stack, DB engine, or MVP destination list (§10 of the original spec is unchanged). It changes the data model (§2 below) and how the product should be described in UI copy, onboarding, and marketing strings — any copy that currently frames the product as "get notified when permits open" should instead lead with preparation + breadth, e.g. "Everything you need to prepare for the world's hardest-to-get permits — documents, deadlines, and alerts, in one place" (placeholder direction, not final copy — write real copy in English first per the i18n rules, then translate into all locales per §3 below).

## 2. New Data Model: General Requirements Layer

**Problem this solves:** many bureaucratic requirements (passport validity, specific vaccinations, travel insurance with activity-specific coverage, fitness clearance) repeat across dozens of destinations. Without a shared layer, the same text would need to be duplicated into 30+ `checklist_items` rows and re-edited 30+ times whenever something changes.

### 2.1 New table: `general_requirements`

Standalone, reusable requirement definitions — not tied to any single destination.

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| requirement_type | enum | `passport_validity`, `visa`, `vaccination`, `travel_insurance`, `fitness_certificate`, `other` |
| title_key | text | translation key (see `translations` table, §4.3 of original spec) — e.g. `req.passport_6mo` |
| description_key | text | translation key for longer explanation |
| is_general_default | boolean | if true, this requirement is suggested for every destination that shares its category/region unless explicitly excluded — see §2.3 |

### 2.2 New join table: `destination_requirements`

Links destinations to the general requirements that apply to them, plus destination-specific notes.

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| destination_id | UUID FK → destinations | |
| general_requirement_id | UUID FK → general_requirements | |
| destination_specific_note_key | text nullable | translation key for a note that overrides/extends the generic requirement text for this specific destination (e.g. generic "yellow fever vaccination may be required" becomes destination-specific "required for entry to Rwanda — carry certificate" for the gorilla trekking destination) |
| order_index | integer | display order relative to this destination's other requirements and checklist items |

### 2.3 Rendering logic on the destination detail page

The full "what you need to prepare" view for a destination (post-purchase, per §11.3 of the original spec) combines **two sources**, rendered together as one unified checklist, grouped by section:

1. **General requirements** — pulled via `destination_requirements` → `general_requirements`, rendered with the destination-specific note if present, else the generic description.
2. **Destination-specific checklist items** — the existing `checklist_items` table from the original spec, unchanged.

Suggested section grouping in the UI: "Documents & Bureaucracy" (passport, visa, vaccination, insurance — sourced from general requirements) then "Specific to this permit" (booking steps, gear, destination-only actions — sourced from checklist_items). Both should render through a shared `PrepItem` component so future item types don't require UI changes.

### 2.4 Admin workflow implication

When adding a new destination, the admin flow (§11.6 / §12 of original spec) should:

1. Prompt the admin to attach relevant existing `general_requirements` rows (checkbox list: "Passport 6-month validity", "Travel insurance", "Yellow fever vaccination", etc. — pick 0 or more).
2. Allow adding a destination-specific note per attached requirement.
3. Only then move to adding destination-specific `checklist_items`.

This keeps the general requirements layer from silently growing unused duplicate rows — reuse existing ones before creating new ones. Add a simple search/autocomplete over `general_requirements.title_key` in the admin UI for this.

### 2.5 Suggested seed data for `general_requirements`

Seed at least these before populating the 30 MVP destinations, since several will need to reference them immediately:

- Passport validity — minimum 6 months beyond travel dates (very common; applies to most international destinations)
- Travel insurance — general coverage
- Travel insurance — high-altitude/trekking-specific coverage (relevant to high-altitude US treks like Mount Whitney, and to any future high-altitude destinations)
- Travel insurance — diving-specific coverage (relevant to Sipadan, Silver Bank)
- Yellow fever vaccination certificate (relevant to gorilla trekking / Rwanda)
- Physical fitness / medical clearance (relevant to Son Doong, high-altitude treks)
- Valid guide/agency booking confirmation (relevant to `guided_tour_only` and Corcovado-style `fixed_daily_quota` destinations that mandate a licensed guide)

Do not seed anything beyond this list without checking with the user first — this is a starting set, not exhaustive, and each entry needs real sourced text before publishing (same human-verification rule as the destination data itself — see the "Definition of Done" section in the original spec, which still applies here).

## 3. Locale Scope Update — MVP Now Includes 6 Languages

The original spec (§6) specified English + Hebrew only for MVP, with other locales as a later phase. **This is now updated: MVP must support translation from English into all of the following at launch:**

- Hebrew (`he`) — RTL, as already specified in §6 of the original spec
- German (`de`)
- French (`fr`)
- Spanish (`es`)
- Portuguese (`pt`, Brazilian Portuguese variant — `pt-BR`)

English remains the source of truth / default locale. Every entity must have an `en` row before publishing; any locale missing a translation for a given item falls back to English automatically (no broken/blank UI in any language).

**Reasoning for this specific set of languages** (for context, not something to re-derive): German and French travelers are disproportionately represented in international trekking/adventure travel; Spanish covers both Spain and Latin America, where several MVP destinations are physically located (Peru, Chile, Costa Rica) — serving local/regional users as well as international travelers; Portuguese (Brazil) is a fast-growing outbound adventure-travel market. Chinese and Japanese were deliberately considered and excluded for now — not because the markets are small, but because serving them properly involves more than translation (different payment rails, different platform/distribution norms, in some cases access restrictions). Treat those as a separate future initiative if it comes up, not something to add via the standard translation workflow.

### 3.1 What This Changes Technically

Nothing in the architecture changes — this is exactly why the `translations` table (§4.3) and `react-i18next` namespace structure (§6) were built as generic, content-driven systems rather than hardcoded per-language. Concretely:

- **Static UI strings**: create `/locales/de/common.json`, `/locales/fr/common.json`, `/locales/es/common.json`, `/locales/pt-BR/common.json` alongside the existing `en` and `he` files, with the same keys.
- **Dynamic content** (destination names/descriptions, checklist items, general requirements from §2 above): every row that currently needs an `en` translation row also needs `de`, `fr`, `es`, and `pt-BR` rows before that destination is considered fully ready.
- **Language switcher UI**: must list all 6 locales (en, he, de, fr, es, pt-BR), not just 2.
- **RTL handling**: only Hebrew needs `dir="rtl"` — German/French/Spanish/Portuguese are all LTR, same as English. Don't apply RTL logic to them.

### 3.2 Practical Implication to Flag Back to the User

This is a real increase in translation workload, not just a config change: every piece of content for all 30 MVP destinations (names, descriptions, mechanism explanations, every checklist item, every general requirement) now needs to exist in **6 languages** instead of 2 before a destination can be considered "fully ready," per the fallback rule above. A destination can still be published with only English content (it'll just show English to everyone until translated), but if the goal is a genuinely multilingual launch on day one, translation is now a significant chunk of the content work — comparable in size to writing the checklists themselves. Flag this explicitly rather than silently assuming machine translation is an acceptable substitute for the human-verified content described in the original spec's Definition of Done.

## 4. No Other Changes

Tech stack, non-goals (§3 of original spec — still no mobile apps/IAP/WhatsApp/auto-publish in this phase), the 30 MVP destinations (§10), payments (§9), monitoring job (§8), and theming (§7) requirements are all unchanged. Implement this addendum as an extension of the existing schema and admin flow, not a rewrite.
