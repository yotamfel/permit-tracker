import { useEffect, useState, useCallback } from "react";
import { useParams, useSearchParams, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import { getMechanismStats } from "../lib/mechanismConfig";
import CompetitivenessNote from "../components/CompetitivenessNote";

const TRAVEL_DATE_REQUIRED = new Set([
  "guided_tour_only",
  "first_come_first_served",
  "single_operator_annual_quota",
  "fixed_daily_quota",
  "rolling_window",
]);

const LEAD_TIME_OPTIONS = [
  { minutes: 20160, label: "2 weeks before" },
  { minutes: 10080, label: "1 week before" },
  { minutes: 4320, label: "3 days before" },
  { minutes: 1440, label: "1 day before" },
  { minutes: 30, label: "30 minutes before" },
];

export default function DestinationDetail() {
  const { id } = useParams();
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [destination, setDestination] = useState(null);
  const [checklist, setChecklist] = useState(null);
  const [error, setError] = useState("");
  const [subscription, setSubscription] = useState({ lead_time_minutes: 10080, travel_date: "" });
  const [alertMessage, setAlertMessage] = useState("");
  const [calendarStatus, setCalendarStatus] = useState("");

  const load = useCallback(() => {
    api.get(`/api/destinations/${id}`, { params: { locale: i18n.language } }).then((res) => setDestination(res.data));
    api
      .get(`/api/destinations/${id}/checklist`, { params: { locale: i18n.language } })
      .then((res) => setChecklist(res.data));
  }, [id, i18n.language]);

  useEffect(() => {
    load();
  }, [load]);

  const handleUnlock = async () => {
    setError("");
    try {
      const res = await api.post(`/api/checkout/${id}`);
      window.location.href = res.data.checkout_url;
    } catch (e) {
      setError(e.response?.data?.detail || t("auth.error"));
    }
  };

  const handleSubscribe = async (e) => {
    e.preventDefault();
    setAlertMessage("");
    try {
      await api.post("/api/subscriptions", {
        destination_id: id,
        lead_time_minutes: Number(subscription.lead_time_minutes),
        travel_date: subscription.travel_date || null,
      });
      setAlertMessage(t("alert.success"));
    } catch (e) {
      setAlertMessage(e.response?.data?.detail || t("auth.error"));
    }
  };

  const handleAddToCalendar = async () => {
    try {
      const res = await api.get(`/api/destinations/${id}/calendar.ics`, { responseType: "blob" });
      const url = window.URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${destination.name.toLowerCase().replace(/\s+/g, "-")}.ics`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setCalendarStatus(t("destination.calendar_downloaded"));
      setTimeout(() => setCalendarStatus(""), 4000);
    } catch {
      setError(t("auth.error"));
    }
  };

  const handleToggleItem = async (prepItemId, isCustom) => {
    // Optimistic update, then reconcile with the server response.
    setChecklist((c) => ({
      ...c,
      items: c.items.map((i) => (i.id === prepItemId ? { ...i, is_completed: !i.is_completed } : i)),
    }));
    try {
      const path = isCustom
        ? `/api/destinations/${id}/checklist/custom/${prepItemId}/toggle`
        : `/api/destinations/${id}/checklist/${prepItemId}/toggle`;
      const res = await api.post(path);
      setChecklist((c) => ({
        ...c,
        items: c.items.map((i) => (i.id === prepItemId ? { ...i, is_completed: res.data.is_completed } : i)),
      }));
    } catch {
      // revert on failure
      setChecklist((c) => ({
        ...c,
        items: c.items.map((i) => (i.id === prepItemId ? { ...i, is_completed: !i.is_completed } : i)),
      }));
    }
  };

  const handleAddCustomItem = async (text) => {
    const res = await api.post(`/api/destinations/${id}/checklist/custom`, { text });
    setChecklist((c) => ({ ...c, items: [...c.items, res.data] }));
  };

  const handleDeleteCustomItem = async (itemId) => {
    setChecklist((c) => ({ ...c, items: c.items.filter((i) => i.id !== itemId) }));
    try {
      await api.delete(`/api/destinations/${id}/checklist/custom/${itemId}`);
    } catch {
      load();
    }
  };

  if (!destination) return <div className="mx-auto max-w-3xl px-4 py-8 text-stone-500">...</div>;

  const purchaseStatus = searchParams.get("purchase");
  const needsTravelDate = TRAVEL_DATE_REQUIRED.has(destination.mechanism_type);

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <Link
        to="/catalog"
        className="mb-4 flex w-fit items-center gap-1 text-sm text-stone-500 hover:text-amber-700 dark:text-stone-400 dark:hover:text-amber-400"
      >
        ← Back to catalog
      </Link>

      {purchaseStatus === "success" && !destination.is_owned && (
        <div className="mb-4 rounded-xl bg-amber-100 p-3 text-sm text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
          Payment received - refresh in a few seconds once the webhook processes.
        </div>
      )}

      <span className="text-xs font-medium uppercase tracking-wide text-amber-700 dark:text-amber-400">
        {t(`category.${destination.category}`)}
      </span>
      <h1 className="mt-1 font-display text-3xl font-bold text-stone-900 dark:text-stone-50">{destination.name}</h1>
      <p className="text-stone-500 dark:text-stone-400">{destination.country}</p>

      {destination.description && (
        <p className="mt-4 max-w-prose text-stone-800 leading-relaxed dark:text-stone-300">{destination.description}</p>
      )}

      <CompetitivenessNote level={destination.competitiveness_level} />

      {destination.last_verified_at && (
        <p className="mt-2 flex items-center gap-1 text-xs text-emerald-700 dark:text-emerald-400">
          <span aria-hidden="true">✓</span>
          Verified {new Date(destination.last_verified_at).toLocaleDateString()}
        </p>
      )}

      <div className="mt-4 rounded-xl bg-amber-50 px-4 py-3 text-sm dark:bg-amber-900/20">
        <span className="font-semibold text-stone-900 dark:text-stone-100">{t("browse.next_release")}: </span>
        <span className="text-stone-800 dark:text-stone-300">
          {destination.next_known_release
            ? new Date(destination.next_known_release).toLocaleString(undefined, {
                dateStyle: "medium",
                timeStyle: "short",
              })
            : t("browse.not_computable")}
        </span>
        {destination.next_known_release && (
          <span className="ml-1 text-xs text-stone-500 dark:text-stone-400">(your local time)</span>
        )}
      </div>

      <section className="mt-8 rounded-2xl border border-stone-200 bg-stone-50 p-5 dark:border-stone-800 dark:bg-stone-900/50">
        <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">{t("destination.how_it_works")}</h2>
        <p className="mt-1 text-sm font-medium text-amber-700 dark:text-amber-400">
          {t(`mechanism_type.${destination.mechanism_type}`)}
        </p>
        {Object.keys(destination.mechanism_config).length > 0 && (
          <ul className="mt-2 space-y-1.5 rounded-lg bg-white p-3 dark:bg-stone-800">
            {getMechanismStats(destination.mechanism_type, destination.mechanism_config).map((stat, i) => (
              <li key={i} className="flex items-baseline gap-2 text-sm text-stone-800 dark:text-stone-300">
                <span className="text-amber-600 dark:text-amber-400" aria-hidden="true">
                  ●
                </span>
                <span>{stat}</span>
              </li>
            ))}
          </ul>
        )}
        {destination.is_owned ? (
          <p className="mt-2 text-stone-800 dark:text-stone-300">{destination.mechanism_explanation}</p>
        ) : (
          <div className="relative mt-2 overflow-hidden rounded-lg">
            <p className="select-none blur-sm">
              ████ ███████ ████ ████ ████████ ██ ████ ████████ ██████ ████ ████████ ██ ████ ████ ██████████.
            </p>
            <div className="absolute inset-0 flex items-center justify-center bg-stone-50/70 dark:bg-stone-900/70">
              <span className="text-xs text-stone-500 dark:text-stone-400">{t("destination.mechanism_locked")}</span>
            </div>
          </div>
        )}
      </section>

      <section className="mt-6">
        <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">{t("destination.checklist")}</h2>
        {checklist?.is_owned ? (
          <>
            <ChecklistProgress items={checklist.items} />
            <div className="mt-2 rounded-2xl border border-stone-200 p-4 dark:border-stone-800">
              <PrepSection
                title={t("destination.section_general")}
                items={checklist.items.filter((i) => i.section === "general")}
                t={t}
                onToggle={handleToggleItem}
              />
              <PrepSection
                title={t("destination.section_specific")}
                items={checklist.items.filter((i) => i.section === "specific")}
                t={t}
                onToggle={handleToggleItem}
              />
              <CustomChecklistSection
                items={checklist.items.filter((i) => i.section === "custom")}
                onToggle={handleToggleItem}
                onDelete={handleDeleteCustomItem}
                onAdd={handleAddCustomItem}
              />
            </div>
            <GoodToKnowSection
              title={t("destination.section_good_to_know")}
              items={checklist.items.filter((i) => i.section === "good_to_know")}
            />
          </>
        ) : (
          <div className="relative mt-2 rounded-2xl border-2 border-dashed border-stone-300 p-6 dark:border-stone-700">
            <div className="select-none space-y-2 text-stone-400 blur-sm">
              <p>████████ ████ ████████</p>
              <p>████ ████████████</p>
              <p>████████ ████</p>
            </div>
            {Object.keys(destination.checklist_item_counts).length > 0 && (
              <p className="mt-3 text-sm font-medium text-stone-800 dark:text-stone-300">
                This permit requires: {formatChecklistCounts(destination.checklist_item_counts)}
              </p>
            )}
            <p className="mt-2 text-sm text-stone-500 dark:text-stone-400">{t("destination.checklist_locked")}</p>
          </div>
        )}
      </section>

      {destination.is_owned && destination.application_url && (
        <section className="mt-6">
          <a
            href={destination.application_url}
            target="_blank"
            rel="noreferrer"
            className="inline-block rounded-full bg-amber-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-amber-700"
          >
            Continue to the official application site ↗
          </a>
          <p className="mt-2 text-xs text-stone-500 dark:text-stone-400">
            This opens the official site for {destination.name} in a new tab. You submit your
            application there directly - we don't process or submit applications on your behalf.
          </p>
        </section>
      )}

      {destination.is_owned && !destination.application_url && destination.operators.length > 0 && (
        <section className="mt-6 rounded-2xl border border-stone-200 p-5 dark:border-stone-800">
          <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">Book through one of these operators</h2>
          <p className="mt-1 text-xs text-stone-500 dark:text-stone-400">
            There's no single official booking site for {destination.name} - these are the legitimate operators.
            We don't favor any one of them.
          </p>
          <ul className="mt-3 space-y-2">
            {destination.operators.map((op, i) => (
              <li key={i} className="text-sm">
                {op.url ? (
                  <a href={op.url} target="_blank" rel="noreferrer" className="font-medium text-amber-700 hover:underline dark:text-amber-400">
                    {op.name} ↗
                  </a>
                ) : (
                  <span className="font-medium text-stone-800 dark:text-stone-200">{op.name}</span>
                )}
                {op.note && <span className="text-stone-500 dark:text-stone-400"> - {op.note}</span>}
                {(op.phone || op.email) && (
                  <div className="mt-0.5 flex flex-wrap gap-x-3 text-xs text-stone-500 dark:text-stone-400">
                    {op.phone && <a href={`tel:${op.phone}`} className="hover:underline">{op.phone}</a>}
                    {op.email && <a href={`mailto:${op.email}`} className="hover:underline">{op.email}</a>}
                  </div>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {destination.is_owned && destination.next_known_release && (
        <section className="mt-4">
          <button
            onClick={handleAddToCalendar}
            className="inline-flex items-center gap-1.5 rounded-full border border-stone-300 px-4 py-1.5 text-sm font-medium text-stone-700 hover:bg-stone-100 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
          >
            <span aria-hidden="true">📅</span> Add to calendar
          </button>
          {calendarStatus && <p className="mt-1.5 text-xs text-emerald-700 dark:text-emerald-400">{calendarStatus}</p>}
        </section>
      )}

      {destination.is_owned && destination.alternatives.length > 0 && (
        <section className="mt-6 rounded-2xl border border-stone-200 p-5 dark:border-stone-800">
          <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">If you don't get in</h2>
          <ul className="mt-2 space-y-2">
            {destination.alternatives.map((alt) => (
              <li key={alt.destination_id}>
                <Link
                  to={`/destinations/${alt.destination_id}`}
                  className="font-medium text-amber-700 hover:underline dark:text-amber-400"
                >
                  {alt.name}
                </Link>
                {alt.note && <span className="text-sm text-stone-500 dark:text-stone-400"> - {alt.note}</span>}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="mt-8 rounded-2xl border border-stone-200 p-5 dark:border-stone-800">
        {destination.is_owned ? (
          <>
            <p className="font-semibold text-emerald-600 dark:text-emerald-400">✓ {t("destination.already_owned")}</p>
            <form onSubmit={handleSubscribe} className="mt-4 space-y-3">
              <h3 className="font-semibold text-stone-900 dark:text-stone-100">{t("alert.title")}</h3>
              <label className="block text-sm text-stone-800 dark:text-stone-300">
                {t("alert.lead_time")}
                <select
                  value={subscription.lead_time_minutes}
                  onChange={(e) => setSubscription((s) => ({ ...s, lead_time_minutes: e.target.value }))}
                  className="mt-1 block w-full rounded-lg border border-stone-300 bg-white px-2 py-1.5 text-stone-900 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-100"
                >
                  {LEAD_TIME_OPTIONS.map((opt) => (
                    <option key={opt.minutes} value={opt.minutes}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </label>
              {needsTravelDate && (
                <label className="block text-sm text-stone-800 dark:text-stone-300">
                  {t("alert.travel_date")}
                  <input
                    type="date"
                    required
                    value={subscription.travel_date}
                    onChange={(e) => setSubscription((s) => ({ ...s, travel_date: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1.5 dark:border-stone-700"
                  />
                  <span className="text-xs text-stone-500 dark:text-stone-400">{t("alert.travel_date_help")}</span>
                </label>
              )}
              <button
                type="submit"
                className="rounded-full bg-amber-600 px-5 py-2 text-sm font-semibold text-white hover:bg-amber-700"
              >
                {t("alert.submit")}
              </button>
              {alertMessage && <p className="text-sm text-stone-800 dark:text-stone-300">{alertMessage}</p>}
            </form>
          </>
        ) : (
          <>
            {!user && <p className="mb-3 text-sm text-stone-500 dark:text-stone-400">Log in to unlock this destination.</p>}
            <p className="mb-3 text-sm text-stone-500 dark:text-stone-400">{t("destination.risk_framing")}</p>
            <button
              onClick={handleUnlock}
              disabled={!user}
              className="rounded-full bg-amber-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-amber-700 disabled:opacity-50"
            >
              {t("destination.unlock_cta", { price: destination.price_usd })}
            </button>
            {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          </>
        )}
      </section>

      <DestinationContactSection destinationId={id} destinationName={destination.name} userEmail={user?.email} />
    </div>
  );
}

function DestinationContactSection({ destinationId, destinationName, userEmail }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", email: userEmail || "", message: "" });
  const [status, setStatus] = useState("idle");

  const submit = async (e) => {
    e.preventDefault();
    setStatus("sending");
    try {
      await api.post("/api/contact", { ...form, destination_id: destinationId });
      setStatus("sent");
      setForm((f) => ({ ...f, message: "" }));
    } catch {
      setStatus("error");
    }
  };

  return (
    <section className="mt-8 border-t border-stone-200 pt-6 dark:border-stone-800">
      {!open ? (
        <button
          onClick={() => setOpen(true)}
          className="text-sm text-stone-500 underline hover:text-amber-700 dark:text-stone-400 dark:hover:text-amber-400"
        >
          Something wrong or missing on this page? Let us know
        </button>
      ) : status === "sent" ? (
        <p className="text-sm text-emerald-700 dark:text-emerald-400">Thanks - we received your message about {destinationName}.</p>
      ) : (
        <form onSubmit={submit} className="max-w-md space-y-2">
          <h3 className="text-sm font-semibold text-stone-900 dark:text-stone-100">Report an issue with {destinationName}</h3>
          <input
            required
            placeholder="Your name"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            className="block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1.5 text-sm dark:border-stone-700"
          />
          <input
            required
            type="email"
            placeholder="Your email"
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
            className="block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1.5 text-sm dark:border-stone-700"
          />
          <textarea
            required
            rows={3}
            placeholder="What's wrong or missing?"
            value={form.message}
            onChange={(e) => setForm((f) => ({ ...f, message: e.target.value }))}
            className="block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1.5 text-sm dark:border-stone-700"
          />
          <div className="flex items-center gap-2">
            <button
              type="submit"
              disabled={status === "sending"}
              className="rounded-full bg-amber-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-amber-700 disabled:opacity-50"
            >
              {status === "sending" ? "Sending..." : "Send"}
            </button>
            <button type="button" onClick={() => setOpen(false)} className="text-sm text-stone-500 dark:text-stone-400">
              Cancel
            </button>
          </div>
          {status === "error" && <p className="text-sm text-red-600">Something went wrong. Try again.</p>}
        </form>
      )}
    </section>
  );
}

const CHECKLIST_COUNT_LABELS = {
  document: (n) => `${n} document${n === 1 ? "" : "s"}`,
  action: (n) => `${n} registration step${n === 1 ? "" : "s"}`,
  gear: (n) => `${n} gear item${n === 1 ? "" : "s"}`,
  payment: (n) => `${n} payment${n === 1 ? "" : "s"}`,
  general_requirement: (n) => `${n} general requirement${n === 1 ? "" : "s"}`,
};

function formatChecklistCounts(counts) {
  return Object.entries(counts)
    .map(([type, n]) => (CHECKLIST_COUNT_LABELS[type] ? CHECKLIST_COUNT_LABELS[type](n) : `${n} ${type}`))
    .join(", ");
}

function ChecklistProgress({ items }) {
  // "Good to know" items are informational, not checkable - exclude them.
  const checkable = items.filter((i) => i.section !== "good_to_know");
  if (checkable.length === 0) return null;
  const done = checkable.filter((i) => i.is_completed).length;
  const percent = Math.round((done / checkable.length) * 100);
  return (
    <div className="mt-3">
      <div className="flex items-center justify-between text-xs text-stone-500 dark:text-stone-400">
        <span>Your progress</span>
        <span>
          {done}/{checkable.length} ({percent}%)
        </span>
      </div>
      <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-stone-200 dark:bg-stone-800">
        <div className="h-full rounded-full bg-emerald-500 transition-all" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

function PrepSection({ title, items, t, onToggle }) {
  if (items.length === 0) return null;
  return (
    <div className="mt-3">
      <h3 className="text-sm font-semibold text-stone-500 dark:text-stone-400">{title}</h3>
      <ul className="mt-1 space-y-2">
        {items.map((item) => (
          <PrepItem key={item.id} item={item} t={t} onToggle={onToggle} />
        ))}
      </ul>
    </div>
  );
}

function CustomChecklistSection({ items, onToggle, onDelete, onAdd }) {
  const [draft, setDraft] = useState("");
  const [adding, setAdding] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!draft.trim()) return;
    setAdding(true);
    try {
      await onAdd(draft.trim());
      setDraft("");
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="mt-3">
      <h3 className="text-sm font-semibold text-stone-500 dark:text-stone-400">Your own items</h3>
      {items.length > 0 && (
        <ul className="mt-1 space-y-2">
          {items.map((item) => (
            <li
              key={item.id}
              className={`flex items-start gap-2 rounded-lg px-2 py-1 text-sm ${item.is_completed ? "border border-emerald-300 dark:border-emerald-800" : ""}`}
            >
              <input
                type="checkbox"
                checked={item.is_completed}
                onChange={() => onToggle(item.id, true)}
                className="mt-0.5 h-4 w-4 shrink-0 accent-amber-600"
              />
              <span className="flex-1 text-stone-800 dark:text-stone-300">{item.text}</span>
              <button
                onClick={() => onDelete(item.id)}
                aria-label="Remove"
                className="shrink-0 text-stone-400 hover:text-red-600"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={submit} className="mt-2 flex gap-2">
        <input
          type="text"
          placeholder="Add your own item..."
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          className="flex-1 rounded-lg border border-stone-300 bg-transparent px-2 py-1 text-sm dark:border-stone-700"
        />
        <button
          type="submit"
          disabled={adding || !draft.trim()}
          className="rounded-lg border border-stone-300 px-3 py-1 text-sm font-medium text-stone-700 hover:bg-stone-100 disabled:opacity-50 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
        >
          + Add
        </button>
      </form>
    </div>
  );
}

function GoodToKnowSection({ title, items }) {
  if (items.length === 0) return null;
  return (
    <div className="mt-4 rounded-2xl border border-sky-200 bg-sky-50 p-4 dark:border-sky-900 dark:bg-sky-950/40">
      <h3 className="flex items-center gap-1.5 text-sm font-semibold text-sky-900 dark:text-sky-200">
        <span aria-hidden="true">💡</span>
        {title}
      </h3>
      <ul className="mt-2 space-y-2">
        {items.map((item) => (
          <li key={item.id} className="flex items-start gap-2 text-sm text-sky-950 dark:text-sky-100">
            <span aria-hidden="true" className="mt-0.5 text-sky-400">
              •
            </span>
            <span>
              {item.text}
              {item.link_url && (
                <a
                  href={item.link_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-0.5 block text-xs text-sky-700 hover:underline dark:text-sky-300"
                >
                  {item.link_url} ↗
                </a>
              )}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function PrepItem({ item, t, onToggle }) {
  return (
    <li
      className={`flex items-start gap-2 rounded-lg px-2 py-1 text-sm ${item.is_completed ? "border border-emerald-300 dark:border-emerald-800" : ""}`}
    >
      <input
        type="checkbox"
        checked={item.is_completed}
        onChange={() => onToggle(item.id)}
        className="mt-0.5 h-4 w-4 shrink-0 accent-amber-600"
      />
      <span>
        <span className="text-stone-800 dark:text-stone-300">
          {item.text}{" "}
          <span className="text-xs text-stone-400">
            ({item.is_required ? t("destination.required") : t("destination.optional")})
          </span>
        </span>
        {item.link_url && (
          <a
            href={item.link_url}
            target="_blank"
            rel="noreferrer"
            className="mt-0.5 block text-xs text-amber-700 hover:underline dark:text-amber-400"
          >
            {item.link_url} ↗
          </a>
        )}
      </span>
    </li>
  );
}
