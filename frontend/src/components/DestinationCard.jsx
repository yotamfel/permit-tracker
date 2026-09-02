import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { COMPETITIVENESS_INFO } from "./CompetitivenessNote";

const CATEGORY_INFO = {
  trek: { icon: "🥾", color: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300" },
  national_park_entry: { icon: "🏞️", color: "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300" },
  camping: { icon: "⛺", color: "bg-lime-100 text-lime-800 dark:bg-lime-900/40 dark:text-lime-300" },
  diving: { icon: "🤿", color: "bg-sky-100 text-sky-800 dark:bg-sky-900/40 dark:text-sky-300" },
  wildlife_safari: { icon: "🦁", color: "bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300" },
  thru_hike: { icon: "🎒", color: "bg-teal-100 text-teal-800 dark:bg-teal-900/40 dark:text-teal-300" },
  tourist_attraction: { icon: "🗼", color: "bg-violet-100 text-violet-800 dark:bg-violet-900/40 dark:text-violet-300" },
  seasonal_nature_event: { icon: "🌸", color: "bg-pink-100 text-pink-800 dark:bg-pink-900/40 dark:text-pink-300" },
  endurance_event: { icon: "🏁", color: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300" },
};
const DEFAULT_CATEGORY = { icon: "📍", color: "bg-stone-100 text-stone-700 dark:bg-stone-800 dark:text-stone-300" };

export default function DestinationCard({ d }) {
  const { t } = useTranslation();
  const category = CATEGORY_INFO[d.category] || DEFAULT_CATEGORY;
  const competitiveness = COMPETITIVENESS_INFO[d.competitiveness_level];

  return (
    <Link
      to={`/destinations/${d.id}`}
      className="group flex flex-col gap-2 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg dark:border-stone-800 dark:bg-stone-900"
    >
      <div className="flex flex-wrap items-center gap-1.5">
        <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium uppercase tracking-wide ${category.color}`}>
          <span aria-hidden="true">{category.icon}</span>
          {t(`category.${d.category}`)}
        </span>
        {competitiveness && (
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${competitiveness.color}`}>{competitiveness.label}</span>
        )}
      </div>
      <h2 className="font-display text-lg font-semibold text-stone-900 group-hover:text-amber-700 dark:text-stone-100 dark:group-hover:text-amber-400">
        {d.name}
      </h2>
      <p className="text-sm text-stone-500 dark:text-stone-400">{d.country}</p>
      <span className="w-fit rounded-full bg-stone-100 px-2 py-0.5 text-xs text-stone-600 dark:bg-stone-800 dark:text-stone-400">
        {t(`mechanism_type.${d.mechanism_type}`)}
      </span>
      <p className="text-sm text-stone-800 dark:text-stone-300">
        {t("browse.next_release")}:{" "}
        {d.next_known_release ? new Date(d.next_known_release).toLocaleDateString() : t("browse.not_computable")}
      </p>
      {d.is_owned ? (
        <div className="mt-2 text-sm font-semibold text-emerald-600 dark:text-emerald-400">✓ {t("browse.owned")}</div>
      ) : (
        <div className="mt-2 text-sm font-semibold text-amber-700 dark:text-amber-400">
          {t("browse.unlock_for", { price: d.price_usd })}
        </div>
      )}
    </Link>
  );
}
