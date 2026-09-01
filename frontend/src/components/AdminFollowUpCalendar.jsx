import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];
const WEEKDAY_LABELS = ["S", "M", "T", "W", "T", "F", "S"];

export default function AdminFollowUpCalendar() {
  const [monthOffset, setMonthOffset] = useState(0);
  const [followUps, setFollowUps] = useState([]);
  const [destinations, setDestinations] = useState([]);
  const [selectedDay, setSelectedDay] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newFollowUp, setNewFollowUp] = useState({ destination_id: "", due_date: "", title: "", notes: "" });

  const { year, month } = useMemo(() => {
    const d = new Date();
    d.setDate(1);
    d.setMonth(d.getMonth() + monthOffset);
    return { year: d.getFullYear(), month: d.getMonth() + 1 };
  }, [monthOffset]);

  const load = () => {
    api.get("/admin/api/follow-ups").then((res) => setFollowUps(res.data));
    api.get("/admin/api/destinations").then((res) => setDestinations(res.data));
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    setSelectedDay(null);
  }, [year, month]);

  const byDay = useMemo(() => {
    const map = {};
    for (const f of followUps) {
      const [fy, fm, fd] = f.due_date.split("-").map(Number);
      if (fy === year && fm === month) {
        (map[fd] ||= []).push(f);
      }
    }
    return map;
  }, [followUps, year, month]);

  const firstWeekday = new Date(year, month - 1, 1).getDay();
  const daysInMonth = new Date(year, month, 0).getDate();
  const cells = [...Array(firstWeekday).fill(null), ...Array.from({ length: daysInMonth }, (_, i) => i + 1)];

  const toggleDone = async (f) => {
    await api.put(`/admin/api/follow-ups/${f.id}`, { ...f, is_done: !f.is_done });
    load();
  };

  const deleteFollowUp = async (id) => {
    await api.delete(`/admin/api/follow-ups/${id}`);
    load();
  };

  const addFollowUp = async () => {
    if (!newFollowUp.destination_id || !newFollowUp.due_date || !newFollowUp.title) return;
    await api.post("/admin/api/follow-ups", newFollowUp);
    setNewFollowUp({ destination_id: "", due_date: "", title: "", notes: "" });
    setShowAddForm(false);
    load();
  };

  return (
    <div>
      <div className="mx-auto max-w-xs">
        <div className="mb-3 flex items-center justify-between">
          <button
            onClick={() => setMonthOffset((o) => o - 1)}
            className="rounded-full border border-slate-300 px-2 py-0.5 text-sm dark:border-slate-600"
          >
            ←
          </button>
          <span className="text-sm font-medium text-slate-800 dark:text-slate-100">
            {MONTH_NAMES[month - 1]} {year}
          </span>
          <button
            onClick={() => setMonthOffset((o) => o + 1)}
            className="rounded-full border border-slate-300 px-2 py-0.5 text-sm dark:border-slate-600"
          >
            →
          </button>
        </div>

        <div className="grid grid-cols-7 gap-0.5 text-center text-[10px] font-medium text-slate-500 dark:text-slate-400">
          {WEEKDAY_LABELS.map((w, i) => (
            <div key={i} className="pb-1">
              {w}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-0.5">
          {cells.map((day, i) => {
            if (day === null) return <div key={`empty-${i}`} />;
            const dayItems = byDay[day] || [];
            const hasItems = dayItems.length > 0;
            const allDone = hasItems && dayItems.every((f) => f.is_done);
            const isSelected = selectedDay === day;
            return (
              <button
                key={day}
                onClick={() => hasItems && setSelectedDay(isSelected ? null : day)}
                className={`aspect-square rounded-md border text-xs ${
                  isSelected
                    ? "border-blue-600 bg-blue-200 font-semibold text-blue-950 dark:border-blue-400 dark:bg-blue-800 dark:text-blue-50"
                    : hasItems
                      ? allDone
                        ? "border-emerald-400 bg-emerald-100 text-emerald-800 hover:bg-emerald-200 dark:border-emerald-600 dark:bg-emerald-900/40 dark:text-emerald-200"
                        : "border-blue-400 bg-blue-100 font-medium text-blue-900 hover:bg-blue-200 dark:border-blue-500 dark:bg-blue-900/40 dark:text-blue-200 dark:hover:bg-blue-900/70"
                      : "border-slate-200 text-slate-500 dark:border-slate-700 dark:text-slate-300"
                }`}
              >
                {day}
              </button>
            );
          })}
        </div>

        {selectedDay && byDay[selectedDay] && (
          <div className="mt-3 space-y-2 rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-slate-800 dark:bg-slate-900/50">
            {byDay[selectedDay].map((f) => (
              <div key={f.id} className="rounded border border-slate-200 bg-white p-2 text-xs dark:border-slate-700 dark:bg-slate-900">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <Link to={`/admin/destinations/${f.destination_id}`} className="font-semibold text-blue-700 underline dark:text-blue-400">
                      {f.destination_name}
                    </Link>
                    <p className={`mt-0.5 font-medium ${f.is_done ? "text-slate-400 line-through" : "text-slate-800 dark:text-slate-200"}`}>
                      {f.title}
                    </p>
                  </div>
                  <label className="flex shrink-0 items-center gap-1 text-slate-500 dark:text-slate-400">
                    <input type="checkbox" checked={f.is_done} onChange={() => toggleDone(f)} />
                    done
                  </label>
                </div>
                {f.notes && <p className="mt-1 whitespace-pre-wrap text-slate-600 dark:text-slate-400">{f.notes}</p>}
                <button onClick={() => deleteFollowUp(f.id)} className="mt-1 text-red-600 underline">
                  delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-4">
        {!showAddForm ? (
          <button
            onClick={() => setShowAddForm(true)}
            className="rounded bg-slate-700 px-3 py-1.5 text-xs font-medium text-white"
          >
            + schedule a check
          </button>
        ) : (
          <div className="max-w-md space-y-2 rounded border border-slate-200 p-3 text-sm dark:border-slate-800">
            <select
              value={newFollowUp.destination_id}
              onChange={(e) => setNewFollowUp((f) => ({ ...f, destination_id: e.target.value }))}
              className="block w-full rounded border border-slate-300 bg-white px-2 py-1 text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            >
              <option value="">Select destination...</option>
              {destinations.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.country})
                </option>
              ))}
            </select>
            <input
              type="date"
              value={newFollowUp.due_date}
              onChange={(e) => setNewFollowUp((f) => ({ ...f, due_date: e.target.value }))}
              className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
            />
            <input
              placeholder="Title, e.g. Check official 2026/27 season prices"
              value={newFollowUp.title}
              onChange={(e) => setNewFollowUp((f) => ({ ...f, title: e.target.value }))}
              className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
            />
            <textarea
              placeholder="Notes - what to check, where to check it, links, context"
              rows={3}
              value={newFollowUp.notes}
              onChange={(e) => setNewFollowUp((f) => ({ ...f, notes: e.target.value }))}
              className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
            />
            <div className="flex gap-2">
              <button onClick={addFollowUp} className="rounded bg-blue-600 px-3 py-1.5 text-xs font-medium text-white">
                Add
              </button>
              <button
                onClick={() => setShowAddForm(false)}
                className="rounded border border-slate-300 px-3 py-1.5 text-xs dark:border-slate-700"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
