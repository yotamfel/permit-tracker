import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import DestinationCard from "../components/DestinationCard";

export default function Home() {
  const { t, i18n } = useTranslation();
  const [featured, setFeatured] = useState([]);
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Entering the site fresh (no remembered login) goes to login/signup
    // first, per the site's requested flow - a returning, already-logged-in
    // visitor lands straight on this page as before.
    if (!loading && !user) {
      navigate("/login", { replace: true });
    }
  }, [loading, user, navigate]);

  useEffect(() => {
    api
      .get("/api/destinations", { params: { locale: i18n.language } })
      .then((res) => setFeatured(pickFeatured(res.data)));
  }, [i18n.language]);

  if (loading || !user) return null;

  return (
    <div>
      <section className="border-b border-stone-200 bg-gradient-to-b from-amber-50 to-white dark:border-stone-800 dark:from-stone-900 dark:to-stone-950">
        <div className="mx-auto max-w-5xl px-4 py-16 text-center sm:py-24">
          <h1 className="text-4xl font-extrabold tracking-tight text-stone-900 dark:text-stone-50 sm:text-5xl">
            {t("browse.title")}
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-stone-600 dark:text-stone-400">{t("browse.subtitle")}</p>
          <Link
            to="/catalog"
            className="mt-8 inline-block rounded-full bg-amber-600 px-8 py-3 text-base font-semibold text-white shadow-sm transition hover:bg-amber-700"
          >
            View catalog
          </Link>
        </div>
      </section>

      {featured.length > 0 && (
        <section className="mx-auto max-w-5xl px-4 py-14">
          <div className="mb-6 flex items-baseline justify-between">
            <h2 className="text-2xl font-bold text-stone-900 dark:text-stone-100">Popular right now</h2>
            <Link to="/catalog" className="text-sm font-medium text-amber-700 hover:underline dark:text-amber-400">
              See all →
            </Link>
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {featured.map((d) => (
              <DestinationCard key={d.id} d={d} />
            ))}
          </div>
        </section>
      )}

      <section className="border-t border-stone-200 bg-stone-50 dark:border-stone-800 dark:bg-stone-900/50">
        <div className="mx-auto max-w-5xl px-4 py-14">
          <h2 className="text-2xl font-bold text-stone-900 dark:text-stone-100">How it works</h2>
          <div className="mt-6 grid grid-cols-1 gap-8 sm:grid-cols-3">
            <HowStep
              emoji="🔎"
              title="Search destinations"
              text="Find the trek, park, dive, or event you're after and see what it takes to get in, at a glance."
            />
            <HowStep
              emoji="🔓"
              title="Get your game plan"
              text="One quick unlock gives you the exact steps, dates, and documents you need - so you're ready to act the moment applications open."
            />
            <HowStep
              emoji="🔔"
              title="Get notified in time"
              text="Set an alert and we'll email you before the application window opens."
            />
          </div>
        </div>
      </section>
    </div>
  );
}

function HowStep({ emoji, title, text }) {
  return (
    <div>
      <div className="text-3xl" aria-hidden="true">
        {emoji}
      </div>
      <h3 className="mt-3 font-semibold text-stone-900 dark:text-stone-100">{title}</h3>
      <p className="mt-1 text-sm text-stone-600 dark:text-stone-400">{text}</p>
    </div>
  );
}

function pickFeatured(destinations) {
  // A little variety instead of just the alphabetically-first few: prefer
  // higher-competitiveness destinations (the ones people are most likely to
  // search for) and spread across categories rather than piling up one type.
  const seenCategories = new Set();
  const ranked = [...destinations].sort((a, b) => {
    const order = { very_high: 0, high: 1, medium: 2, low: 3 };
    return (order[a.competitiveness_level] ?? 4) - (order[b.competitiveness_level] ?? 4);
  });

  const picked = [];
  for (const d of ranked) {
    if (picked.length >= 6) break;
    if (seenCategories.has(d.category)) continue;
    seenCategories.add(d.category);
    picked.push(d);
  }
  if (picked.length < 6) {
    for (const d of ranked) {
      if (picked.length >= 6) break;
      if (!picked.includes(d)) picked.push(d);
    }
  }
  return picked;
}
