import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { CATEGORY_INFO, DEFAULT_CATEGORY } from "../lib/categoryInfo";

const COMPETITIVENESS_TEXT = {
  low: "text-emerald-700 dark:text-emerald-300",
  medium: "text-amber-700 dark:text-amber-300",
  high: "text-orange-700 dark:text-orange-300",
  very_high: "text-rose-700 dark:text-rose-300",
};

// Shared pill treatment for badges overlaid on the image - a translucent
// white/dark backdrop keeps them legible over any gradient now, and over
// whatever real photo eventually replaces the placeholder here.
function OverlayBadge({ className, children }) {
  return (
    <span
      className={`inline-flex w-fit items-center gap-1 rounded-full bg-white/90 px-2 py-0.5 text-xs font-medium shadow-sm backdrop-blur-sm dark:bg-stone-950/80 ${className}`}
    >
      {children}
    </span>
  );
}

export default function DestinationCard({ d }) {
  const { t } = useTranslation();
  const category = CATEGORY_INFO[d.category] || DEFAULT_CATEGORY;
  const competitivenessLabel = d.competitiveness_level ? t(`competitiveness_level.${d.competitiveness_level}`) : null;
  const competitivenessText = COMPETITIVENESS_TEXT[d.competitiveness_level];

  return (
    <Link
      to={`/destinations/${d.id}`}
      className="group flex flex-col overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg dark:border-stone-800 dark:bg-stone-900"
    >
      {/* Image slot - placeholder for now, ready to hold a real destination
          photo (same slot is reused on the destination detail page) without
          reworking this layout later. */}
      <div className={`relative aspect-[3/2] w-full bg-gradient-to-br ${category.gradient}`}>
        <span className="absolute inset-0 flex items-center justify-center text-5xl opacity-40" aria-hidden="true">
          {category.icon}
        </span>
        <div className="absolute left-2 top-2 flex flex-col items-start gap-1">
          <OverlayBadge className={`uppercase tracking-wide ${category.text}`}>
            <span aria-hidden="true">{category.icon}</span>
            {t(`category.${d.category}`)}
          </OverlayBadge>
          {competitivenessLabel && <OverlayBadge className={competitivenessText}>{competitivenessLabel}</OverlayBadge>}
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-1 p-4">
        <h2 className="font-display text-lg font-semibold text-stone-900 group-hover:text-amber-700 dark:text-stone-100 dark:group-hover:text-amber-400">
          {d.name}
        </h2>
        <p className="text-sm text-stone-500 dark:text-stone-400">
          {d.country} · {t(`mechanism_type.${d.mechanism_type}`)}
        </p>
        <p className="text-sm text-stone-800 dark:text-stone-300">
          {t("browse.next_release")}:{" "}
          {d.next_known_release ? new Date(d.next_known_release).toLocaleDateString() : t("browse.not_computable")}
        </p>
        {d.is_owned ? (
          <div className="mt-1 text-sm font-semibold text-emerald-600 dark:text-emerald-400">✓ {t("browse.owned")}</div>
        ) : (
          <div className="mt-1 text-sm font-semibold text-amber-700 dark:text-amber-400">
            {t("browse.unlock_for", { price: d.price_usd })}
          </div>
        )}
      </div>
    </Link>
  );
}
