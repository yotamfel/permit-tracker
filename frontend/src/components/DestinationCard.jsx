import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

const CATEGORY_ICON = {
  trek: "🥾",
  national_park_entry: "🏞️",
  camping: "⛺",
  diving: "🤿",
  wildlife_safari: "🦁",
  thru_hike: "🎒",
  tourist_attraction: "🗼",
  seasonal_nature_event: "🌸",
};

function competitivenessColor(level) {
  return (
    {
      low: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
      medium: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
      high: "bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300",
      very_high: "bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300",
    }[level] || ""
  );
}

export default function DestinationCard({ d }) {
  const { t } = useTranslation();

  return (
    <Link
      to={`/destinations/${d.id}`}
      className="group flex flex-col gap-2 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg dark:border-stone-800 dark:bg-stone-900"
    >
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-stone-500 dark:text-stone-400">
          <span aria-hidden="true">{CATEGORY_ICON[d.category] || "📍"}</span>
          {t(`category.${d.category}`)}
        </span>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${competitivenessColor(d.competitiveness_level)}`}>
          {t(`competitiveness_level.${d.competitiveness_level}`)}
        </span>
      </div>
      <h2 className="text-lg font-semibold text-stone-900 group-hover:text-amber-700 dark:text-stone-100 dark:group-hover:text-amber-400">
        {d.name}
      </h2>
      <p className="text-sm text-stone-500 dark:text-stone-400">{d.country}</p>
      <p className="text-sm text-stone-500 dark:text-stone-400">{t(`mechanism_type.${d.mechanism_type}`)}</p>
      <p className="text-sm text-stone-700 dark:text-stone-300">
        {t("browse.next_release")}:{" "}
        {d.next_known_release ? new Date(d.next_known_release).toLocaleDateString() : t("browse.not_computable")}
      </p>
      {d.is_owned && (
        <div className="mt-2 text-sm font-semibold text-emerald-600 dark:text-emerald-400">
          ✓ {t("browse.owned")}
        </div>
      )}
    </Link>
  );
}
