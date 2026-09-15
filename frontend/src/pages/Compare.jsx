import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import { MONTH_NAMES } from "../lib/months";
import SeoHead from "../components/SeoHead";

const ROWS = [
  { label: "Country", render: (d) => d.country },
  { label: "Category", render: (d, t) => t(`category.${d.category}`) },
  { label: "Mechanism", render: (d, t) => t(`mechanism_type.${d.mechanism_type}`) },
  { label: "Competitiveness", render: (d, t) => (d.competitiveness_level ? t(`competitiveness_level.${d.competitiveness_level}`) : "-") },
  {
    label: "Next known opening",
    render: (d) => (d.next_known_release ? new Date(d.next_known_release).toLocaleDateString("en-US") : "Not computable"),
  },
  {
    label: "Season",
    render: (d) =>
      d.season_start_month && d.season_end_month
        ? `${MONTH_NAMES[d.season_start_month - 1]} - ${MONTH_NAMES[d.season_end_month - 1]}`
        : "-",
  },
  { label: "Unlock price", render: (d) => `$${d.price_usd.toFixed(2)}` },
  { label: "Safety advisory", render: (d) => d.safety_advisory || "-" },
];

export default function Compare() {
  const { t, i18n } = useTranslation();
  const { user, loading: authLoading } = useAuth();
  const [searchParams] = useSearchParams();
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);

  const ids = (searchParams.get("ids") || "").split(",").filter(Boolean);

  useEffect(() => {
    if (!user || ids.length === 0) {
      setLoading(false);
      return;
    }
    Promise.all(ids.map((id) => api.get(`/api/destinations/${id}`, { params: { locale: i18n.language } })))
      .then((results) => setDestinations(results.map((r) => r.data)))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, user]);

  if (authLoading) return null;
  if (!user) return <div className="mx-auto max-w-3xl px-4 py-8">Log in to compare destinations.</div>;

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <SeoHead title="Compare Destinations" path="/compare" />
      <Link to="/catalog" className="text-sm text-stone-500 hover:text-amber-700 dark:text-stone-400 dark:hover:text-amber-400">
        ← Back to catalog
      </Link>
      <h1 className="mt-2 text-2xl font-bold text-stone-900 dark:text-stone-100">Compare destinations</h1>

      {loading ? (
        <p className="mt-8 text-stone-500">...</p>
      ) : destinations.length === 0 ? (
        <p className="mt-8 text-stone-500 dark:text-stone-400">
          Nothing to compare -{" "}
          <Link to="/catalog" className="text-amber-700 underline dark:text-amber-400">
            pick a couple of destinations from the catalog
          </Link>
          .
        </p>
      ) : (
        <div className="mt-6 overflow-x-auto">
          <table className="w-full min-w-[500px] border-collapse text-sm">
            <thead>
              <tr>
                <th className="border-b border-stone-200 p-2 text-left dark:border-stone-800"></th>
                {destinations.map((d) => (
                  <th key={d.id} className="border-b border-stone-200 p-2 text-left dark:border-stone-800">
                    <Link
                      to={`/destinations/${d.id}`}
                      className="font-semibold text-stone-900 hover:text-amber-700 dark:text-stone-100 dark:hover:text-amber-400"
                    >
                      {d.name}
                    </Link>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {ROWS.map((row) => (
                <tr key={row.label}>
                  <td className="border-b border-stone-200 p-2 font-medium text-stone-600 dark:border-stone-800 dark:text-stone-400">
                    {row.label}
                  </td>
                  {destinations.map((d) => (
                    <td key={d.id} className="border-b border-stone-200 p-2 text-stone-800 dark:border-stone-800 dark:text-stone-300">
                      {row.render(d, t)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
