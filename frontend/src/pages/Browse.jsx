import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";

const CATEGORIES = [
  "trek",
  "national_park_entry",
  "camping",
  "diving",
  "wildlife_safari",
  "thru_hike",
  "tourist_attraction",
  "seasonal_nature_event",
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
      <h1 className="text-2xl font-bold">{t("browse.title")}</h1>
      <p className="mt-1 text-slate-600 dark:text-slate-400">{t("browse.subtitle")}</p>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
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
        <p className="mt-8 text-slate-500">...</p>
      ) : destinations.length === 0 ? (
        <p className="mt-8 text-slate-500">{t("browse.no_results")}</p>
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {destinations.map((d) => (
            <DestinationCard key={d.id} d={d} t={t} />
          ))}
        </div>
      )}
    </div>
  );
}

function FilterSelect({ label, value, onChange, options, allLabel }) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="text-slate-500">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
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

function competitivenessColor(level) {
  return (
    {
      low: "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300",
      medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300",
      high: "bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300",
      very_high: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300",
    }[level] || ""
  );
}

function DestinationCard({ d, t }) {
  return (
    <Link
      to={`/destinations/${d.id}`}
      className="flex flex-col gap-2 rounded-lg border border-slate-200 p-4 transition hover:shadow-md dark:border-slate-800"
    >
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase tracking-wide text-slate-500">{t(`category.${d.category}`)}</span>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${competitivenessColor(d.competitiveness_level)}`}>
          {t(`competitiveness_level.${d.competitiveness_level}`)}
        </span>
      </div>
      <h2 className="text-lg font-semibold">{d.name}</h2>
      <p className="text-sm text-slate-500">{d.country}</p>
      <p className="text-sm text-slate-500">{t(`mechanism_type.${d.mechanism_type}`)}</p>
      <p className="text-sm">
        {t("browse.next_release")}:{" "}
        {d.next_known_release ? new Date(d.next_known_release).toLocaleDateString() : t("browse.not_computable")}
      </p>
      <div className="mt-2 text-sm font-medium">
        {d.is_owned ? (
          <span className="text-green-600 dark:text-green-400">{t("browse.owned")}</span>
        ) : (
          <span>{t("browse.unlock_for", { price: d.price_usd })}</span>
        )}
      </div>
    </Link>
  );
}
