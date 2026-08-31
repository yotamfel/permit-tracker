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
        {["destinations", "monitoring"].map((key) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`pb-2 ${tab === key ? "border-b-2 border-slate-900 font-medium dark:border-slate-100" : "text-slate-500"}`}
          >
            {t(`admin.${key === "destinations" ? "destinations" : "monitoring"}`)}
          </button>
        ))}
      </div>

      {tab === "destinations" ? <DestinationsTab t={t} /> : <MonitoringTab t={t} />}
    </div>
  );
}

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
        {["country", "name", "source_url"].map((field) => (
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
