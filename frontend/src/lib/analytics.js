// Google Analytics (GA4) - only loads if VITE_GA_MEASUREMENT_ID is set (so
// local dev and any deploy without the env var configured never sends data)
// AND the visitor has accepted the cookie consent banner (see
// components/CookieConsent.jsx) - GA sets cookies, so it must not load
// before consent, not just be disclosed after the fact.
export const CONSENT_KEY = "cookie_consent"; // "accepted" | "declined"

export function hasAnalyticsConsent() {
  try {
    return localStorage.getItem(CONSENT_KEY) === "accepted";
  } catch {
    return false;
  }
}

export function initAnalytics() {
  const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID;
  if (!measurementId || !hasAnalyticsConsent()) return;
  if (window.gtag) return; // already loaded this session

  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
  document.head.appendChild(script);

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = gtag;
  gtag("js", new Date());
  // send_page_view: false - this is a client-routed SPA, so page views are
  // sent explicitly on every route change (trackPageView) instead of once
  // automatically here, which would miss all in-app navigation.
  gtag("config", measurementId, { send_page_view: false });
}

export function trackPageView(path) {
  if (typeof window.gtag !== "function") return;
  window.gtag("event", "page_view", { page_path: path });
}
