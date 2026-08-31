import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../lib/api";
import { formatMechanismConfig } from "../lib/mechanismConfig";
import { COMPETITIVENESS_INFO } from "../components/CompetitivenessNote";

const CATEGORIES = [
  "trek", "national_park_entry", "camping", "diving", "wildlife_safari",
  "thru_hike", "tourist_attraction", "seasonal_nature_event",
];
const MECHANISMS = [
  "fixed_daily_quota", "lottery", "rolling_window", "fixed_annual_date",
  "weekly_release", "guided_tour_only", "single_operator_annual_quota", "first_come_first_served",
];
const ISSUERS = ["government", "tribal", "commercial", "mixed"];
const COMPETITIVENESS = ["low", "medium", "high", "very_high"];
const ITEM_TYPES = ["document", "action", "gear", "payment"];

export default function AdminDestinationEdit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState(null);
  const [checklistItems, setChecklistItems] = useState([]);
  const [newItemText, setNewItemText] = useState("");
  const [newItemType, setNewItemType] = useState("document");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const load = useCallback(() => {
    api.get(`/admin/api/destinations/${id}`).then((res) =>
      setForm({ ...res.data, mechanism_config: JSON.stringify(res.data.mechanism_config, null, 2) })
    );
    api.get("/admin/api/checklist-items", { params: { destination_id: id } }).then((res) => setChecklistItems(res.data));
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  const set = (field, value) => setForm((f) => ({ ...f, [field]: value }));

  const buildPayload = () => {
    let mechanism_config;
    try {
      mechanism_config = JSON.parse(form.mechanism_config);
    } catch {
      throw new Error("mechanism_config must be valid JSON");
    }
    return { ...form, mechanism_config, price_usd: Number(form.price_usd) };
  };

  const save = async () => {
    setError("");
    setSaving(true);
    try {
      const payload = buildPayload();
      await api.put(`/admin/api/destinations/${id}`, payload);
      load();
    } catch (e) {
      setError(e.message || JSON.stringify(e.response?.data?.detail) || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const approveAndPublish = async () => {
    setError("");
    setSaving(true);
    try {
      const payload = { ...buildPayload(), is_published: true };
      await api.post(`/admin/api/review-queue/${id}/approve`, payload);
      navigate("/admin");
    } catch (e) {
      setError(e.message || JSON.stringify(e.response?.data?.detail) || "Approve failed");
    } finally {
      setSaving(false);
    }
  };

  const unpublish = async () => {
    setError("");
    try {
      await api.put(`/admin/api/destinations/${id}`, { ...buildPayload(), is_published: false });
      load();
    } catch (e) {
      setError(e.message || "Failed to unpublish");
    }
  };

  const discard = async () => {
    await api.delete(`/admin/api/destinations/${id}`);
    navigate("/admin");
  };

  const updateChecklistItem = async (itemId, patch) => {
    const item = checklistItems.find((i) => i.id === itemId);
    await api.put(`/admin/api/checklist-items/${itemId}`, { ...item, ...patch, destination_id: id });
    load();
  };

  const deleteChecklistItem = async (itemId) => {
    await api.delete(`/admin/api/checklist-items/${itemId}`);
    load();
  };

  const addChecklistItem = async () => {
    if (!newItemText.trim()) return;
    await api.post("/admin/api/checklist-items", {
      destination_id: id,
      item_type: newItemType,
      order_index: checklistItems.length,
      is_required: true,
      text_key: newItemText,
    });
    setNewItemText("");
    load();
  };

  if (!form) return <div className="mx-auto max-w-3xl px-4 py-8 text-stone-500">...</div>;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <Link
        to="/admin"
        className="mb-4 flex w-fit items-center gap-1 text-sm text-stone-500 hover:text-amber-700 dark:text-stone-400 dark:hover:text-amber-400"
      >
        ← Back to admin
      </Link>

      <div className="mb-4 flex items-center justify-between">
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
            form.is_published
              ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300"
              : "bg-stone-200 text-stone-700 dark:bg-stone-800 dark:text-stone-300"
          }`}
        >
          {form.is_published ? "Published (live)" : "Not published yet"}
        </span>
      </div>

      {/* Sources - admin only, never shown on the public page */}
      <div className="mb-4 rounded-xl bg-stone-100 p-3 text-xs dark:bg-stone-800">
        <label className="block font-semibold text-stone-500 dark:text-stone-400">
          Primary source URL (admin-only - the weekly monitoring job re-fetches this one URL to detect changes)
        </label>
        <input
          value={form.source_url ?? ""}
          onChange={(e) => set("source_url", e.target.value)}
          placeholder="https://..."
          className="mt-1 block w-full rounded border border-stone-300 bg-white px-2 py-1 dark:border-stone-700 dark:bg-stone-900"
        />
        <label className="mt-3 block font-semibold text-stone-500 dark:text-stone-400">
          All sources consulted (admin-only, one per line)
        </label>
        <textarea
          rows={4}
          value={form.research_notes ?? ""}
          onChange={(e) => set("research_notes", e.target.value)}
          placeholder={"https://...\nhttps://...\nnotes on anything else consulted"}
          className="mt-1 block w-full rounded border border-stone-300 bg-white px-2 py-1 font-mono dark:border-stone-700 dark:bg-stone-900"
        />
      </div>

      <div className="flex gap-2">
        <select
          value={form.category}
          onChange={(e) => set("category", e.target.value)}
          className="rounded-lg border border-stone-300 bg-transparent px-2 py-1 text-xs font-medium uppercase tracking-wide text-amber-700 dark:border-stone-700 dark:text-amber-400"
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>
      <input
        value={form.name}
        onChange={(e) => set("name", e.target.value)}
        className="mt-1 block w-full rounded-lg border border-stone-300 bg-transparent text-3xl font-extrabold text-stone-900 dark:border-stone-700 dark:text-stone-50"
      />
      <input
        value={form.country}
        onChange={(e) => set("country", e.target.value)}
        className="mt-1 block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1 text-stone-500 dark:border-stone-700 dark:text-stone-400"
      />

      <textarea
        rows={3}
        value={form.description ?? ""}
        onChange={(e) => set("description", e.target.value)}
        placeholder="Description shown to everyone, before unlock"
        className="mt-4 block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1 text-stone-700 dark:border-stone-700 dark:text-stone-300"
      />

      <div className="mt-4 flex items-center gap-2 text-sm">
        <select
          value={form.competitiveness_level}
          onChange={(e) => set("competitiveness_level", e.target.value)}
          className="rounded-full border border-stone-300 bg-transparent px-2 py-0.5 text-xs font-medium dark:border-stone-700"
        >
          {COMPETITIVENESS.map((c) => (
            <option key={c} value={c}>
              {COMPETITIVENESS_INFO[c].label}
            </option>
          ))}
        </select>
      </div>

      <section className="mt-8 rounded-2xl border border-stone-200 bg-stone-50 p-5 dark:border-stone-800 dark:bg-stone-900/50">
        <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">How it works</h2>
        <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
          <label className="text-stone-500 dark:text-stone-400">
            Mechanism type
            <select
              value={form.mechanism_type}
              onChange={(e) => set("mechanism_type", e.target.value)}
              className="mt-1 block w-full rounded border border-stone-300 bg-white px-2 py-1 dark:border-stone-700 dark:bg-stone-900"
            >
              {MECHANISMS.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </label>
          <label className="text-stone-500 dark:text-stone-400">
            Issuing authority
            <select
              value={form.issuing_authority}
              onChange={(e) => set("issuing_authority", e.target.value)}
              className="mt-1 block w-full rounded border border-stone-300 bg-white px-2 py-1 dark:border-stone-700 dark:bg-stone-900"
            >
              {ISSUERS.map((i) => (
                <option key={i} value={i}>
                  {i}
                </option>
              ))}
            </select>
          </label>
        </div>
        <textarea
          rows={2}
          value={form.mechanism_explanation ?? ""}
          onChange={(e) => set("mechanism_explanation", e.target.value)}
          placeholder="How it works, in plain language"
          className="mt-2 block w-full rounded-lg border border-stone-300 bg-white px-2 py-1 text-sm text-stone-700 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-300"
        />
        <label className="mt-2 block text-xs text-stone-500 dark:text-stone-400">
          mechanism_config (JSON - see PROJECT_SPEC.md §5 for the shape per type)
          <textarea
            rows={5}
            value={form.mechanism_config}
            onChange={(e) => set("mechanism_config", e.target.value)}
            className="mt-1 block w-full rounded-lg border border-stone-300 bg-white px-2 py-1 font-mono text-xs dark:border-stone-700 dark:bg-stone-900"
          />
        </label>
        <p className="mt-2 rounded-lg bg-white p-3 text-sm text-stone-700 dark:bg-stone-800 dark:text-stone-300">
          Preview:{" "}
          {(() => {
            try {
              return formatMechanismConfig(form.mechanism_type, JSON.parse(form.mechanism_config));
            } catch {
              return <span className="text-red-600">invalid JSON</span>;
            }
          })()}
        </p>
      </section>

      <section className="mt-6">
        <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">Prepare for your trip</h2>
        <p className="mt-1 text-xs text-stone-500 dark:text-stone-400">
          "Documents &amp; Bureaucracy" (general requirements like passport/insurance) aren't editable here yet -
          manage those via /docs if needed. Editing "Specific to this permit" below.
        </p>
        <ul className="mt-2 space-y-2">
          {checklistItems.map((item) => (
            <li key={item.id} className="flex items-center gap-2 text-sm">
              <select
                value={item.item_type}
                onChange={(e) => updateChecklistItem(item.id, { item_type: e.target.value })}
                className="rounded border border-stone-300 bg-transparent px-1 py-0.5 text-xs dark:border-stone-700"
              >
                {ITEM_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
              <input
                value={item.text_key}
                onChange={(e) => updateChecklistItem(item.id, { text_key: e.target.value })}
                className="flex-1 rounded border border-stone-300 bg-transparent px-2 py-1 dark:border-stone-700"
              />
              <label className="flex items-center gap-1 text-xs text-stone-500 dark:text-stone-400">
                <input
                  type="checkbox"
                  checked={item.is_required}
                  onChange={(e) => updateChecklistItem(item.id, { is_required: e.target.checked })}
                />
                required
              </label>
              <button onClick={() => deleteChecklistItem(item.id)} className="text-xs text-red-600 underline">
                remove
              </button>
            </li>
          ))}
        </ul>
        <div className="mt-2 flex items-center gap-2 text-sm">
          <select
            value={newItemType}
            onChange={(e) => setNewItemType(e.target.value)}
            className="rounded border border-stone-300 bg-transparent px-1 py-0.5 text-xs dark:border-stone-700"
          >
            {ITEM_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <input
            placeholder="e.g. Valid passport (6+ months)"
            value={newItemText}
            onChange={(e) => setNewItemText(e.target.value)}
            className="flex-1 rounded border border-stone-300 bg-transparent px-2 py-1 dark:border-stone-700"
          />
          <button onClick={addChecklistItem} className="rounded bg-stone-700 px-3 py-1 text-xs text-white">
            + add
          </button>
        </div>
      </section>

      <section className="mt-6">
        <label className="block text-sm font-semibold text-stone-900 dark:text-stone-100">
          Apply URL (shown to users as "Continue to the official application site" once unlocked)
        </label>
        <input
          value={form.application_url ?? ""}
          onChange={(e) => set("application_url", e.target.value)}
          placeholder="https://..."
          className="mt-1 block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1 text-sm dark:border-stone-700"
        />
      </section>

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      <section className="mt-8 flex flex-wrap gap-2 rounded-2xl border border-stone-200 p-5 dark:border-stone-800">
        {!form.is_published ? (
          <button
            onClick={approveAndPublish}
            disabled={saving}
            className="rounded-full bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
          >
            Approve &amp; Publish
          </button>
        ) : (
          <button
            onClick={unpublish}
            className="rounded-full bg-stone-500 px-6 py-2.5 text-sm font-semibold text-white hover:bg-stone-600"
          >
            Unpublish
          </button>
        )}
        <button
          onClick={save}
          disabled={saving}
          className="rounded-full border border-stone-300 px-6 py-2.5 text-sm font-semibold text-stone-700 hover:bg-stone-100 disabled:opacity-50 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
        >
          Save without publishing
        </button>
        <button onClick={discard} className="rounded-full bg-red-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-red-700">
          Discard
        </button>
      </section>
    </div>
  );
}
