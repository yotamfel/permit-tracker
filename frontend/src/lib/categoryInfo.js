export const CATEGORY_INFO = {
  trek: { icon: "🥾", text: "text-emerald-700 dark:text-emerald-300", gradient: "from-emerald-200 to-emerald-400 dark:from-emerald-950 dark:to-emerald-800" },
  national_park_entry: { icon: "🏞️", text: "text-green-700 dark:text-green-300", gradient: "from-green-200 to-green-400 dark:from-green-950 dark:to-green-800" },
  camping: { icon: "⛺", text: "text-lime-700 dark:text-lime-300", gradient: "from-lime-200 to-lime-400 dark:from-lime-950 dark:to-lime-800" },
  diving: { icon: "🤿", text: "text-sky-700 dark:text-sky-300", gradient: "from-sky-200 to-sky-400 dark:from-sky-950 dark:to-sky-800" },
  wildlife_safari: { icon: "🦁", text: "text-orange-700 dark:text-orange-300", gradient: "from-orange-200 to-orange-400 dark:from-orange-950 dark:to-orange-800" },
  thru_hike: { icon: "🎒", text: "text-teal-700 dark:text-teal-300", gradient: "from-teal-200 to-teal-400 dark:from-teal-950 dark:to-teal-800" },
  tourist_attraction: { icon: "🗼", text: "text-violet-700 dark:text-violet-300", gradient: "from-violet-200 to-violet-400 dark:from-violet-950 dark:to-violet-800" },
  seasonal_nature_event: { icon: "🌸", text: "text-pink-700 dark:text-pink-300", gradient: "from-pink-200 to-pink-400 dark:from-pink-950 dark:to-pink-800" },
  endurance_event: { icon: "🏁", text: "text-red-700 dark:text-red-300", gradient: "from-red-200 to-red-400 dark:from-red-950 dark:to-red-800" },
};

export const DEFAULT_CATEGORY = {
  icon: "📍",
  text: "text-stone-700 dark:text-stone-300",
  gradient: "from-stone-200 to-stone-400 dark:from-stone-800 dark:to-stone-700",
};

export const CATEGORY_ORDER = Object.keys(CATEGORY_INFO);
