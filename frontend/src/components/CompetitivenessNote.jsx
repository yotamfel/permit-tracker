export const COMPETITIVENESS_INFO = {
  low: {
    label: "Low competitiveness",
    text: "Straightforward to get - rarely sells out.",
    color: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
  },
  medium: {
    label: "Medium competitiveness",
    text: "Can sell out in peak season - don't wait too long.",
    color: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
  },
  high: {
    label: "High competitiveness",
    text: "Expect real competition for a spot - plan ahead.",
    color: "bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300",
  },
  very_high: {
    label: "Very high competitiveness",
    text: "Often sells out within hours or days of opening.",
    color: "bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300",
  },
};

export default function CompetitivenessNote({ level }) {
  const info = COMPETITIVENESS_INFO[level];
  if (!info) return null;
  return (
    <div className="mt-4 flex items-center gap-2 text-sm">
      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${info.color}`}>{info.label}</span>
      <span className="text-stone-600 dark:text-stone-400">{info.text}</span>
    </div>
  );
}
