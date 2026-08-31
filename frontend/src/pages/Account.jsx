import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";

export default function Account() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [purchases, setPurchases] = useState([]);

  useEffect(() => {
    if (user) api.get("/api/me/purchases").then((res) => setPurchases(res.data));
  }, [user]);

  if (!user) return <div className="mx-auto max-w-3xl px-4 py-8">Log in to see your account.</div>;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">{t("account.title")}</h1>
      <p className="mt-1 text-stone-500">{user.email}</p>

      <section className="mt-6">
        <h2 className="text-lg font-semibold">{t("account.purchases")}</h2>
        {purchases.length === 0 ? (
          <p className="mt-2 text-sm text-stone-500">{t("account.no_purchases")}</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {purchases.map((p) => (
              <li key={p.id}>
                <Link to={`/destinations/${p.destination_id}`} className="underline">
                  {p.destination_name}
                </Link>{" "}
                - ${p.amount_usd}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
