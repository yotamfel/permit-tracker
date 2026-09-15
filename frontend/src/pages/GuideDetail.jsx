import { Link, useParams } from "react-router-dom";
import SeoHead from "../components/SeoHead";
import { getGuide, GUIDES_LAST_UPDATED } from "../data/guides";
import NotFound from "./NotFound";

export default function GuideDetail() {
  const { slug } = useParams();
  const guide = getGuide(slug);

  if (!guide) return <NotFound />;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <SeoHead
        title={guide.title}
        description={guide.description}
        path={`/guides/${guide.slug}`}
        jsonLd={{
          "@context": "https://schema.org",
          "@type": "Article",
          headline: guide.title,
          description: guide.description,
          dateModified: GUIDES_LAST_UPDATED,
          publisher: { "@type": "Organization", name: "SlotScout" },
        }}
      />
      <Link to="/guides" className="text-sm text-stone-500 hover:text-amber-700 dark:text-stone-400 dark:hover:text-amber-400">
        ← All guides
      </Link>
      <h1 className="mt-2 text-2xl font-bold text-stone-900 dark:text-stone-100">{guide.title}</h1>

      <div className="mt-6 space-y-6 text-stone-800 dark:text-stone-300">
        {guide.sections.map((s) => (
          <section key={s.heading}>
            <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">{s.heading}</h2>
            <div className="mt-2 space-y-2 text-sm leading-relaxed">
              {s.paragraphs.map((p, i) => (
                <p key={i}>{p}</p>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
