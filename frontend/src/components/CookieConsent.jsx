import { useState } from "react";
import { Link } from "react-router-dom";
import { CONSENT_KEY, initAnalytics } from "../lib/analytics";

function getStoredChoice() {
  try {
    return localStorage.getItem(CONSENT_KEY);
  } catch {
    return "declined"; // localStorage unavailable (e.g. private mode) - default to no tracking
  }
}

export default function CookieConsent() {
  const [choice, setChoice] = useState(getStoredChoice);

  if (choice) return null;

  const decide = (value) => {
    try {
      localStorage.setItem(CONSENT_KEY, value);
    } catch {
      // Nothing we can do if storage is unavailable - just don't load analytics.
    }
    setChoice(value);
    if (value === "accepted") initAnalytics();
  };

  return (
    <div className="fixed inset-x-0 bottom-0 z-50 border-t border-stone-200 bg-white/95 px-4 py-3 backdrop-blur dark:border-stone-800 dark:bg-stone-950/95">
      <div className="mx-auto flex max-w-5xl flex-col items-center gap-3 sm:flex-row sm:justify-between">
        <p className="text-sm text-stone-600 dark:text-stone-400">
          We use analytics cookies to understand how the site is used. See our{" "}
          <Link to="/privacy" className="text-amber-700 underline dark:text-amber-400">
            Privacy Policy
          </Link>
          .
        </p>
        <div className="flex shrink-0 gap-2">
          <button
            onClick={() => decide("declined")}
            className="rounded-full border border-stone-300 px-4 py-1.5 text-sm font-medium text-stone-700 hover:bg-stone-100 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
          >
            Decline
          </button>
          <button
            onClick={() => decide("accepted")}
            className="rounded-full bg-amber-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-amber-700"
          >
            Accept
          </button>
        </div>
      </div>
    </div>
  );
}
