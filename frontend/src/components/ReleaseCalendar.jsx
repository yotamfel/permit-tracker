import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];
const WEEKDAY_LABELS = ["S", "M", "T", "W", "T", "F", "S"];
const MAX_MONTHS_AHEAD = 3;

export default function ReleaseCalendar() {
  const [monthOffset, setMonthOffset] = useState(0);
  const [entries, setEntries] = useState([]);
  const [selectedDay, setSelectedDay] = useState(null);

  const { year, month } = useMemo(() => {
    const d = new Date();
    d.setDate(1);
    d.setMonth(d.getMonth() + monthOffset);
    return { year: d.getFullYear(), month: d.getMonth() + 1 };
  }, [monthOffset]);

  useEffect(() => {
    const monthParam = `${year}-${String(month).padStart(2, "0")}`;
    api.get("/api/destinations/calendar", { params: { month: monthParam } }).then((res) => setEntries(res.data));
    setSelectedDay(null);
  }, [year, month]);

  const byDay = useMemo(() => {
    const map = {};
    for (const entry of entries) {
      for (const dateStr of entry.dates) {
        const day = Number(dateStr.split("-")[2]);
        (map[day] ||= []).push(entry);
      }
    }
    return map;
  }, [entries]);

  const firstWeekday = new Date(year, month - 1, 1).getDay();
  const daysInMonth = new Date(year, month, 0).getDate();
  const cells = [...Array(firstWeekday).fill(null), ...Array.from({ length: daysInMonth }, (_, i) => i + 1)];

  return (
    <section className="mx-auto max-w-5xl px-4 py-14">
      <h2 className="mb-6 text-center text-2xl font-bold text-stone-900 dark:text-stone-100">What opens this month</h2>

      <div className="mx-auto max-w-xs">
        <div className="mb-3 flex items-center justify-between">
          <button
            onClick={() => setMonthOffset((o) => o - 1)}
            disabled={monthOffset === 0}
            className="rounded-full border border-stone-300 px-2 py-0.5 text-sm text-stone-700 disabled:opacity-30 dark:border-stone-600 dark:text-stone-200"
          >
            ←
          </button>
          <span className="text-sm font-medium text-stone-700 dark:text-stone-200">
            {MONTH_NAMES[month - 1]} {year}
          </span>
          <button
            onClick={() => setMonthOffset((o) => Math.min(o + 1, MAX_MONTHS_AHEAD))}
            disabled={monthOffset === MAX_MONTHS_AHEAD}
            className="rounded-full border border-stone-300 px-2 py-0.5 text-sm text-stone-700 disabled:opacity-30 dark:border-stone-600 dark:text-stone-200"
          >
            →
          </button>
        </div>

        <div className="grid grid-cols-7 gap-0.5 text-center text-[10px] font-medium text-stone-500 dark:text-stone-400">
          {WEEKDAY_LABELS.map((w, i) => (
            <div key={i} className="pb-1">
              {w}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-0.5">
          {cells.map((day, i) => {
            if (day === null) return <div key={`empty-${i}`} />;
            const dayEntries = byDay[day] || [];
            const hasRelease = dayEntries.length > 0;
            const isSelected = selectedDay === day;
            return (
              <button
                key={day}
                onClick={() => hasRelease && setSelectedDay(isSelected ? null : day)}
                className={`aspect-square rounded-md border text-xs ${
                  isSelected
                    ? "border-amber-600 bg-amber-200 font-semibold text-amber-950 dark:border-amber-400 dark:bg-amber-800 dark:text-amber-50"
                    : hasRelease
                      ? "border-amber-400 bg-amber-100 font-medium text-amber-900 hover:bg-amber-200 dark:border-amber-500 dark:bg-amber-900/40 dark:text-amber-200 dark:hover:bg-amber-900/70"
                      : "border-stone-200 text-stone-500 dark:border-stone-700 dark:text-stone-500"
                }`}
              >
                {day}
              </button>
            );
          })}
        </div>

        {selectedDay && byDay[selectedDay] && (
          <div className="mt-3 rounded-xl border border-stone-200 bg-stone-50 p-3 dark:border-stone-800 dark:bg-stone-900/50">
            <h3 className="text-xs font-semibold text-stone-900 dark:text-stone-100">
              Opening {MONTH_NAMES[month - 1]} {selectedDay}, {year}
            </h3>
            <ul className="mt-1.5 space-y-1">
              {byDay[selectedDay].map((entry) => (
                <li key={entry.destination_id}>
                  <Link
                    to={`/destinations/${entry.destination_id}`}
                    className="text-sm text-amber-700 hover:underline dark:text-amber-400"
                  >
                    {entry.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}

        {entries.length === 0 && (
          <p className="mt-3 text-center text-xs text-stone-500 dark:text-stone-400">Nothing with a known opening date this month.</p>
        )}
      </div>
    </section>
  );
}
