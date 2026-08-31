import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";

const EMPTY_FORM = {
  country: "",
  category: "trek",
  name: "",
  mechanism_type: "fixed_daily_quota",
  mechanism_config: "{}",
  issuing_authority: "government",
  competitiveness_level: "medium",
  source_url: "",
  application_url: "",
  price_usd: 4.99,
  is_published: false,
};

export default function Admin() {
  const { t } = useTranslation();
  const { user, loading } = useAuth();
  const [tab, setTab] = useState("destinations");
  const [forbidden, setForbidden] = useState(false);

  useEffect(() => {
    if (!user) return;
    api.get("/admin/api/destinations").catch((e) => {
      if (e.response?.status === 403) setForbidden(true);
    });
  }, [user]);

  if (loading) return null;
  if (!user) return <div className="mx-auto max-w-3xl px-4 py-8">Log in as an admin to continue.</div>;
  if (forbidden) return <div className="mx-auto max-w-3xl px-4 py-8">Admin access required for this account.</div>;

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-2xl font-bold">{t("admin.title")}</h1>
      <div className="mt-4 flex gap-4 border-b border-slate-200 text-sm dark:border-slate-800">
        {TABS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`pb-2 ${tab === key ? "border-b-2 border-slate-900 font-medium dark:border-slate-100" : "text-slate-500"}`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "destinations" && <DestinationsTab t={t} />}
      {tab === "review" && <ReviewQueueTab />}
      {tab === "monitoring" && <MonitoringTab t={t} />}
      {tab === "stats" && <StatsTab />}
      {tab === "inquiries" && <InquiriesTab />}
    </div>
  );
}

const TABS = [
  { key: "review", label: "Review Queue" },
  { key: "destinations", label: "Destinations" },
  { key: "monitoring", label: "Monitoring diffs" },
  { key: "stats", label: "Stats" },
  { key: "inquiries", label: "Inquiries" },
];

function DestinationsTab({ t }) {
  const [destinations, setDestinations] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  const load = () => api.get("/admin/api/destinations").then((res) => setDestinations(res.data));

  useEffect(() => {
    load();
  }, []);

  const startEdit = (d) => {
    setEditingId(d.id);
    setForm({ ...d, mechanism_config: JSON.stringify(d.mechanism_config, null, 2) });
  };

  const resetForm = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    let parsedConfig;
    try {
      parsedConfig = JSON.parse(form.mechanism_config);
    } catch {
      setError("mechanism_config must be valid JSON");
      return;
    }
    const payload = { ...form, mechanism_config: parsedConfig, price_usd: Number(form.price_usd) };
    try {
      if (editingId) {
        await api.put(`/admin/api/destinations/${editingId}`, payload);
      } else {
        await api.post("/admin/api/destinations", payload);
      }
      resetForm();
      load();
    } catch (e) {
      setError(JSON.stringify(e.response?.data?.detail || "Save failed"));
    }
  };

  const handleDelete = async (id) => {
    await api.delete(`/admin/api/destinations/${id}`);
    load();
  };

  return (
    <div className="mt-6 grid grid-cols-1 gap-8 lg:grid-cols-2">
      <div>
        <ul className="space-y-2">
          {destinations.map((d) => (
            <li key={d.id} className="flex items-center justify-between rounded border border-slate-200 p-2 text-sm dark:border-slate-800">
              <div>
                <span className="font-medium">{d.name}</span>{" "}
                <span className="text-slate-500">
                  ({d.country}) - {d.is_published ? t("admin.published") : t("admin.unpublished")}
                </span>
              </div>
              <div className="flex gap-2">
                <button onClick={() => startEdit(d)} className="underline">
                  edit
                </button>
                <button onClick={() => handleDelete(d.id)} className="text-red-600 underline">
                  delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <form onSubmit={handleSubmit} className="space-y-2 text-sm">
        <h2 className="font-semibold">{editingId ? "Edit destination" : t("admin.create")}</h2>
        {["country", "name", "source_url", "application_url"].map((field) => (
          <input
            key={field}
            placeholder={field}
            value={form[field] ?? ""}
            onChange={(e) => setForm((f) => ({ ...f, [field]: e.target.value }))}
            className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
          />
        ))}
        <input
          type="number"
          step="0.01"
          placeholder="price_usd"
          value={form.price_usd}
          onChange={(e) => setForm((f) => ({ ...f, price_usd: e.target.value }))}
          className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
        />
        <textarea
          rows={6}
          value={form.mechanism_config}
          onChange={(e) => setForm((f) => ({ ...f, mechanism_config: e.target.value }))}
          className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1 font-mono text-xs dark:border-slate-700"
        />
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={form.is_published}
            onChange={(e) => setForm((f) => ({ ...f, is_published: e.target.checked }))}
          />
          {t("admin.published")}
        </label>
        {error && <p className="text-red-600">{error}</p>}
        <div className="flex gap-2">
          <button type="submit" className="rounded bg-slate-900 px-3 py-1.5 text-white dark:bg-slate-100 dark:text-slate-900">
            {t("admin.save")}
          </button>
          {editingId && (
            <button type="button" onClick={resetForm} className="rounded border border-slate-300 px-3 py-1.5 dark:border-slate-700">
              cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

function MonitoringTab({ t }) {
  const [diffs, setDiffs] = useState([]);

  const load = () => api.get("/admin/api/monitoring/diffs").then((res) => setDiffs(res.data));

  useEffect(() => {
    load();
  }, []);

  const act = async (id, action) => {
    await api.post(`/admin/api/monitoring/diffs/${id}/${action}`);
    load();
  };

  return (
    <div className="mt-6 space-y-4">
      {diffs.length === 0 && <p className="text-sm text-slate-500">No diffs yet.</p>}
      {diffs.map((d) => (
        <div key={d.id} className="rounded border border-slate-200 p-3 text-sm dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="font-medium">{d.destination_name}</span>
            <span className="text-xs uppercase text-slate-500">{t(`admin.${d.review_status}`)}</span>
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

function ReviewQueueTab() {
  const [items, setItems] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [forms, setForms] = useState({});
  const [error, setError] = useState("");

  const load = () => api.get("/admin/api/review-queue").then((res) => setItems(res.data));

  useEffect(() => {
    load();
  }, []);

  const toggleExpand = (item) => {
    if (expandedId === item.id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(item.id);
    setForms((f) => ({
      ...f,
      [item.id]: f[item.id] || { ...item, mechanism_config: JSON.stringify(item.mechanism_config, null, 2) },
    }));
  };

  const updateField = (id, field, value) => {
    setForms((f) => ({ ...f, [id]: { ...f[id], [field]: value } }));
  };

  const approve = async (id) => {
    setError("");
    const form = forms[id];
    let parsedConfig;
    try {
      parsedConfig = JSON.parse(form.mechanism_config);
    } catch {
      setError("mechanism_config must be valid JSON");
      return;
    }
    try {
      await api.post(`/admin/api/review-queue/${id}/approve`, {
        ...form,
        mechanism_config: parsedConfig,
        price_usd: Number(form.price_usd),
      });
      setExpandedId(null);
      load();
    } catch (e) {
      setError(JSON.stringify(e.response?.data?.detail || "Approve failed"));
    }
  };

  const discard = async (id) => {
    await api.delete(`/admin/api/destinations/${id}`);
    load();
  };

  return (
    <div className="mt-6">
      <p className="mb-4 text-sm text-slate-500">
        Everything here is unpublished and invisible on the live site. Review the source, edit anything
        wrong, then Approve &amp; Publish to send it live, or discard it.
      </p>
      {items.length === 0 && <p className="text-sm text-slate-500">Nothing pending review.</p>}
      <ul className="space-y-2">
        {items.map((item) => {
          const form = forms[item.id];
          const expanded = expandedId === item.id;
          return (
            <li key={item.id} className="rounded border border-slate-200 dark:border-slate-800">
              <button
                onClick={() => toggleExpand(item)}
                className="flex w-full items-center justify-between p-3 text-left text-sm"
              >
                <span className="font-medium">
                  {item.name} <span className="font-normal text-slate-500">({item.country})</span>
                </span>
                <span className="text-xs text-slate-500">{expanded ? "collapse" : "review"}</span>
              </button>

              {expanded && form && (
                <div className="border-t border-slate-200 p-3 text-sm dark:border-slate-800">
                  {item.source_note && (
                    <div className="mb-3 rounded bg-slate-100 p-2 text-xs dark:bg-slate-800">
                      <span className="font-semibold">Source: </span>
                      {item.source_url ? (
                        <a href={item.source_url} target="_blank" rel="noreferrer" className="underline">
                          {item.source_note}
                        </a>
                      ) : (
                        item.source_note
                      )}
                    </div>
                  )}
                  <div className="space-y-2">
                    {["country", "name", "source_url", "application_url"].map((field) => (
                      <input
                        key={field}
                        placeholder={field}
                        value={form[field] ?? ""}
                        onChange={(e) => updateField(item.id, field, e.target.value)}
                        className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
                      />
                    ))}
                    <div className="grid grid-cols-3 gap-2">
                      <input
                        placeholder="category"
                        value={form.category ?? ""}
                        onChange={(e) => updateField(item.id, "category", e.target.value)}
                        className="rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
                      />
                      <input
                        placeholder="mechanism_type"
                        value={form.mechanism_type ?? ""}
                        onChange={(e) => updateField(item.id, "mechanism_type", e.target.value)}
                        className="rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
                      />
                      <input
                        placeholder="issuing_authority"
                        value={form.issuing_authority ?? ""}
                        onChange={(e) => updateField(item.id, "issuing_authority", e.target.value)}
                        className="rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <input
                        placeholder="competitiveness_level"
                        value={form.competitiveness_level ?? ""}
                        onChange={(e) => updateField(item.id, "competitiveness_level", e.target.value)}
                        className="rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
                      />
                      <input
                        type="number"
                        step="0.01"
                        placeholder="price_usd"
                        value={form.price_usd ?? ""}
                        onChange={(e) => updateField(item.id, "price_usd", e.target.value)}
                        className="rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
                      />
                    </div>
                    <textarea
                      rows={5}
                      value={form.mechanism_config ?? ""}
                      onChange={(e) => updateField(item.id, "mechanism_config", e.target.value)}
                      className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1 font-mono text-xs dark:border-slate-700"
                    />
                  </div>
                  {error && <p className="mt-2 text-red-600">{error}</p>}
                  <div className="mt-3 flex gap-2">
                    <button
                      onClick={() => approve(item.id)}
                      className="rounded bg-green-600 px-3 py-1.5 text-xs font-medium text-white"
                    >
                      Approve &amp; Publish
                    </button>
                    <button
                      onClick={() => discard(item.id)}
                      className="rounded bg-red-600 px-3 py-1.5 text-xs font-medium text-white"
                    >
                      Discard
                    </button>
                  </div>
                </div>
              )}
            </li>
          );
        })}
      </ul>
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
          <div className="text-sm text-slate-500">Total purchases</div>
        </div>
        <div>
          <div className="text-2xl font-bold">${stats.total_revenue_usd}</div>
          <div className="text-sm text-slate-500">Total revenue</div>
        </div>
      </div>

      {stats.by_destination.length === 0 ? (
        <p className="text-sm text-slate-500">No purchases yet.</p>
      ) : (
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-slate-500 dark:border-slate-800">
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
    </div>
  );
}

function InquiriesTab() {
  const [messages, setMessages] = useState([]);

  const load = () => api.get("/admin/api/contact-messages").then((res) => setMessages(res.data));

  useEffect(() => {
    load();
  }, []);

  const setStatus = async (id, status) => {
    await api.patch(`/admin/api/contact-messages/${id}`, { status });
    load();
  };

  return (
    <div className="mt-6 space-y-3">
      {messages.length === 0 && <p className="text-sm text-slate-500">No messages yet.</p>}
      {messages.map((m) => (
        <div key={m.id} className="rounded border border-slate-200 p-3 text-sm dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="font-medium">
              {m.name} <span className="font-normal text-slate-500">({m.email})</span>
            </span>
            <span className="text-xs uppercase text-slate-500">{m.status}</span>
          </div>
          <p className="mt-2 whitespace-pre-wrap">{m.message}</p>
          <p className="mt-1 text-xs text-slate-400">{new Date(m.created_at).toLocaleString()}</p>
          <div className="mt-2 flex gap-2">
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
          </div>
        </div>
      ))}
    </div>
  );
}
