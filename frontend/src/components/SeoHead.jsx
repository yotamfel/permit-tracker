import { Helmet } from "react-helmet-async";

const SITE_NAME = "SlotScout";

// Per-page title/description/canonical/social-preview tags - without this,
// every page shared the exact same static tags from index.html, so search
// results and shared links for e.g. a specific destination looked identical
// to the homepage. No sitewide fallback image exists yet, so `image` is only
// rendered when a page actually has one (e.g. a destination's real photo) -
// pointing every other page at a fake URL would just 404 in link previews.
export default function SeoHead({ title, description, image, path, jsonLd }) {
  const fullTitle = title ? `${title} - ${SITE_NAME}` : `${SITE_NAME} - Never miss a permit window again`;
  const url = path ? `https://www.myslotscout.com${path}` : undefined;

  return (
    <Helmet>
      <title>{fullTitle}</title>
      {description && <meta name="description" content={description} />}
      {url && <link rel="canonical" href={url} />}
      <meta property="og:type" content="website" />
      <meta property="og:site_name" content={SITE_NAME} />
      <meta property="og:title" content={fullTitle} />
      {description && <meta property="og:description" content={description} />}
      {url && <meta property="og:url" content={url} />}
      {image && <meta property="og:image" content={image} />}
      <meta name="twitter:card" content={image ? "summary_large_image" : "summary"} />
      <meta name="twitter:title" content={fullTitle} />
      {description && <meta name="twitter:description" content={description} />}
      {image && <meta name="twitter:image" content={image} />}
      {jsonLd && <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>}
    </Helmet>
  );
}
