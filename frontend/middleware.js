import { next } from "@vercel/functions";

// Social-preview crawlers (Facebook, WhatsApp, Twitter/X, Slack, LinkedIn,
// Telegram, Discord, etc.) don't execute JavaScript, so they never see the
// per-page tags react-helmet-async sets client-side (see SeoHead.jsx) - they
// only ever see the raw HTML Vercel serves. This middleware detects exactly
// those bots and serves them a small dedicated HTML page with the right
// title/description/image for the requested path (including a real photo
// for a specific destination). Everyone else (real visitors, and Google -
// which does execute JS) passes straight through to the normal SPA,
// completely unaffected.
const BOT_UA_PATTERN =
  /facebookexternalhit|Facebot|Twitterbot|WhatsApp|Slackbot|LinkedInBot|TelegramBot|Discordbot|Pinterest|SkypeUriPreview|vkShare|redditbot|Applebot/i;

const API_BASE = "https://permit-tracker-production-d4cf.up.railway.app";
const SITE = "https://www.myslotscout.com";

export const config = {
  matcher: ["/", "/catalog", "/destinations/:path*"],
};

function escapeHtml(str) {
  return String(str).replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
  );
}

function renderHtml({ title, description, image, url }) {
  const safeTitle = escapeHtml(title);
  const safeDesc = description ? escapeHtml(description) : "";
  return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>${safeTitle}</title>
${description ? `<meta name="description" content="${safeDesc}">` : ""}
<meta property="og:type" content="website">
<meta property="og:site_name" content="SlotScout">
<meta property="og:title" content="${safeTitle}">
${description ? `<meta property="og:description" content="${safeDesc}">` : ""}
<meta property="og:url" content="${escapeHtml(url)}">
${image ? `<meta property="og:image" content="${escapeHtml(image)}">` : ""}
<meta name="twitter:card" content="${image ? "summary_large_image" : "summary"}">
<meta name="twitter:title" content="${safeTitle}">
${description ? `<meta name="twitter:description" content="${safeDesc}">` : ""}
${image ? `<meta name="twitter:image" content="${escapeHtml(image)}">` : ""}
</head>
<body></body>
</html>`;
}

function htmlResponse(html) {
  return new Response(html, { headers: { "content-type": "text/html; charset=utf-8" } });
}

export default async function middleware(request) {
  const ua = request.headers.get("user-agent") || "";
  if (!BOT_UA_PATTERN.test(ua)) return next();

  const path = new URL(request.url).pathname;

  if (path === "/") {
    return htmlResponse(
      renderHtml({
        title: "SlotScout - Never miss a permit window again",
        description:
          "Track application windows, quotas, and lotteries for permits that sell out fast - Aconcagua, Torres del Paine, national park entries, and more. Get the exact prep checklist and an alert before the window opens.",
        url: `${SITE}/`,
      })
    );
  }

  if (path === "/catalog") {
    return htmlResponse(
      renderHtml({
        title: "Browse Permits, Quotas & Lotteries Worldwide - SlotScout",
        description:
          "Browse every hard-to-get permit, quota, and lottery SlotScout tracks worldwide - treks, national parks, camping, diving, safaris, and seasonal nature events.",
        url: `${SITE}/catalog`,
      })
    );
  }

  const match = path.match(/^\/destinations\/([^/]+)\/?$/);
  if (match) {
    const id = match[1];
    try {
      const res = await fetch(`${API_BASE}/api/destinations/${id}`);
      if (res.ok) {
        const d = await res.json();
        return htmlResponse(
          renderHtml({
            title: `${d.name} Permit & Application Guide - SlotScout`,
            description:
              d.description ||
              `Everything you need to prepare for ${d.name} (${d.country}) - application checklist, key dates, and alerts before the window opens.`,
            image: d.image_url,
            url: `${SITE}/destinations/${id}`,
          })
        );
      }
    } catch {
      // Fetch failed - fall through to the normal SPA below rather than erroring.
    }
  }

  return next();
}
