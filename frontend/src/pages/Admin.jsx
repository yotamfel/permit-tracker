import { Fragment, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import AdminFollowUpCalendar from "../components/AdminFollowUpCalendar";

export default function Admin() {
  const { t } = useTranslation();
  const { user, loading } = useAuth();
  const [tab, setTab] = useState("destinations");
  const [forbidden, setForbidden] = useState(false);
  const [destCount, setDestCount] = useState(null);
  const [reviewCount, setReviewCount] = useState(null);

  useEffect(() => {
    if (!user) return;
    api
      .get("/admin/api/destinations")
      .then((res) => setDestCount(res.data.filter((d) => d.is_published).length))
      .catch((e) => {
        if (e.response?.status === 403) setForbidden(true);
      });
    api.get("/admin/api/review-queue").then((res) => setReviewCount(res.data.length));
  }, [user]);

  if (loading) return null;
  if (!user) return <div className="mx-auto max-w-3xl px-4 py-8">Log in as an admin to continue.</div>;
  if (forbidden) return <div className="mx-auto max-w-3xl px-4 py-8">Admin access required for this account.</div>;

  const counts = { destinations: destCount, review: reviewCount };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="text-2xl font-bold">{t("admin.title")}</h1>
      <div className="mt-6 flex flex-col gap-8 md:flex-row">
        <nav className="shrink-0 md:w-48">
          {TAB_GROUPS.map((group) => (
            <div key={group.label} className="mb-5">
              <div className="mb-1 px-2 text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
                {group.label}
              </div>
              <div className="flex flex-row flex-wrap gap-1 md:flex-col md:flex-nowrap">
                {group.tabs.map((key) => {
                  const meta = TABS.find((x) => x.key === key);
                  return (
                    <button
                      key={key}
                      onClick={() => setTab(key)}
                      className={`rounded-lg px-2 py-1.5 text-left text-sm transition ${
                        tab === key
                          ? "bg-slate-900 font-medium text-white dark:bg-slate-100 dark:text-slate-900"
                          : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                      }`}
                    >
                      {meta.label}
                      {counts[key] != null && <span className="ml-1 text-xs opacity-70">({counts[key]})</span>}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="min-w-0 flex-1">
          {tab === "destinations" && <DestinationsTab onCountChange={setDestCount} />}
          {tab === "review" && <ReviewQueueTab onCountChange={setReviewCount} />}
          {tab === "monitoring" && <MonitoringTab t={t} />}
          {tab === "stats" && <StatsTab />}
          {tab === "users" && <UsersTab />}
          {tab === "feedback" && <FeedbackStatsTab />}
          {tab === "inquiries" && <InquiriesTab />}
          {tab === "follow-ups" && (
            <div>
              <p className="mb-4 text-sm text-slate-500 dark:text-slate-300">
                Schedule a reminder to manually re-check something about a destination on a specific date - e.g.
                official prices that only publish in October. Click a marked day to see what's due.
              </p>
              <AdminFollowUpCalendar />
            </div>
          )}
          {tab === "reports" && <ReportsTab />}
        </div>
      </div>
    </div>
  );
}

const TABS = [
  { key: "review", label: "Review Queue" },
  { key: "destinations", label: "Destinations" },
  { key: "monitoring", label: "Monitoring diffs" },
  { key: "stats", label: "Stats" },
  { key: "users", label: "Users" },
  { key: "feedback", label: "Feedback" },
  { key: "inquiries", label: "Inquiries" },
  { key: "follow-ups", label: "Follow-ups" },
  { key: "reports", label: "Reports" },
];

// Grouped for the sidebar nav - purely a presentation grouping, doesn't
// change what any tab does or drops anything that was there before.
const TAB_GROUPS = [
  { label: "Content", tabs: ["destinations", "review", "monitoring"] },
  { label: "Users & access", tabs: ["users", "stats"] },
  { label: "Messages", tabs: ["inquiries", "feedback", "follow-ups"] },
  { label: "Agents", tabs: ["reports"] },
];

const AGENT_TYPE_LABELS = {
  destination_pipeline: "מחקר יעדים (חוקר + בודק)",
  visitor_tester: "בודק חוויית משתמש",
  ux_reviewer: "עיצוב וחוויית משתמש (כלל האתר)",
};

function agentTypeLabel(agentType) {
  return AGENT_TYPE_LABELS[agentType] || agentType;
}

// Prefix match (starts-with), not substring - per explicit admin request: as
// soon as a typed character doesn't match the start of a row, it disappears.
function prefixMatch(text, query) {
  if (!query) return true;
  return (text || "").toLowerCase().startsWith(query.toLowerCase());
}

function SearchBox({ value, onChange, placeholder }) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder || "חיפוש..."}
      dir="rtl"
      className="mb-3 block w-full max-w-xs rounded-lg border border-stone-300 bg-white px-2 py-1.5 text-sm text-stone-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
    />
  );
}

function ReportsTab() {
  const [agentTypes, setAgentTypes] = useState([]);
  const [selectedType, setSelectedType] = useState(null);
  const [reports, setReports] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.get("/admin/api/reports/agent-types").then((res) => {
      setAgentTypes(res.data);
      if (res.data.length > 0) setSelectedType((t) => t ?? res.data[0]);
    });
  }, []);

  const load = () => {
    if (!selectedType) return;
    api.get("/admin/api/reports", { params: { agent_type: selectedType } }).then((res) => setReports(res.data));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedType]);

  const deleteReport = async (id) => {
    await api.delete(`/admin/api/reports/${id}`);
    load();
  };

  const visible = reports.filter((r) => prefixMatch(r.destination_name || r.title || "", search));

  return (
    <div className="mt-6">
      <p className="mb-4 text-sm text-slate-500 dark:text-slate-300">
        דוחות מכל הסוכנים, מרוכזים כאן לפי הסוכן ששלח אותם. בוחרים סוכן כדי לראות רק את הדוחות שלו.
      </p>
      <div className="mb-4 flex flex-wrap gap-2">
        {agentTypes.map((at) => (
          <button
            key={at}
            onClick={() => {
              setSelectedType(at);
              setExpandedId(null);
              setSearch("");
            }}
            className={`rounded-full border px-3 py-1.5 text-sm ${
              selectedType === at
                ? "border-amber-400 bg-amber-50 font-medium text-amber-800 dark:border-amber-700 dark:bg-amber-900/30 dark:text-amber-300"
                : "border-slate-300 text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            }`}
          >
            {agentTypeLabel(at)}
          </button>
        ))}
      </div>
      {agentTypes.length === 0 && <p className="text-sm text-slate-500 dark:text-slate-300">אין עדיין דוחות מאף סוכן.</p>}
      {agentTypes.length > 0 && (
        <>
          <SearchBox value={search} onChange={setSearch} placeholder="חיפוש לפי שם יעד / כותרת..." />
          {visible.length === 0 && <p className="text-sm text-slate-500 dark:text-slate-300">אין דוחות תואמים.</p>}
          <ul className="space-y-2">
            {visible.map((r) => {
              const expanded = expandedId === r.id;
              return (
                <li key={r.id} className="rounded border border-slate-200 dark:border-slate-800">
                  <button
                    onClick={() => setExpandedId(expanded ? null : r.id)}
                    className="flex w-full items-center justify-between p-3 text-left text-sm"
                  >
                    <span>
                      {r.destination_id ? (
                        <Link
                          to={`/admin/destinations/${r.destination_id}`}
                          onClick={(e) => e.stopPropagation()}
                          className="font-medium text-blue-700 underline dark:text-blue-400"
                        >
                          {r.destination_name}
                        </Link>
                      ) : (
                        <span className="font-medium">{r.title || "דוח"}</span>
                      )}{" "}
                      <span className="text-xs text-slate-500 dark:text-slate-300">{new Date(r.created_at).toLocaleString()}</span>
                      {r.escalations && (
                        <span className="ml-2 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
                          דורש הכרעה
                        </span>
                      )}
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-300">{expanded ? "כווץ" : "פתח"}</span>
                  </button>
                  {expanded && (
                    <div className="space-y-3 border-t border-slate-200 p-3 text-sm dark:border-slate-800" dir="rtl">
                      <div>
                        <h4 className="text-xs font-semibold uppercase text-slate-500 dark:text-slate-300">סיכום</h4>
                        <p className="mt-1 whitespace-pre-wrap">{r.summary}</p>
                      </div>
                      {r.secondary_summary && (
                        <div>
                          <h4 className="text-xs font-semibold uppercase text-slate-500 dark:text-slate-300">מה נמצא ותוקן (בדיקה נוספת)</h4>
                          <p className="mt-1 whitespace-pre-wrap">{r.secondary_summary}</p>
                        </div>
                      )}
                      {r.escalations && (
                        <div className="rounded bg-amber-50 p-2 dark:bg-amber-900/20">
                          <h4 className="text-xs font-semibold uppercase text-amber-800 dark:text-amber-300">
                            דברים שהושארו להכרעה שלך
                          </h4>
                          <p className="mt-1 whitespace-pre-wrap">{r.escalations}</p>
                        </div>
                      )}
                      {r.recommendation && (
                        <div className="rounded bg-emerald-50 p-2 dark:bg-emerald-900/20">
                          <h4 className="text-xs font-semibold uppercase text-emerald-800 dark:text-emerald-300">
                            המלצת הסוכנים
                          </h4>
                          <p className="mt-1 whitespace-pre-wrap">{r.recommendation}</p>
                        </div>
                      )}
                      <button onClick={() => deleteReport(r.id)} className="text-xs text-red-600 underline">
                        מחק דוח
                      </button>
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        </>
      )}
    </div>
  );
}

function ResearchReportButton({ reportId }) {
  const [modalReport, setModalReport] = useState(null); // { loading, data }

  if (!reportId) return null;

  const openReport = async () => {
    setModalReport({ loading: true, data: null });
    const res = await api.get(`/admin/api/reports/${reportId}`);
    setModalReport({ loading: false, data: res.data });
  };

  return (
    <>
      <button
        onClick={openReport}
        className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900/40 dark:text-blue-300"
      >
        דוח סוכן
      </button>
      {modalReport && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
          onClick={() => setModalReport(null)}
        >
          <div
            className="max-h-[85vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-white p-5 shadow-xl dark:bg-slate-900"
            onClick={(e) => e.stopPropagation()}
            dir="rtl"
          >
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold">דוח סוכן</h3>
              <button
                onClick={() => setModalReport(null)}
                className="rounded px-2 py-1 text-xs text-slate-500 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                סגור ✕
              </button>
            </div>
            {modalReport.loading ? (
              <p className="text-xs text-slate-500 dark:text-slate-300">טוען...</p>
            ) : (
              <div className="space-y-3 text-sm">
                <div>
                  <h4 className="text-xs font-semibold uppercase text-slate-500 dark:text-slate-300">סיכום</h4>
                  <p className="mt-1 whitespace-pre-wrap">{modalReport.data.summary}</p>
                </div>
                {modalReport.data.secondary_summary && (
                  <div>
                    <h4 className="text-xs font-semibold uppercase text-slate-500 dark:text-slate-300">מה נמצא ותוקן (בדיקה נוספת)</h4>
                    <p className="mt-1 whitespace-pre-wrap">{modalReport.data.secondary_summary}</p>
                  </div>
                )}
                {modalReport.data.escalations && (
                  <div className="rounded bg-amber-50 p-2 dark:bg-amber-900/20">
                    <h4 className="text-xs font-semibold uppercase text-amber-800 dark:text-amber-300">
                      דברים שהושארו להכרעה שלך
                    </h4>
                    <p className="mt-1 whitespace-pre-wrap">{modalReport.data.escalations}</p>
                  </div>
                )}
                {modalReport.data.recommendation && (
                  <div className="rounded bg-emerald-50 p-2 dark:bg-emerald-900/20">
                    <h4 className="text-xs font-semibold uppercase text-emerald-800 dark:text-emerald-300">
                      המלצת הסוכנים
                    </h4>
                    <p className="mt-1 whitespace-pre-wrap">{modalReport.data.recommendation}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

function DestinationsTab({ onCountChange }) {
  const [destinations, setDestinations] = useState([]);

  const load = () =>
    api.get("/admin/api/destinations").then((res) => {
      setDestinations(res.data);
      onCountChange?.(res.data.filter((d) => d.is_published).length);
    });

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (id, name) => {
    if (!window.confirm(`"${name}" is LIVE and PUBLISHED right now. Deleting it removes it from the site permanently and cannot be undone. Are you sure?`)) return;
    await api.delete(`/admin/api/destinations/${id}`);
    load();
  };

  const [search, setSearch] = useState("");
  const published = destinations.filter((d) => d.is_published && prefixMatch(d.name, search));

  return (
    <div className="mt-6">
      <p className="mb-4 text-sm text-slate-500 dark:text-slate-300">
        Published destinations only - unpublished ones are in the Review Queue tab.
      </p>
      <SearchBox value={search} onChange={setSearch} placeholder="חיפוש יעד..." />
      <ul className="space-y-2">
        {published.map((d) => (
          <li key={d.id} className="flex items-center justify-between rounded border border-slate-200 p-2 text-sm dark:border-slate-800">
            <Link to={`/admin/destinations/${d.id}`} className="flex-1">
              <span className="font-medium">{d.name}</span> <span className="text-slate-500 dark:text-slate-300">({d.country})</span>
            </Link>
            <div className="flex items-center gap-2">
              <ResearchReportButton reportId={d.latest_report_id} />
              <Link to={`/admin/destinations/${d.id}`} className="underline">
                edit
              </Link>
              <button onClick={() => handleDelete(d.id, d.name)} className="text-red-600 underline">
                delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function MonitoringTab({ t }) {
  const [diffs, setDiffs] = useState([]);
  const [fetchFailures, setFetchFailures] = useState([]);

  const load = () => {
    api.get("/admin/api/monitoring/diffs").then((res) => setDiffs(res.data));
    api.get("/admin/api/monitoring/fetch-failures").then((res) => setFetchFailures(res.data));
  };

  useEffect(() => {
    load();
  }, []);

  const act = async (id, action) => {
    await api.post(`/admin/api/monitoring/diffs/${id}/${action}`);
    load();
  };

  return (
    <div className="mt-6 space-y-4">
      {fetchFailures.length > 0 && (
        <div className="rounded border border-amber-300 bg-amber-50 p-3 dark:border-amber-800 dark:bg-amber-900/20">
          <h3 className="text-sm font-semibold text-amber-900 dark:text-amber-200">
            Needs manual check ({fetchFailures.length})
          </h3>
          <p className="mt-1 text-xs text-amber-800 dark:text-amber-300">
            Automated monitoring can't reach these sources (blocked, broken, or moved) - you were emailed when
            each one first failed. Worth checking these by hand periodically.
          </p>
          <ul className="mt-2 space-y-2">
            {fetchFailures.map((f) => (
              <li key={f.destination_id} className="text-xs">
                <Link to={`/admin/destinations/${f.destination_id}`} className="font-medium text-amber-900 underline dark:text-amber-100">
                  {f.destination_name}
                </Link>
                <span className="text-amber-700 dark:text-amber-400">
                  {" "}
                  - failing since {f.failing_since ? new Date(f.failing_since).toLocaleDateString() : "?"} ({f.error})
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
      {diffs.length === 0 && <p className="text-sm text-slate-500 dark:text-slate-300">No diffs yet.</p>}
      {diffs.map((d) => (
        <div key={d.id} className="rounded border border-slate-200 p-3 text-sm dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="font-medium">{d.destination_name}</span>
            <span className="text-xs uppercase text-slate-500 dark:text-slate-300">{t(`admin.${d.review_status}`)}</span>
          </div>
          <pre className="mt-2 max-h-40 overflow-y-auto whitespace-pre-wrap rounded bg-slate-100 p-2 text-xs dark:bg-slate-800">
            {d.diff_summary}
          </pre>
    {d.review_status === "pending" && (
            <div className="mt-2 flex gap-2">
              <button onClick={() => act(d.id, "approve")} className="rounded bg-green-600 px-2 py-1 text-xs text-white">
                {t("admin.approve")}
              </button>
              <button onClick={() => act(d.id, "dismiss")} className="rounded bg-slate-500 px-2 py-1 text-xs text-white">
                {t("admin.dismiss")}
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function ReviewQueueTab({ onCountChange }) {
  const [items, setItems] = useState([]);

  const load = () =>
    api.get("/admin/api/review-queue").then((res) => {
      setItems(res.data);
      onCountChange?.(res.data.length);
    });

  useEffect(() => {
    load();
  }, []);

  const [search, setSearch] = useState("");
  const visible = items.filter((item) => prefixMatch(item.name, search));

  return (
    <div className="mt-6">
      <p className="mb-4 text-sm text-slate-500 dark:text-slate-300">
        Everything here is unpublished and invisible on the live site. Click a destination to open it as it
        will appear on the site, with every field editable, then Approve &amp; Publish to send it live, or
        discard it.
      </p>
      <SearchBox value={search} onChange={setSearch} placeholder="חיפוש יעד..." />
      {items.length === 0 && <p className="text-sm text-slate-500 dark:text-slate-300">Nothing pending review.</p>}
      <ul className="space-y-2">
        {visible.map((item) => (
          <li key={item.id} className="rounded border border-slate-200 dark:border-slate-800">
            <div className="flex items-center justify-between p-3 text-sm">
              <Link to={`/admin/destinations/${item.id}`} className="flex-1">
                <span className="font-medium">
                  {item.name} <span className="font-normal text-slate-500 dark:text-slate-300">({item.country})</span>
                </span>
              </Link>
              <div className="flex items-center gap-3">
                <ResearchReportButton reportId={item.latest_report_id} />
                <Link to={`/admin/destinations/${item.id}`} className="text-xs text-slate-500 dark:text-slate-300">
                  review
                </Link>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function UsersTab() {
  const [email, setEmail] = useState("");
  const [purchases, setPurchases] = useState(null);
  const [searched, setSearched] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [untilInput, setUntilInput] = useState("");
  const [noteInput, setNoteInput] = useState("");

  const search = async (e) => {
    e?.preventDefault();
    if (!email.trim()) return;
    const res = await api.get("/admin/api/purchases/lookup", { params: { email: email.trim() } });
    setPurchases(res.data);
    setSearched(true);
  };

  const startEdit = (p) => {
    setEditingId(p.purchase_id);
    setUntilInput(p.admin_override_until ? p.admin_override_until.slice(0, 10) : "");
    setNoteInput(p.admin_override_note || "");
  };

  const saveOverride = async (purchaseId) => {
    // A blank date means "reopen indefinitely" in this form - the backend
    // treats until=null as "no override" (falls back to normal cycle rules),
    // so an empty field is sent as a far-future date instead of null.
    const until = untilInput ? new Date(untilInput).toISOString() : new Date("2100-01-01").toISOString();
    const res = await api.post(`/admin/api/purchases/${purchaseId}/override`, {
      until,
      note: noteInput || null,
    });
    setPurchases((cur) => cur.map((p) => (p.purchase_id === purchaseId ? res.data : p)));
    setEditingId(null);
  };

  const clearOverride = async (purchaseId) => {
    const res = await api.post(`/admin/api/purchases/${purchaseId}/override`, { until: null, note: null });
    setPurchases((cur) => cur.map((p) => (p.purchase_id === purchaseId ? res.data : p)));
    setEditingId(null);
  };

  return (
    <div className="mt-6">
      <p className="mb-4 text-sm text-slate-500 dark:text-slate-300">
        Look up a user's purchases and, if a destination locked again for them by mistake (or any other reason),
        manually reopen it - either until a specific date, or leave the date blank to reopen indefinitely.
      </p>
      <form onSubmit={search} className="flex gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="user@example.com"
          className="w-64 rounded border border-slate-300 bg-transparent px-2 py-1 text-sm dark:border-slate-700"
        />
        <button type="submit" className="rounded bg-slate-700 px-3 py-1 text-xs text-white">
          Search
        </button>
      </form>

      {searched && purchases.length === 0 && (
        <p className="mt-4 text-sm text-slate-500 dark:text-slate-300">No completed purchases found for this email.</p>
      )}

      {purchases && purchases.length > 0 && (
        <table className="mt-4 w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 dark:border-slate-800 dark:text-slate-300">
              <th className="pb-2">Destination</th>
              <th className="pb-2">Purchased</th>
              <th className="pb-2">Status</th>
              <th className="pb-2">Active until</th>
              <th className="pb-2"></th>
            </tr>
          </thead>
          <tbody>
            {purchases.map((p) => (
              <tr key={p.purchase_id} className="border-b border-slate-100 align-top dark:border-slate-900">
                <td className="py-2">{p.destination_name}</td>
                <td className="py-2">{new Date(p.purchased_at).toLocaleDateString()}</td>
                <td className="py-2">
                  {p.currently_active ? (
                    <span className="text-emerald-600 dark:text-emerald-400">Unlocked</span>
                  ) : (
                    <span className="text-red-600 dark:text-red-400">Locked</span>
                  )}
                </td>
                <td className="py-2">
                  {p.active_until
                    ? new Date(p.active_until).getFullYear() >= 2100
                      ? "Indefinite"
                      : new Date(p.active_until).toLocaleDateString()
                    : "-"}
                  {p.admin_override_note && (
                    <div className="text-xs text-slate-500 dark:text-slate-400">Override note: {p.admin_override_note}</div>
                  )}
                </td>
                <td className="py-2">
                  {editingId === p.purchase_id ? (
                    <div className="flex flex-col gap-1">
                      <input
                        type="date"
                        value={untilInput}
                        onChange={(e) => setUntilInput(e.target.value)}
                        className="rounded border border-slate-300 bg-transparent px-1.5 py-0.5 text-xs dark:border-slate-700"
                      />
                      <input
                        value={noteInput}
                        onChange={(e) => setNoteInput(e.target.value)}
                        placeholder="Reason (optional)"
                        className="rounded border border-slate-300 bg-transparent px-1.5 py-0.5 text-xs dark:border-slate-700"
                      />
                      <div className="flex gap-2">
                        <button onClick={() => saveOverride(p.purchase_id)} className="text-xs text-amber-700 underline dark:text-amber-400">
                          Save (blank date = reopen indefinitely)
                        </button>
                        <button onClick={() => setEditingId(null)} className="text-xs text-slate-500 underline">
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex gap-2">
                      <button onClick={() => startEdit(p)} className="text-xs text-amber-700 underline dark:text-amber-400">
                        {p.admin_override_until || (!p.currently_active && p.admin_override_note) ? "Edit override" : "Reopen access"}
                      </button>
                      {(p.admin_override_until || p.admin_override_note) && (
                        <button onClick={() => clearOverride(p.purchase_id)} className="text-xs text-red-600 underline">
                          Clear override
                        </button>
                      )}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function StatsTab() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get("/admin/api/stats/purchases").then((res) => setStats(res.data));
  }, []);

  if (!stats) return null;

  return (
    <div className="mt-6">
      <div className="mb-6 flex gap-8">
        <div>
          <div className="text-2xl font-bold">{stats.total_purchases}</div>
          <div className="text-sm text-slate-500 dark:text-slate-300">Total purchases</div>
        </div>
        <div>
          <div className="text-2xl font-bold">${stats.total_revenue_usd}</div>
          <div className="text-sm text-slate-500 dark:text-slate-300">Total revenue</div>
        </div>
        <div>
          <div className="text-2xl font-bold">{stats.total_accounts}</div>
          <div className="text-sm text-slate-500 dark:text-slate-300">Accounts created</div>
        </div>
        <div>
          <div className="text-2xl font-bold">{stats.accounts_created_last_7_days}</div>
          <div className="text-sm text-slate-500 dark:text-slate-300">New accounts (7 days)</div>
        </div>
      </div>

      {stats.by_destination.length === 0 ? (
        <p className="text-sm text-slate-500 dark:text-slate-300">No purchases yet.</p>
      ) : (
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 dark:text-slate-300 dark:border-slate-800">
              <th className="pb-2">Destination</th>
              <th className="pb-2">Purchases</th>
              <th className="pb-2">Revenue</th>
            </tr>
          </thead>
          <tbody>
            {stats.by_destination.map((row) => (
              <tr key={row.destination_id} className="border-b border-slate-100 dark:border-slate-900">
                <td className="py-2">{row.destination_name}</td>
                <td className="py-2">{row.purchase_count}</td>
                <td className="py-2">${row.revenue_usd}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h2 className="mb-3 mt-8 text-lg font-semibold">Accounts by country</h2>
      {stats.by_country.length === 0 ? (
        <p className="text-sm text-slate-500 dark:text-slate-300">No accounts yet.</p>
      ) : (
        <table className="w-full max-w-sm text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 dark:border-slate-800 dark:text-slate-300">
              <th className="pb-2">Country</th>
              <th className="pb-2">Accounts</th>
            </tr>
          </thead>
          <tbody>
            {stats.by_country.map((row) => (
              <tr key={row.country} className="border-b border-slate-100 dark:border-slate-900">
                <td className="py-2">{row.country}</td>
                <td className="py-2">{row.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function FeedbackStatsTab() {
  const [stats, setStats] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [sortBy, setSortBy] = useState("response_count");

  useEffect(() => {
    api.get("/admin/api/feedback-stats").then((res) => setStats(res.data));
  }, []);

  if (!stats) return null;

  const categories = [...new Set(stats.by_destination.map((r) => r.category))].sort();
  const rows = stats.by_destination
    .filter((r) => categoryFilter === "all" || r.category === categoryFilter)
    .slice()
    .sort((a, b) => (b[sortBy] ?? -1) - (a[sortBy] ?? -1));

  return (
    <div className="mt-6">
      <p className="mb-4 text-sm text-slate-500 dark:text-slate-300">
        Private user responses to the post-release "did you get in / did the site help" follow-up email.
        Never shown to regular users or aggregated anywhere public.
      </p>
      <div className="mb-6 flex gap-8">
        <div>
          <div className="text-2xl font-bold">{stats.total_responses}</div>
          <div className="text-sm text-slate-500 dark:text-slate-300">Total responses</div>
        </div>
        <div>
          <div className="text-2xl font-bold">{stats.overall_succeeded_pct ?? "-"}%</div>
          <div className="text-sm text-slate-500 dark:text-slate-300">Succeeded</div>
        </div>
        <div>
          <div className="text-2xl font-bold">{stats.overall_helpful_pct ?? "-"}%</div>
          <div className="text-sm text-slate-500 dark:text-slate-300">Found site helpful</div>
        </div>
      </div>

      {stats.by_destination.length === 0 ? (
        <p className="text-sm text-slate-500 dark:text-slate-300">No responses yet.</p>
      ) : (
        <>
          <div className="mb-3 flex items-center gap-3 text-sm">
            <label className="flex items-center gap-1">
              Category
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="rounded border border-slate-300 bg-transparent px-1 py-0.5 dark:border-slate-700"
              >
                <option value="all">All</option>
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex items-center gap-1">
              Sort by
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="rounded border border-slate-300 bg-transparent px-1 py-0.5 dark:border-slate-700"
              >
                <option value="response_count">Response count</option>
                <option value="succeeded_pct">Succeeded %</option>
                <option value="helpful_pct">Helpful %</option>
              </select>
            </label>
          </div>
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 dark:text-slate-300 dark:border-slate-800">
                <th className="pb-2">Destination</th>
                <th className="pb-2">Category</th>
                <th className="pb-2">Responses</th>
                <th className="pb-2">Succeeded</th>
                <th className="pb-2">Helpful</th>
                <th className="pb-2">Comments</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.destination_id} className="border-b border-slate-100 align-top dark:border-slate-900">
                  <td className="py-2">{row.destination_name}</td>
                  <td className="py-2 text-xs text-slate-500 dark:text-slate-300">{row.category}</td>
                  <td className="py-2">{row.response_count}</td>
                  <td className="py-2">{row.succeeded_pct ?? "-"}%</td>
                  <td className="py-2">{row.helpful_pct ?? "-"}%</td>
                  <td className="py-2">
                    {row.comments.length === 0 ? (
                      <span className="text-slate-400 dark:text-slate-300">-</span>
                    ) : (
                      <ul className="space-y-1 text-xs text-slate-600 dark:text-slate-300">
                        {row.comments.map((c, i) => (
                          <li key={i}>"{c}"</li>
                        ))}
                      </ul>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}

function InquiriesTab() {
  const [messages, setMessages] = useState([]);
  const [replyDrafts, setReplyDrafts] = useState({});
  const [openReplyId, setOpenReplyId] = useState(null);

  const load = () => api.get("/admin/api/contact-messages").then((res) => setMessages(res.data));

  useEffect(() => {
    load();
  }, []);

  const setStatus = async (id, status) => {
    await api.patch(`/admin/api/contact-messages/${id}`, { status });
    load();
  };

  const sendReply = async (id) => {
    const message = replyDrafts[id];
    if (!message) return;
    await api.post(`/admin/api/contact-messages/${id}/reply`, { message });
    setOpenReplyId(null);
    setReplyDrafts((d) => ({ ...d, [id]: "" }));
    load();
  };

  return (
    <div className="mt-6">
      {messages.length === 0 && <p className="text-sm text-slate-500 dark:text-slate-300">No messages yet.</p>}
      {messages.length > 0 && (
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 dark:text-slate-300 dark:border-slate-800">
              <th className="pb-2 pr-3">From</th>
              <th className="pb-2 pr-3">Message</th>
              <th className="pb-2 pr-3">Received</th>
              <th className="pb-2 pr-3">Status</th>
              <th className="pb-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {messages.map((m) => (
              <Fragment key={m.id}>
                <tr
                  className={`border-b align-top dark:border-slate-900 ${m.destination_id ? "border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-900/10" : "border-slate-100"}`}
                >
                  <td className="py-2 pr-3">
                    <div className="font-medium">{m.name}</div>
                    <div className="text-xs text-slate-500 dark:text-slate-300">{m.email}</div>
                    {m.destination_id && (
                      <Link
                        to={`/admin/destinations/${m.destination_id}`}
                        className="mt-1 inline-block rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900/40 dark:text-amber-300"
                      >
                        דחוף - {m.destination_name}
                      </Link>
                    )}
                  </td>
                  <td className="max-w-sm py-2 pr-3 whitespace-pre-wrap">{m.message}</td>
                  <td className="py-2 pr-3 text-xs text-slate-400 dark:text-slate-300">{new Date(m.created_at).toLocaleString()}</td>
                  <td className="py-2 pr-3 text-xs uppercase text-slate-500 dark:text-slate-300">{m.status}</td>
                  <td className="py-2">
                    <div className="flex flex-wrap gap-2">
                      {m.status !== "read" && (
                        <button onClick={() => setStatus(m.id, "read")} className="rounded bg-slate-500 px-2 py-1 text-xs text-white">
                          Mark read
                        </button>
                      )}
                      {m.status !== "resolved" && (
                        <button onClick={() => setStatus(m.id, "resolved")} className="rounded bg-green-600 px-2 py-1 text-xs text-white">
                          Mark resolved
                        </button>
                      )}
                      <button
                        onClick={() => setOpenReplyId(openReplyId === m.id ? null : m.id)}
                        className="rounded bg-amber-600 px-2 py-1 text-xs text-white"
                      >
                        {m.admin_reply ? "Reply again" : "Reply"}
                      </button>
                    </div>
                  </td>
                </tr>
                {(m.admin_reply || openReplyId === m.id) && (
                  <tr className="border-b border-slate-100 dark:border-slate-900">
                    <td />
                    <td colSpan={4} className="py-2">
                      {m.admin_reply && (
                        <div className="rounded bg-green-50 p-2 text-xs dark:bg-green-900/20">
                          <span className="font-semibold">Your reply</span> ({new Date(m.replied_at).toLocaleString()}):
                          <p className="mt-1 whitespace-pre-wrap">{m.admin_reply}</p>
                        </div>
                      )}
                      {openReplyId === m.id && (
                        <div className="mt-2 space-y-2">
                          <textarea
                            rows={4}
                            placeholder={`Write your reply to ${m.name}...`}
                            value={replyDrafts[m.id] ?? ""}
                            onChange={(e) => setReplyDrafts((d) => ({ ...d, [m.id]: e.target.value }))}
                            className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1 text-sm dark:border-slate-700"
                          />
                          <button
                            onClick={() => sendReply(m.id)}
                            className="rounded bg-amber-600 px-3 py-1.5 text-xs font-medium text-white"
                          >
                            Send email reply
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
