import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import { useOnboarding } from "../lib/OnboardingContext";
import DestinationCard from "../components/DestinationCard";
import ReleaseCalendar from "../components/ReleaseCalendar";
import SeoHead from "../components/SeoHead";
import { pickFeatured } from "../lib/pickFeatured";

export default function Home() {
  const { t, i18n } = useTranslation();
  const [featured, setFeatured] = useState([]);
  const [destinationCount, setDestinationCount] = useState(null);
  const { user, loading } = useAuth();
  const { openIfFirstVisit } = useOnboarding();

  useEffect(() => {
    if (user) {
      openIfFirstVisit();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  useEffect(() => {
    api.get("/api/destinations", { params: { locale: i18n.language } }).then((res) => {
      setFeatured(pickFeatured(res.data, 4));
      setDestinationCount(Math.floor(res.data.length / 10) * 10);
    });
  }, [i18n.language]);

  if (loading) return null;

  return (
    <div>
      <SeoHead
        description="Track application windows, quotas, and lotteries for permits that sell out fast - Aconcagua, Torres del Paine, national park entries, and more. Get the exact prep checklist and an alert before the window opens."
        path="/"
      />
      <section className="border-b border-stone-200 bg-gradient-to-b from-amber-50 to-white dark:border-stone-800 dark:from-stone-900 dark:to-stone-950">
        <div className="mx-auto max-w-5xl px-4 py-16 text-center sm:py-24">
          <div className="mb-6 text-7xl" aria-hidden="true">
            🧭
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight text-stone-900 dark:text-stone-50 sm:text-5xl">
            {t("home.title")}
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-stone-700 dark:text-stone-400">{t("home.subtitle")}</p>
          {destinationCount > 0 && (
            <p className="mx-auto mt-2 max-w-xl text-sm text-stone-500 dark:text-stone-500">
              {t("home.examples", { count: destinationCount })}
            </p>
          )}
          <Link
            to="/catalog"
            className="mt-8 inline-block rounded-full bg-amber-700 px-8 py-3 text-base font-semibold text-white shadow-sm transition hover:bg-amber-800"
          >
            View catalog
          </Link>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-4 py-14">
        <div className="grid grid-cols-1 gap-10 lg:grid-cols-[320px_1fr]">
          <ReleaseCalendar />

          {featured.length > 0 && (
            <div>
              <div className="mb-6 flex items-baseline justify-between">
                <h2 className="text-2xl font-bold text-stone-900 dark:text-stone-100">Popular right now</h2>
                <Link to="/catalog" className="text-sm font-medium text-amber-700 hover:underline dark:text-amber-400">
                  See all →
                </Link>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {featured.map((d) => (
                  <DestinationCard key={d.id} d={d} compact />
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

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
          <p className="mt-8 text-sm text-stone-500 dark:text-stone-400">
            Curious how permit lotteries, quotas, and deposits actually work?{" "}
            <Link to="/guides" className="text-amber-700 underline hover:text-amber-800 dark:text-amber-400 dark:hover:text-amber-300">
              Read our guides →
            </Link>
          </p>
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
      <p className="mt-1 text-sm text-stone-700 dark:text-stone-400">{text}</p>
    </div>
  );
}

