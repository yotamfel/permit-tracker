// Google Analytics (GA4) - only loads if VITE_GA_MEASUREMENT_ID is set, so
// local dev and any deploy without the env var configured never sends data.
// Set the measurement ID (from the GA4 property's Data Streams page, looks
// like "G-XXXXXXXXXX") as VITE_GA_MEASUREMENT_ID in Vercel's env vars.
export function initAnalytics() {
  const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID;
  if (!measurementId) return;

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
  if (!import.meta.env.VITE_GA_MEASUREMENT_ID || typeof window.gtag !== "function") return;
  window.gtag("event", "page_view", { page_path: path });
}
