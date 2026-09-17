import { Link } from "react-router-dom";
import SeoHead from "../components/SeoHead";

export default function Pricing() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <SeoHead
        title="Pricing"
        description="SlotScout pricing: $6.99 to unlock a destination's full checklist and application details, no subscription."
        path="/pricing"
      />
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">Pricing</h1>
      <p className="mt-2 text-stone-700 dark:text-stone-400">
        Browsing the catalog, reading how each destination's permit system works, and setting alerts is free.
        You only pay when you want the full prep checklist for a specific destination.
      </p>

      <div className="mt-8 rounded-2xl border border-stone-200 bg-stone-50 p-6 dark:border-stone-800 dark:bg-stone-900/50">
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-extrabold text-stone-900 dark:text-stone-100">$6.99</span>
          <span className="text-stone-500 dark:text-stone-400">per destination, one-time</span>
        </div>
        <p className="mt-1 text-sm text-stone-500 dark:text-stone-400">
          No subscription, no recurring charge. Unlocking a destination covers its current application cycle
          (the upcoming release, lottery, or travel window) plus a 60-day grace period afterward.
        </p>
        <p className="mt-2 text-sm text-stone-500 dark:text-stone-400">
          For destinations with a fixed release date (a lottery or scheduled release), the 60 days start from
          that date. For destinations that don't have one, it's based on the travel date you set when you
          create an alert - if you don't set one, the 60 days start from your purchase date instead. You can
          set or change that travel date within 7 days of your purchase; after that, contact us to update it.
        </p>

        <h2 className="mt-6 text-sm font-semibold uppercase tracking-wide text-stone-500 dark:text-stone-400">
          What's included
        </h2>
        <ul className="mt-2 list-disc space-y-1 ps-5 text-sm text-stone-800 dark:text-stone-300">
          <li>The full prep checklist - documents, fees, and destination-specific requirements</li>
          <li>A plain-language explanation of exactly how that destination's permit/lottery/quota system works</li>
          <li>Direct links to the official application site</li>
          <li>Calendar export and a downloadable PDF of the checklist</li>
          <li>Email alerts before the application window opens</li>
        </ul>

        <p className="mt-4 text-sm text-stone-500 dark:text-stone-400">
          Have a referral code from a friend? Unlock any destination for <span className="font-medium">$3.99</span>{" "}
          instead.
        </p>
      </div>

      <p className="mt-6 text-sm text-stone-500 dark:text-stone-400">
        Payments are processed by our third-party payment provider - see the{" "}
        <Link to="/terms#refund-policy" className="text-amber-700 underline dark:text-amber-400">
          refund policy
        </Link>{" "}
        in our Terms of Service for details.
      </p>

      <Link
        to="/catalog"
        className="mt-8 inline-block rounded-full bg-amber-700 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-amber-800"
      >
        Browse the catalog
      </Link>
    </div>
  );
}
