import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import { regionFor } from "../lib/regions";
import { MONTH_NAMES, monthInSeason } from "../lib/months";
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

const OPENS_SOON_OPTIONS = [
  ["30", "Within 30 days"],
  ["60", "Within 60 days"],
  ["90", "Within 90 days"],
];

const EMPTY_FILTERS = { country: "", category: "", region: "", opensSoon: "", season: "" };

const COMPETITIVENESS_RANK = { very_high: 3, high: 2, medium: 1, low: 0 };

const SORT_OPTIONS = [
  ["soonest", "Opening soonest"],
  ["competitiveness", "Most competitive first"],
  ["name", "Name (A-Z)"],
];

function sortDestinations(list, sortBy) {
  const sorted = [...list];
  if (sortBy === "soonest") {
    sorted.sort((a, b) => {
      if (!a.next_known_release && !b.next_known_release) return 0;
      if (!a.next_known_release) return 1;
      if (!b.next_known_release) return -1;
      return new Date(a.next_known_release) - new Date(b.next_known_release);
    });
  } else if (sortBy === "competitiveness") {
    sorted.sort((a, b) => (COMPETITIVENESS_RANK[b.competitiveness_level] ?? -1) - (COMPETITIVENESS_RANK[a.competitiveness_level] ?? -1));
  } else {
    sorted.sort((a, b) => a.name.localeCompare(b.name));
  }
  return sorted;
}

export default function Browse() {
  const { t, i18n } = useTranslation();
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [panelOpen, setPanelOpen] = useState(false);
  const [sortBy, setSortBy] = useState("soonest");

  useEffect(() => {
    // The full catalog is an account perk - guests get a small taste on the
    // login page instead (see Login.jsx) and are sent there to sign up.
    if (!authLoading && !user) {
      navigate("/login", { replace: true });
    }
  }, [authLoading, user, navigate]);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    // Fetch everything once and filter client-side - the catalog is small
    // (~100s of rows) and several filters (region, opens-soon, season) are
    // derived/computed rather than plain DB columns, so there's nothing to
    // gain from round-tripping to the server per filter change.
    api
      .get("/api/destinations", { params: { locale: i18n.language } })
      .then((res) => setDestinations(res.data))
      .finally(() => setLoading(false));
  }, [i18n.language, user]);

  const countries = useMemo(() => [...new Set(destinations.map((d) => d.country))].sort(), [destinations]);
  const regions = useMemo(() => [...new Set(destinations.map((d) => regionFor(d.country)))].sort(), [destinations]);

  const filterDefs = [
    { key: "country", label: t("browse.filter_country"), allLabel: t("browse.all"), options: countries.map((c) => [c, c]) },
    { key: "category", label: t("browse.filter_category"), allLabel: t("browse.all"), options: CATEGORIES.map((c) => [c, t(`category.${c}`)]) },
    { key: "region", label: "Region", allLabel: t("browse.all"), options: regions.map((r) => [r, r]) },
    { key: "opensSoon", label: "Opens soon", allLabel: "Any time", options: OPENS_SOON_OPTIONS },
    { key: "season", label: "Season", allLabel: t("browse.all"), options: MONTH_NAMES.map((m, i) => [String(i + 1), m]) },
  ];
  const activeFilters = filterDefs.filter((f) => filters[f.key]);

  const filtered = useMemo(() => {
    const now = Date.now();
    const opensSoonMs = filters.opensSoon ? Number(filters.opensSoon) * 24 * 60 * 60 * 1000 : null;
    return destinations.filter((d) => {
      if (filters.country && d.country !== filters.country) return false;
      if (filters.category && d.category !== filters.category) return false;
      if (filters.region && regionFor(d.country) !== filters.region) return false;
      if (opensSoonMs) {
        if (!d.next_known_release) return false;
        const diff = new Date(d.next_known_release).getTime() - now;
        if (diff < 0 || diff > opensSoonMs) return false;
      }
      if (filters.season) {
        if (!monthInSeason(Number(filters.season), d.season_start_month, d.season_end_month)) return false;
      }
      return true;
    });
  }, [destinations, filters]);

  const sorted = useMemo(() => sortDestinations(filtered, sortBy), [filtered, sortBy]);

  if (authLoading || !user) return null;

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">Catalog</h1>
      <p className="mt-1 text-stone-700 dark:text-stone-400">{t("browse.subtitle")}</p>

      <div className="sticky top-0 z-30 -mx-4 mt-6 bg-stone-50/95 px-4 py-3 backdrop-blur dark:bg-stone-950/95">
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setPanelOpen((o) => !o)}
            className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm font-medium ${
              activeFilters.length > 0
                ? "border-amber-400 bg-amber-50 text-amber-800 dark:border-amber-700 dark:bg-amber-900/30 dark:text-amber-300"
                : "border-stone-300 text-stone-700 hover:bg-stone-100 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
            }`}
          >
            <span aria-hidden="true">⚙</span>
            Filters{activeFilters.length > 0 ? ` (${activeFilters.length})` : ""}
            <span aria-hidden="true" className="text-xs">
              {panelOpen ? "▴" : "▾"}
            </span>
          </button>

          {activeFilters.map((f) => {
            const selectedLabel = f.options.find(([v]) => v === filters[f.key])?.[1] ?? filters[f.key];
            return (
              <span
                key={f.key}
                className="flex items-center gap-1.5 rounded-full border border-amber-400 bg-amber-50 px-3 py-1.5 text-sm text-amber-800 dark:border-amber-700 dark:bg-amber-900/30 dark:text-amber-300"
              >
                {f.label}: {selectedLabel}
                <button
                  type="button"
                  aria-label={`Clear ${f.label} filter`}
                  onClick={() => setFilters((cur) => ({ ...cur, [f.key]: "" }))}
                  className="text-amber-600 hover:text-amber-900 dark:text-amber-400 dark:hover:text-amber-100"
                >
                  ×
                </button>
              </span>
            );
          })}

          {activeFilters.length > 0 && (
            <button
              type="button"
              onClick={() => setFilters(EMPTY_FILTERS)}
              className="text-sm text-stone-500 underline hover:text-stone-700 dark:text-stone-400 dark:hover:text-stone-200"
            >
              Clear all
            </button>
          )}

          <label className="ms-auto flex items-center gap-1.5 text-sm text-stone-600 dark:text-stone-400">
            Sort:
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="rounded-lg border border-stone-300 bg-white px-2 py-1 text-sm text-stone-900 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-100"
            >
              {SORT_OPTIONS.map(([v, label]) => (
                <option key={v} value={v}>
                  {label}
                </option>
              ))}
            </select>
          </label>
        </div>

        {!loading && (
          <p className="mt-2 text-xs text-stone-500 dark:text-stone-400">
            Showing {sorted.length} of {destinations.length} destinations
          </p>
        )}

        {panelOpen && (
          <>
            <div className="fixed inset-0 z-10" onClick={() => setPanelOpen(false)} />
            <div className="absolute z-20 mt-2 grid w-full grid-cols-1 gap-4 rounded-2xl border border-stone-200 bg-white p-4 shadow-lg sm:grid-cols-2 lg:grid-cols-3 dark:border-stone-800 dark:bg-stone-900">
              {filterDefs.map((f) => (
                <label key={f.key} className="block text-sm">
                  <span className="mb-1 block font-medium text-stone-700 dark:text-stone-300">{f.label}</span>
                  <select
                    value={filters[f.key]}
                    onChange={(e) => setFilters((cur) => ({ ...cur, [f.key]: e.target.value }))}
                    className="block w-full rounded-lg border border-stone-300 bg-white px-2 py-1.5 text-stone-900 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-100"
                  >
                    <option value="">{f.allLabel}</option>
                    {f.options.map(([v, label]) => (
                      <option key={v} value={v}>
                        {label}
                      </option>
                    ))}
                  </select>
                </label>
              ))}
            </div>
          </>
        )}
      </div>

      {loading ? (
        <p className="mt-8 text-stone-500">...</p>
      ) : sorted.length === 0 ? (
        <p className="mt-8 text-stone-500">{t("browse.no_results")}</p>
      ) : (
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {sorted.map((d) => (
            <DestinationCard key={d.id} d={d} />
          ))}
        </div>
      )}
    </div>
  );
}
