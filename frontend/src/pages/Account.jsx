import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import CountryPicker from "../components/CountryPicker";

const LEAD_TIME_LABELS = {
  20160: "2 weeks before",
  10080: "1 week before",
  4320: "3 days before",
  1440: "1 day before",
  30: "30 minutes before",
};

function formatSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function Account() {
  const { t } = useTranslation();
  const { user, refreshMe } = useAuth();
  const [purchases, setPurchases] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [editingCountry, setEditingCountry] = useState(false);
  const [countryDraft, setCountryDraft] = useState("");
  const [deleteRequested, setDeleteRequested] = useState(false);
  const [deleteReason, setDeleteReason] = useState("");
  const [showDeleteForm, setShowDeleteForm] = useState(false);

  const loadFiles = () => api.get("/api/me/files").then((res) => setFiles(res.data));
  const loadSubscriptions = () => api.get("/api/subscriptions").then((res) => setSubscriptions(res.data));

  useEffect(() => {
    if (!user) return;
    api.get("/api/me/purchases").then((res) => setPurchases(res.data));
    loadSubscriptions();
    loadFiles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setError("");
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      await api.post("/api/me/files", formData);
      await loadFiles();
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const deleteFile = async (id) => {
    await api.delete(`/api/me/files/${id}`);
    setFiles((cur) => cur.filter((f) => f.id !== id));
  };

  const removeAlert = async (id) => {
    await api.delete(`/api/subscriptions/${id}`);
    setSubscriptions((cur) => cur.filter((s) => s.id !== id));
  };

  const saveCountry = async () => {
    if (!countryDraft) return;
    await api.patch("/api/me", { country: countryDraft });
    await refreshMe();
    setEditingCountry(false);
  };

  const submitDeleteRequest = async (e) => {
    e.preventDefault();
    await api.post("/api/me/delete-account-request", { reason: deleteReason || null });
    setDeleteRequested(true);
  };

  if (!user) return <div className="mx-auto max-w-3xl px-4 py-8">Log in to see your account.</div>;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">{t("account.title")}</h1>
      <p className="mt-1 text-stone-500 dark:text-stone-400">{user.email}</p>

      <div className="mt-2 flex items-center gap-2 text-sm text-stone-600 dark:text-stone-400">
        {editingCountry ? (
          <>
            <div className="w-48">
              <CountryPicker value={countryDraft || user.country || ""} onChange={setCountryDraft} placeholder="Country" />
            </div>
            <button onClick={saveCountry} className="text-xs text-amber-700 underline dark:text-amber-400">
              Save
            </button>
            <button onClick={() => setEditingCountry(false)} className="text-xs text-stone-500 underline">
              Cancel
            </button>
          </>
        ) : (
          <>
            <span>Country: {user.country || "not set"}</span>
            <button
              onClick={() => {
                setCountryDraft(user.country || "");
                setEditingCountry(true);
              }}
              className="text-xs text-amber-700 underline dark:text-amber-400"
            >
              Edit
            </button>
          </>
        )}
      </div>

      <section className="mt-6">
        <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">{t("account.purchases")}</h2>
        {purchases.length === 0 ? (
          <p className="mt-2 text-sm text-stone-500 dark:text-stone-400">{t("account.no_purchases")}</p>
        ) : (
          <ul className="mt-2 space-y-1.5">
            {purchases.map((p) => (
              <li key={p.id} className="flex items-center gap-2">
                <Link to={`/destinations/${p.destination_id}`} className="underline text-stone-800 dark:text-stone-200">
                  {p.destination_name}
                </Link>
                {p.is_active ? (
                  <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
                    Active
                  </span>
                ) : (
                  <span className="rounded-full bg-stone-100 px-2 py-0.5 text-xs font-medium text-stone-600 dark:bg-stone-800 dark:text-stone-400">
                    Cycle ended
                  </span>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-8">
        <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">My alerts</h2>
        {subscriptions.length === 0 ? (
          <p className="mt-2 text-sm text-stone-500 dark:text-stone-400">No alerts set.</p>
        ) : (
          <ul className="mt-2 space-y-1.5">
            {subscriptions.map((s) => (
              <li key={s.id} className="flex items-center gap-2 text-sm">
                <Link to={`/destinations/${s.destination_id}`} className="underline text-stone-800 dark:text-stone-200">
                  {s.destination_name}
                </Link>
                <span className="text-xs text-stone-500 dark:text-stone-400">
                  {LEAD_TIME_LABELS[s.lead_time_minutes] || `${s.lead_time_minutes} min before`}
                  {s.travel_date && ` · travel date ${s.travel_date}`}
                </span>
                <button onClick={() => removeAlert(s.id)} className="text-xs text-red-600 underline">
                  remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-8">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">My files</h2>
          <label className="cursor-pointer rounded-full bg-amber-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-700">
            {uploading ? "Uploading..." : "+ Upload file"}
            <input type="file" accept="image/jpeg,image/png,image/webp,image/heic,application/pdf" onChange={handleUpload} disabled={uploading} className="hidden" />
          </label>
        </div>
        <p className="mt-1 text-xs text-stone-500 dark:text-stone-400">
          Images or PDFs, up to 10MB - passport scans, insurance documents, confirmations, etc. Attach a file to a
          specific checklist item from the destination page, or just keep it here for your own reference.
        </p>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
        {files.length === 0 ? (
          <p className="mt-3 text-sm text-stone-500 dark:text-stone-400">No files uploaded yet.</p>
        ) : (
          <ul className="mt-3 space-y-1.5">
            {files.map((f) => (
              <li key={f.id} className="flex items-center gap-2 text-sm">
                <span aria-hidden="true">{f.content_type === "application/pdf" ? "📄" : "🖼️"}</span>
                <a
                  href={`${api.defaults.baseURL}/api/me/files/${f.id}/download`}
                  target="_blank"
                  rel="noreferrer"
                  className="flex-1 truncate text-amber-700 hover:underline dark:text-amber-400"
                >
                  {f.filename}
                </a>
                <span className="text-xs text-stone-500 dark:text-stone-400">{formatSize(f.size_bytes)}</span>
                <button onClick={() => deleteFile(f.id)} className="text-xs text-red-600 underline">
                  remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-10 border-t border-stone-200 pt-6 dark:border-stone-800">
        {deleteRequested ? (
          <p className="text-sm text-stone-600 dark:text-stone-400">
            Your deletion request was received - we'll process it and follow up by email.
          </p>
        ) : showDeleteForm ? (
          <form onSubmit={submitDeleteRequest} className="max-w-md space-y-2">
            <h2 className="text-sm font-semibold text-stone-900 dark:text-stone-100">Request account deletion</h2>
            <p className="text-xs text-stone-500 dark:text-stone-400">
              We'll review and process this by hand rather than instantly, since purchase records need to be kept for
              accounting - see our{" "}
              <Link to="/privacy" className="text-amber-700 underline dark:text-amber-400">
                Privacy Policy
              </Link>
              .
            </p>
            <textarea
              rows={2}
              placeholder="Reason (optional)"
              value={deleteReason}
              onChange={(e) => setDeleteReason(e.target.value)}
              className="block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1.5 text-sm dark:border-stone-700"
            />
            <div className="flex gap-2">
              <button type="submit" className="rounded-full bg-red-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-red-700">
                Submit request
              </button>
              <button type="button" onClick={() => setShowDeleteForm(false)} className="text-sm text-stone-500 underline">
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <button onClick={() => setShowDeleteForm(true)} className="text-sm text-red-600 underline">
            Request account deletion
          </button>
        )}
      </section>
    </div>
  );
}
