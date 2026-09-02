import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";

function formatSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function Account() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [purchases, setPurchases] = useState([]);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const loadFiles = () => api.get("/api/me/files").then((res) => setFiles(res.data));

  useEffect(() => {
    if (!user) return;
    api.get("/api/me/purchases").then((res) => setPurchases(res.data));
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

  if (!user) return <div className="mx-auto max-w-3xl px-4 py-8">Log in to see your account.</div>;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">{t("account.title")}</h1>
      <p className="mt-1 text-stone-500 dark:text-stone-400">{user.email}</p>

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
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">My files</h2>
          <label className="cursor-pointer rounded-full bg-amber-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-700">
            {uploading ? "Uploading..." : "+ Upload file"}
            <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/webp,image/heic,application/pdf" onChange={handleUpload} disabled={uploading} className="hidden" />
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
    </div>
  );
}
