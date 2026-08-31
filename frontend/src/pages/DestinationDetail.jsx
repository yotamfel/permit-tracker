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

  if (!destination) return <div className="mx-auto max-w-3xl px-4 py-8 text-stone-500">...</div>;

  const purchaseStatus = searchParams.get("purchase");
  const needsTravelDate = TRAVEL_DATE_REQUIRED.has(destination.mechanism_type);

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      {purchaseStatus === "success" && !destination.is_owned && (
        <div className="mb-4 rounded-xl bg-amber-100 p-3 text-sm text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
          Payment received - refresh in a few seconds once the webhook processes.
        </div>
      )}

      <span className="text-xs font-medium uppercase tracking-wide text-amber-700 dark:text-amber-400">
        {t(`category.${destination.category}`)}
      </span>
      <h1 className="mt-1 text-3xl font-extrabold text-stone-900 dark:text-stone-50">{destination.name}</h1>
      <p className="text-stone-500 dark:text-stone-400">{destination.country}</p>

      {destination.description && <p className="mt-4 text-stone-700 dark:text-stone-300">{destination.description}</p>}

      <section className="mt-8 rounded-2xl border border-stone-200 bg-stone-50 p-5 dark:border-stone-800 dark:bg-stone-900/50">
        <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">{t("destination.how_it_works")}</h2>
        <p className="mt-1 text-sm font-medium text-amber-700 dark:text-amber-400">
          {t(`mechanism_type.${destination.mechanism_type}`)}
        </p>
        <p className="mt-2 text-stone-700 dark:text-stone-300">{destination.mechanism_explanation}</p>
        {destination.is_owned && destination.mechanism_config && (
          <pre className="mt-3 overflow-x-auto rounded-lg bg-stone-900 p-3 text-xs text-stone-100 dark:bg-black">
            {JSON.stringify(destination.mechanism_config, null, 2)}
          </pre>
        )}
      </section>

      <section className="mt-6">
        <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">{t("destination.checklist")}</h2>
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
          <div className="relative mt-2 rounded-2xl border-2 border-dashed border-stone-300 p-6 dark:border-stone-700">
            <div className="select-none space-y-2 text-stone-400 blur-sm">
              <p>████████ ████ ████████</p>
              <p>████ ████████████</p>
              <p>████████ ████</p>
            </div>
            <p className="mt-4 text-sm text-stone-500 dark:text-stone-400">{t("destination.checklist_locked")}</p>
          </div>
        )}
      </section>

      {destination.is_owned && destination.application_url && (
        <section className="mt-6">
          <a
            href={destination.application_url}
            target="_blank"
            rel="noreferrer"
            className="inline-block rounded-full bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-emerald-700"
          >
            Apply here →
          </a>
        </section>
      )}

      <section className="mt-6 text-sm text-stone-500 dark:text-stone-400">
        <p>
          {t("destination.last_verified")}:{" "}
          {destination.last_verified_at ? new Date(destination.last_verified_at).toLocaleDateString() : t("destination.not_yet_verified")}
        </p>
      </section>

      <section className="mt-8 rounded-2xl border border-stone-200 p-5 dark:border-stone-800">
        {destination.is_owned ? (
          <>
            <p className="font-semibold text-emerald-600 dark:text-emerald-400">✓ {t("destination.already_owned")}</p>
            <form onSubmit={handleSubscribe} className="mt-4 space-y-3">
              <h3 className="font-semibold text-stone-900 dark:text-stone-100">{t("alert.title")}</h3>
              <label className="block text-sm text-stone-700 dark:text-stone-300">
                {t("alert.lead_time")}
                <input
                  type="number"
                  min={0}
                  value={subscription.lead_time_days}
                  onChange={(e) => setSubscription((s) => ({ ...s, lead_time_days: e.target.value }))}
                  className="mt-1 block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1.5 dark:border-stone-700"
                />
              </label>
              {needsTravelDate && (
                <label className="block text-sm text-stone-700 dark:text-stone-300">
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
              {alertMessage && <p className="text-sm text-stone-700 dark:text-stone-300">{alertMessage}</p>}
            </form>
          </>
        ) : (
          <>
            {!user && <p className="mb-3 text-sm text-stone-500 dark:text-stone-400">Log in to unlock this destination.</p>}
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
    </div>
  );
}

function PrepSection({ title, items, t }) {
  if (items.length === 0) return null;
  return (
    <div className="mt-3">
      <h3 className="text-sm font-semibold text-stone-500 dark:text-stone-400">{title}</h3>
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
    <li className="flex items-start gap-2 text-sm text-stone-700 dark:text-stone-300">
      <span className="mt-0.5 text-amber-600 dark:text-amber-400">•</span>
      <span>
        {item.text}{" "}
        <span className="text-xs text-stone-400">
          ({item.is_required ? t("destination.required") : t("destination.optional")})
        </span>
      </span>
    </li>
  );
}
