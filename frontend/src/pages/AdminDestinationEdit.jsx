import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../lib/api";
import { formatMechanismConfig } from "../lib/mechanismConfig";
import { COMPETITIVENESS_INFO } from "../components/CompetitivenessNote";
import { MONTH_NAMES } from "../lib/months";

const CATEGORIES = [
  "trek", "national_park_entry", "camping", "diving", "wildlife_safari",
  "thru_hike", "tourist_attraction", "seasonal_nature_event", "endurance_event",
];
const MECHANISMS = [
  "fixed_daily_quota", "lottery", "rolling_window", "fixed_annual_date",
  "weekly_release", "guided_tour_only", "single_operator_annual_quota", "first_come_first_served",
];
const ISSUERS = ["government", "tribal", "commercial", "mixed"];
const COMPETITIVENESS = ["low", "medium", "high", "very_high"];
const ITEM_TYPES = ["document", "action", "gear", "payment"];
const REQUIREMENT_TYPES = ["passport_validity", "visa", "vaccination", "travel_insurance", "fitness_certificate", "other"];

export default function AdminDestinationEdit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState(null);
  const [checklistItems, setChecklistItems] = useState([]);
  const [sources, setSources] = useState([]);
  const [alternatives, setAlternatives] = useState([]);
  const [operators, setOperators] = useState([]);
  const [allDestinations, setAllDestinations] = useState([]);
  const [destRequirements, setDestRequirements] = useState([]);
  const [generalRequirements, setGeneralRequirements] = useState([]);
  const [newAltId, setNewAltId] = useState("");
  const [newAltNote, setNewAltNote] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const load = useCallback(() => {
    api.get(`/admin/api/destinations/${id}`).then((res) =>
      setForm({ ...res.data, mechanism_config: JSON.stringify(res.data.mechanism_config, null, 2) })
    );
    api.get("/admin/api/checklist-items", { params: { destination_id: id } }).then((res) => setChecklistItems(res.data));
    api.get("/admin/api/sources", { params: { destination_id: id } }).then((res) => setSources(res.data));
    api.get("/admin/api/alternatives", { params: { destination_id: id } }).then((res) => setAlternatives(res.data));
    api.get("/admin/api/operators", { params: { destination_id: id } }).then((res) => setOperators(res.data));
    api.get("/admin/api/destinations").then((res) => setAllDestinations(res.data));
    api.get("/admin/api/destination-requirements", { params: { destination_id: id } }).then((res) => setDestRequirements(res.data));
    api.get("/admin/api/general-requirements").then((res) => setGeneralRequirements(res.data));
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
    const warning = form.is_published
      ? `"${form.name}" is LIVE and PUBLISHED right now. Deleting it removes it from the site permanently and cannot be undone. Are you sure?`
      : `Permanently delete "${form.name}"? This cannot be undone.`;
    if (!window.confirm(warning)) return;
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

  const addChecklistItem = async (section, itemType, text) => {
    if (!text.trim()) return;
    await api.post("/admin/api/checklist-items", {
      destination_id: id,
      item_type: itemType,
      section,
      order_index: checklistItems.length,
      is_required: true,
      text_key: text,
    });
    load();
  };

  const updateSource = async (sourceId, patch) => {
    const source = sources.find((s) => s.id === sourceId);
    await api.put(`/admin/api/sources/${sourceId}`, { ...source, ...patch, destination_id: id });
    load();
  };

  const deleteSource = async (sourceId) => {
    await api.delete(`/admin/api/sources/${sourceId}`);
    load();
  };

  const addSource = async () => {
    await api.post("/admin/api/sources", { destination_id: id, order_index: sources.length, url: "", note: "" });
    load();
  };

  const addAlternative = async () => {
    if (!newAltId) return;
    await api.post("/admin/api/alternatives", {
      destination_id: id,
      alternative_destination_id: newAltId,
      order_index: alternatives.length,
      note: newAltNote,
    });
    setNewAltId("");
    setNewAltNote("");
    load();
  };

  const deleteAlternative = async (altId) => {
    await api.delete(`/admin/api/alternatives/${altId}`);
    load();
  };

  const addOperator = async () => {
    await api.post("/admin/api/operators", { destination_id: id, name: "", url: "", note: "", order_index: operators.length });
    load();
  };

  const updateOperator = async (opId, patch) => {
    const op = operators.find((o) => o.id === opId);
    await api.put(`/admin/api/operators/${opId}`, { ...op, ...patch, destination_id: id });
    load();
  };

  const deleteOperator = async (opId) => {
    await api.delete(`/admin/api/operators/${opId}`);
    load();
  };

  const attachRequirement = async (generalRequirementId) => {
    await api.post("/admin/api/destination-requirements", {
      destination_id: id,
      general_requirement_id: generalRequirementId,
      order_index: destRequirements.length,
    });
    load();
  };

  const createAndAttachRequirement = async (title, description, requirementType) => {
    const res = await api.post("/admin/api/general-requirements", {
      requirement_type: requirementType,
      title_key: title,
      description_key: description,
    });
    await attachRequirement(res.data.id);
  };

  const updateRequirement = async (attachmentId, patch) => {
    const dr = destRequirements.find((r) => r.id === attachmentId);
    await api.put(`/admin/api/destination-requirements/${attachmentId}`, {
      destination_id: id,
      general_requirement_id: dr.general_requirement_id,
      order_index: dr.order_index,
      action_url: dr.action_url,
      note: dr.note,
      ...patch,
    });
    load();
  };

  const detachRequirement = async (attachmentId) => {
    await api.delete(`/admin/api/destination-requirements/${attachmentId}`);
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
        {form.source_fetch_failing && (
          <p className="mt-2 rounded bg-amber-100 p-2 text-amber-900 dark:bg-amber-900/40 dark:text-amber-200">
            ⚠ Automated monitoring has been unable to fetch this URL since{" "}
            {form.source_fetch_failing_since ? new Date(form.source_fetch_failing_since).toLocaleDateString() : "?"}
            {form.source_fetch_error ? ` (${form.source_fetch_error})` : ""}. Check it by hand periodically, or fix
            the URL if it's simply wrong.
          </p>
        )}
        <label className="mt-3 block font-semibold text-stone-500 dark:text-stone-400">
          All sources consulted (admin-only)
        </label>
        <ul className="mt-1 space-y-2">
          {sources.map((s, i) => (
            <li key={s.id} className="rounded border border-stone-300 bg-white p-2 dark:border-stone-700 dark:bg-stone-900">
              <div className="flex items-center gap-2">
                <span className="text-stone-400">{i + 1}.</span>
                <input
                  value={s.url ?? ""}
                  onChange={(e) => updateSource(s.id, { url: e.target.value })}
                  placeholder="https://... (optional - not every source is a URL)"
                  className="flex-1 rounded border border-stone-200 bg-transparent px-2 py-1 dark:border-stone-800"
                />
                <button onClick={() => deleteSource(s.id)} className="shrink-0 text-red-600 underline">
                  remove
                </button>
              </div>
              <textarea
                rows={2}
                value={s.note ?? ""}
                onChange={(e) => updateSource(s.id, { note: e.target.value })}
                placeholder="What this source told us / why it's relevant"
                className="mt-1 block w-full rounded border border-stone-200 bg-transparent px-2 py-1 dark:border-stone-800"
              />
            </li>
          ))}
        </ul>
        <button onClick={addSource} className="mt-2 rounded bg-stone-700 px-3 py-1 text-white">
          + add source
        </button>
      </div>

      <div className="flex gap-2">
        <select
          value={form.category}
          onChange={(e) => set("category", e.target.value)}
          className="rounded-lg border border-stone-300 bg-white px-2 py-1 text-xs font-medium uppercase tracking-wide text-amber-700 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
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
          className="rounded-full border border-stone-300 bg-white px-2 py-0.5 text-xs font-medium text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
        >
          {COMPETITIVENESS.map((c) => (
            <option key={c} value={c}>
              {COMPETITIVENESS_INFO[c].label}
            </option>
          ))}
        </select>
      </div>

      <div className="mt-3 flex items-center gap-2 text-xs">
        <span className="text-stone-500 dark:text-stone-400">Season (when it's actually open/happens, not when applications open):</span>
        <select
          value={form.season_start_month ?? ""}
          onChange={(e) => set("season_start_month", e.target.value ? Number(e.target.value) : null)}
          className="rounded border border-stone-300 bg-white px-1 py-0.5 text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
        >
          <option value="">Not set</option>
          {MONTH_NAMES.map((m, i) => (
            <option key={m} value={i + 1}>
              {m}
            </option>
          ))}
        </select>
        <span className="text-stone-400">to</span>
        <select
          value={form.season_end_month ?? ""}
          onChange={(e) => set("season_end_month", e.target.value ? Number(e.target.value) : null)}
          className="rounded border border-stone-300 bg-white px-1 py-0.5 text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
        >
          <option value="">Not set</option>
          {MONTH_NAMES.map((m, i) => (
            <option key={m} value={i + 1}>
              {m}
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
              className="mt-1 block w-full rounded border border-stone-300 bg-white px-2 py-1 text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
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
              className="mt-1 block w-full rounded border border-stone-300 bg-white px-2 py-1 text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
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
        <RequirementsEditor
          requirements={destRequirements}
          allRequirements={generalRequirements}
          onAttach={attachRequirement}
          onCreateAndAttach={createAndAttachRequirement}
          onUpdate={updateRequirement}
          onDetach={detachRequirement}
        />
        <ChecklistGroup
          title="Specific to this permit - required for the application itself"
          items={checklistItems.filter((i) => i.section === "specific")}
          onUpdate={updateChecklistItem}
          onDelete={deleteChecklistItem}
          onAdd={(itemType, text) => addChecklistItem("specific", itemType, text)}
        />
        <ChecklistGroup
          title="Good to know - useful but not required for the application (country-entry rules, safety tips, etc.)"
          items={checklistItems.filter((i) => i.section === "good_to_know")}
          onUpdate={updateChecklistItem}
          onDelete={deleteChecklistItem}
          onAdd={(itemType, text) => addChecklistItem("good_to_know", itemType, text)}
        />
      </section>

      <section className="mt-6">
        <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">
          "If you don't get in" alternatives
        </h2>
        <ul className="mt-2 space-y-1">
          {alternatives.map((alt) => (
            <li key={alt.id} className="flex items-center gap-2 text-sm">
              <span className="flex-1">
                {alt.alternative_destination_name}
                {alt.note && <span className="text-stone-500 dark:text-stone-400"> - {alt.note}</span>}
              </span>
              <button onClick={() => deleteAlternative(alt.id)} className="text-xs text-red-600 underline">
                remove
              </button>
            </li>
          ))}
        </ul>
        <div className="mt-2 flex items-center gap-2 text-sm">
          <select
            value={newAltId}
            onChange={(e) => setNewAltId(e.target.value)}
            className="rounded border border-stone-300 bg-white px-2 py-1 text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
          >
            <option value="">Select destination...</option>
            {allDestinations
              .filter((d) => d.id !== id)
              .map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.country})
                </option>
              ))}
          </select>
          <input
            placeholder="Why it's a good alternative (optional)"
            value={newAltNote}
            onChange={(e) => setNewAltNote(e.target.value)}
            className="flex-1 rounded border border-stone-300 bg-transparent px-2 py-1 dark:border-stone-700"
          />
          <button onClick={addAlternative} className="rounded bg-stone-700 px-3 py-1 text-xs text-white">
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

      <section className="mt-6">
        <label className="block text-sm font-semibold text-stone-900 dark:text-stone-100">
          Operators (shown to owners only when Apply URL above is empty - the neutral fallback for destinations with
          multiple legitimate operators or no online booking at all)
        </label>
        <ul className="mt-2 space-y-2">
          {operators.map((op) => (
            <li key={op.id} className="rounded border border-stone-200 p-2 dark:border-stone-700">
              <div className="flex items-center gap-2 text-sm">
                <input
                  value={op.name}
                  onChange={(e) => updateOperator(op.id, { name: e.target.value })}
                  placeholder="Operator name"
                  className="flex-1 rounded border border-stone-300 bg-transparent px-2 py-1 dark:border-stone-700"
                />
                <button onClick={() => deleteOperator(op.id)} className="text-xs text-red-600 underline">
                  remove
                </button>
              </div>
              <input
                value={op.url ?? ""}
                onChange={(e) => updateOperator(op.id, { url: e.target.value })}
                placeholder="https://... (optional - verified live link only)"
                className="mt-1.5 block w-full rounded border border-stone-200 bg-transparent px-2 py-1 text-xs text-stone-600 dark:border-stone-800 dark:text-stone-400"
              />
              <div className="mt-1.5 flex gap-1.5">
                <input
                  value={op.phone ?? ""}
                  onChange={(e) => updateOperator(op.id, { phone: e.target.value })}
                  placeholder="Phone (optional - verified only)"
                  className="flex-1 rounded border border-stone-200 bg-transparent px-2 py-1 text-xs text-stone-600 dark:border-stone-800 dark:text-stone-400"
                />
                <input
                  value={op.email ?? ""}
                  onChange={(e) => updateOperator(op.id, { email: e.target.value })}
                  placeholder="Email (optional - verified only)"
                  className="flex-1 rounded border border-stone-200 bg-transparent px-2 py-1 text-xs text-stone-600 dark:border-stone-800 dark:text-stone-400"
                />
              </div>
              <input
                value={op.note ?? ""}
                onChange={(e) => updateOperator(op.id, { note: e.target.value })}
                placeholder="Note (optional)"
                className="mt-1.5 block w-full rounded border border-stone-200 bg-transparent px-2 py-1 text-xs text-stone-600 dark:border-stone-800 dark:text-stone-400"
              />
            </li>
          ))}
        </ul>
        <button onClick={addOperator} className="mt-2 rounded bg-stone-700 px-3 py-1 text-xs text-white">
          + add operator
        </button>
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

function RequirementsEditor({ requirements, allRequirements, onAttach, onCreateAndAttach, onUpdate, onDetach }) {
  const [pickerValue, setPickerValue] = useState("");
  const [showNewForm, setShowNewForm] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [newType, setNewType] = useState("other");

  const attachedIds = new Set(requirements.map((r) => r.general_requirement_id));
  const available = allRequirements.filter((g) => !attachedIds.has(g.id));

  const handlePickerChange = (value) => {
    if (value === "__new__") {
      setShowNewForm(true);
      setPickerValue("");
      return;
    }
    setPickerValue("");
    if (value) onAttach(value);
  };

  const handleCreateSubmit = () => {
    if (!newTitle.trim()) return;
    onCreateAndAttach(newTitle, newDescription, newType);
    setNewTitle("");
    setNewDescription("");
    setNewType("other");
    setShowNewForm(false);
  };

  return (
    <div className="mb-4">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-stone-500 dark:text-stone-400">
        Documents & Bureaucracy (general requirements)
      </h3>
      <ul className="mt-2 space-y-2">
        {requirements.map((r) => (
          <li key={r.id} className="rounded border border-stone-200 p-2 dark:border-stone-700">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-stone-800 dark:text-stone-200">{r.general_requirement_title}</span>
              <button onClick={() => onDetach(r.id)} className="text-xs text-red-600 underline">
                remove
              </button>
            </div>
            <input
              value={r.note ?? ""}
              onChange={(e) => onUpdate(r.id, { note: e.target.value })}
              placeholder="Destination-specific note (optional)"
              className="mt-1.5 block w-full rounded border border-stone-200 bg-transparent px-2 py-1 text-xs text-stone-600 dark:border-stone-800 dark:text-stone-400"
            />
            <input
              value={r.action_url ?? ""}
              onChange={(e) => onUpdate(r.id, { action_url: e.target.value })}
              placeholder="Link for this requirement (optional, e.g. a visa application form)"
              className="mt-1.5 block w-full rounded border border-stone-200 bg-transparent px-2 py-1 text-xs text-stone-600 dark:border-stone-800 dark:text-stone-400"
            />
          </li>
        ))}
      </ul>

      <div className="mt-2 flex items-center gap-2 text-sm">
        <select
          value={pickerValue}
          onChange={(e) => handlePickerChange(e.target.value)}
          className="rounded border border-stone-300 bg-white px-2 py-1 text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
        >
          <option value="">Attach an existing requirement...</option>
          {available.map((g) => (
            <option key={g.id} value={g.id}>
              {g.title_key}
            </option>
          ))}
          <option value="__new__">+ Create new requirement...</option>
        </select>
      </div>

      {showNewForm && (
        <div className="mt-2 space-y-2 rounded border border-stone-200 p-2 dark:border-stone-700">
          <select
            value={newType}
            onChange={(e) => setNewType(e.target.value)}
            className="rounded border border-stone-300 bg-white px-2 py-1 text-xs text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
          >
            {REQUIREMENT_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <input
            placeholder="Title (e.g. Yellow fever vaccination certificate)"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            className="block w-full rounded border border-stone-300 bg-transparent px-2 py-1 text-xs dark:border-stone-700"
          />
          <textarea
            placeholder="Description shown to users"
            rows={2}
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
            className="block w-full rounded border border-stone-300 bg-transparent px-2 py-1 text-xs dark:border-stone-700"
          />
          <div className="flex gap-2">
            <button onClick={handleCreateSubmit} className="rounded bg-stone-700 px-3 py-1 text-xs text-white">
              Create &amp; attach
            </button>
            <button onClick={() => setShowNewForm(false)} className="rounded border border-stone-300 px-3 py-1 text-xs dark:border-stone-700">
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function ChecklistGroup({ title, items, onUpdate, onDelete, onAdd }) {
  const [newItemText, setNewItemText] = useState("");
  const [newItemType, setNewItemType] = useState("document");

  const handleAdd = () => {
    onAdd(newItemType, newItemText);
    setNewItemText("");
  };

  return (
    <div className="mt-4">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-stone-500 dark:text-stone-400">{title}</h3>
      <ul className="mt-2 space-y-2">
        {items.map((item) => (
          <li key={item.id} className="rounded border border-stone-200 p-2 dark:border-stone-700">
            <div className="flex items-center gap-2 text-sm">
              <select
                value={item.item_type}
                onChange={(e) => onUpdate(item.id, { item_type: e.target.value })}
                className="rounded border border-stone-300 bg-white px-1 py-0.5 text-xs text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
              >
                {ITEM_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
              <input
                value={item.text_key}
                onChange={(e) => onUpdate(item.id, { text_key: e.target.value })}
                className="flex-1 rounded border border-stone-300 bg-transparent px-2 py-1 dark:border-stone-700"
              />
              <label className="flex items-center gap-1 text-xs text-stone-500 dark:text-stone-400">
                <input
                  type="checkbox"
                  checked={item.is_required}
                  onChange={(e) => onUpdate(item.id, { is_required: e.target.checked })}
                />
                required
              </label>
              <button onClick={() => onDelete(item.id)} className="text-xs text-red-600 underline">
                remove
              </button>
            </div>
            <input
              value={item.link_url ?? ""}
              onChange={(e) => onUpdate(item.id, { link_url: e.target.value })}
              placeholder="Optional link shown under this item (e.g. a form, operator directory, insurance provider)"
              className="mt-1.5 block w-full rounded border border-stone-200 bg-transparent px-2 py-1 text-xs text-stone-600 dark:border-stone-800 dark:text-stone-400"
            />
          </li>
        ))}
      </ul>
      <div className="mt-2 flex items-center gap-2 text-sm">
        <select
          value={newItemType}
          onChange={(e) => setNewItemType(e.target.value)}
          className="rounded border border-stone-300 bg-white px-1 py-0.5 text-xs text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
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
        <button onClick={handleAdd} className="rounded bg-stone-700 px-3 py-1 text-xs text-white">
          + add
        </button>
      </div>
    </div>
  );
}
