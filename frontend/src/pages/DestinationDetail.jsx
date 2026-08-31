import { useEffect, useState, useCallback } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";

const TRAVEL_DATE_REQUIRED = new Set([
  "guided_tour_only",
  "first_come_first_served",
  "single_operator_annual_quota",
  "fixed_daily_quota",
  "rolling_window",
]);

export default function DestinationDetail() {
  const { id } = useParams();
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [destination, setDestination] = useState(null);
  const [checklist, setChecklist] = useState(null);
  const [error, setError] = useState("");
  const [subscription, setSubscription] = useState({ lead_time_days: 7, travel_date: "" });
  const [alertMessage, setAlertMessage] = useState("");

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
        lead_time_days: Number(subscription.lead_time_days),
        travel_date: subscription.travel_date || null,
      });
      setAlertMessage(t("alert.success"));
    } catch (e) {
      setAlertMessage(e.response?.data?.detail || t("auth.error"));
    }
  };

  if (!destination) return <div className="mx-auto max-w-3xl px-4 py-8">...</div>;

  const purchaseStatus = searchParams.get("purchase");
  const needsTravelDate = TRAVEL_DATE_REQUIRED.has(destination.mechanism_type);

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      {purchaseStatus === "success" && !destination.is_owned && (
        <div className="mb-4 rounded bg-yellow-100 p-3 text-sm text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300">
          Payment received - refresh in a few seconds once the webhook processes.
        </div>
      )}

      <span className="text-xs uppercase tracking-wide text-slate-500">{t(`category.${destination.category}`)}</span>
      <h1 className="text-2xl font-bold">{destination.name}</h1>
      <p className="text-slate-500">{destination.country}</p>

      {destination.description && <p className="mt-4">{destination.description}</p>}

      <section className="mt-6">
        <h2 className="text-lg font-semibold">{t("destination.how_it_works")}</h2>
        <p className="mt-1 text-sm text-slate-500">{t(`mechanism_type.${destination.mechanism_type}`)}</p>
        <p className="mt-2">{destination.mechanism_explanation}</p>
        {destination.is_owned && destination.mechanism_config && (
          <pre className="mt-3 overflow-x-auto rounded bg-slate-100 p-3 text-xs dark:bg-slate-800">
            {JSON.stringify(destination.mechanism_config, null, 2)}
          </pre>
        )}
      </section>

      <section className="mt-6">
        <h2 className="text-lg font-semibold">{t("destination.checklist")}</h2>
        {checklist?.is_owned ? (
          <>
            <PrepSection
              title={t("destination.section_general")}
              items={checklist.items.filter((i) => i.section === "general")}
              t={t}
            />
            <PrepSection
              title={t("destination.section_specific")}
              items={checklist.items.filter((i) => i.section === "specific")}
              t={t}
            />
          </>
        ) : (
          <div className="relative mt-2 rounded border border-dashed border-slate-300 p-6 dark:border-slate-700">
            <div className="select-none space-y-2 blur-sm">
              <p>████████ ████ ████████</p>
              <p>████ ████████████</p>
              <p>████████ ████</p>
            </div>
            <p className="mt-4 text-sm text-slate-500">{t("destination.checklist_locked")}</p>
          </div>
        )}
      </section>

      <section className="mt-6 text-sm text-slate-500">
        {destination.source_url && (
          <p>
            {t("destination.source")}:{" "}
            <a href={destination.source_url} target="_blank" rel="noreferrer" className="underline">
              {destination.source_url}
            </a>
          </p>
        )}
        <p>
          {t("destination.last_verified")}:{" "}
          {destination.last_verified_at ? new Date(destination.last_verified_at).toLocaleDateString() : t("destination.not_yet_verified")}
        </p>
      </section>

      <section className="mt-8 rounded-lg border border-slate-200 p-4 dark:border-slate-800">
        {destination.is_owned ? (
          <>
            <p className="font-medium text-green-600 dark:text-green-400">{t("destination.already_owned")}</p>
            <form onSubmit={handleSubscribe} className="mt-4 space-y-3">
              <h3 className="font-semibold">{t("alert.title")}</h3>
              <label className="block text-sm">
                {t("alert.lead_time")}
                <input
                  type="number"
                  min={0}
                  value={subscription.lead_time_days}
                  onChange={(e) => setSubscription((s) => ({ ...s, lead_time_days: e.target.value }))}
                  className="mt-1 block w-full rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
                />
              </label>
              {needsTravelDate && (
                <label className="block text-sm">
                  {t("alert.travel_date")}
                  <input
                    type="date"
                    required
                    value={subscription.travel_date}
                    onChange={(e) => setSubscription((s) => ({ ...s, travel_date: e.target.value }))}
                    className="mt-1 block w-full rounded border border-slate-300 bg-transparent px-2 py-1 dark:border-slate-700"
                  />
                  <span className="text-xs text-slate-500">{t("alert.travel_date_help")}</span>
                </label>
              )}
              <button type="submit" className="rounded bg-slate-900 px-4 py-2 text-sm text-white dark:bg-slate-100 dark:text-slate-900">
                {t("alert.submit")}
              </button>
              {alertMessage && <p className="text-sm">{alertMessage}</p>}
            </form>
          </>
        ) : (
          <>
            {!user && <p className="mb-3 text-sm text-slate-500">Log in to unlock this destination.</p>}
            <button
              onClick={handleUnlock}
              disabled={!user}
              className="rounded bg-slate-900 px-4 py-2 text-sm text-white disabled:opacity-50 dark:bg-slate-100 dark:text-slate-900"
            >
              {t("destination.unlock_cta", { price: destination.price_usd })}
            </button>
            {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          </>
        )}
      </section>
    </div>
  );
}

function PrepSection({ title, items, t }) {
  if (items.length === 0) return null;
  return (
    <div className="mt-3">
      <h3 className="text-sm font-semibold text-slate-500">{title}</h3>
      <ul className="mt-1 space-y-2">
        {items.map((item) => (
          <PrepItem key={item.id} item={item} t={t} />
        ))}
      </ul>
    </div>
  );
}

function PrepItem({ item, t }) {
  return (
    <li className="flex items-start gap-2 text-sm">
      <span className="mt-0.5 text-slate-400">•</span>
      <span>
        {item.text}{" "}
        <span className="text-xs text-slate-400">
          ({item.is_required ? t("destination.required") : t("destination.optional")})
        </span>
      </span>
    </li>
  );
}
