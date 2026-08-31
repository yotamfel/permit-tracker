import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import DestinationCard from "../components/DestinationCard";

const CATEGORIES = [
  "trek",
  "national_park_entry",
  "camping",
  "diving",
  "wildlife_safari",
  "thru_hike",
  "tourist_attraction",
  "seasonal_nature_event",
  "endurance_event",
];
const MECHANISMS = [
  "fixed_daily_quota",
  "lottery",
  "rolling_window",
  "fixed_annual_date",
  "weekly_release",
  "guided_tour_only",
  "single_operator_annual_quota",
  "first_come_first_served",
];
const COMPETITIVENESS = ["low", "medium", "high", "very_high"];

export default function Browse() {
  const { t, i18n } = useTranslation();
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ country: "", category: "", mechanism_type: "", competitiveness_level: "" });

  useEffect(() => {
    setLoading(true);
    const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
    params.locale = i18n.language;
    api
      .get("/api/destinations", { params })
      .then((res) => setDestinations(res.data))
      .finally(() => setLoading(false));
  }, [filters, i18n.language]);

  const countries = useMemo(() => [...new Set(destinations.map((d) => d.country))].sort(), [destinations]);

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">Catalog</h1>
      <p className="mt-1 text-stone-600 dark:text-stone-400">{t("browse.subtitle")}</p>

      <div className="mt-6 grid grid-cols-2 gap-3 rounded-2xl border border-stone-200 bg-stone-50 p-4 dark:border-stone-800 dark:bg-stone-900/50 sm:grid-cols-4">
        <FilterSelect
          label={t("browse.filter_country")}
          value={filters.country}
          onChange={(v) => setFilters((f) => ({ ...f, country: v }))}
          options={countries.map((c) => [c, c])}
          allLabel={t("browse.all")}
        />
        <FilterSelect
          label={t("browse.filter_category")}
          value={filters.category}
          onChange={(v) => setFilters((f) => ({ ...f, category: v }))}
          options={CATEGORIES.map((c) => [c, t(`category.${c}`)])}
          allLabel={t("browse.all")}
        />
        <FilterSelect
          label={t("browse.filter_mechanism")}
          value={filters.mechanism_type}
          onChange={(v) => setFilters((f) => ({ ...f, mechanism_type: v }))}
          options={MECHANISMS.map((m) => [m, t(`mechanism_type.${m}`)])}
          allLabel={t("browse.all")}
        />
        <FilterSelect
          label={t("browse.filter_competitiveness")}
          value={filters.competitiveness_level}
          onChange={(v) => setFilters((f) => ({ ...f, competitiveness_level: v }))}
          options={COMPETITIVENESS.map((c) => [c, t(`competitiveness_level.${c}`)])}
          allLabel={t("browse.all")}
        />
      </div>

      {loading ? (
        <p className="mt-8 text-stone-500">...</p>
      ) : destinations.length === 0 ? (
        <p className="mt-8 text-stone-500">{t("browse.no_results")}</p>
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {destinations.map((d) => (
            <DestinationCard key={d.id} d={d} />
          ))}
        </div>
      )}
    </div>
  );
}

function FilterSelect({ label, value, onChange, options, allLabel }) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="text-stone-500 dark:text-stone-400">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-lg border border-stone-300 bg-white px-2 py-1.5 dark:border-stone-700 dark:bg-stone-800"
      >
        <option value="">{allLabel}</option>
        {options.map(([value_, labelText]) => (
          <option key={value_} value={value_}>
            {labelText}
          </option>
        ))}
      </select>
    </label>
  );
}
