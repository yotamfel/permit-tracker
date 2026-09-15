import SeoHead from "../components/SeoHead";
import { COMPETITIVENESS_INFO } from "../components/CompetitivenessNote";

export default function Methodology() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <SeoHead
        title="How We Rate Competitiveness"
        description="How SlotScout assigns Low/Medium/High/Very High competitiveness ratings to permits, quotas, and lotteries."
        path="/methodology"
      />
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">How we rate competitiveness</h1>

      <div className="mt-6 space-y-6 text-stone-800 dark:text-stone-300">
        <Section title="What the rating means">
          <p>
            Every destination on SlotScout gets a competitiveness rating - how hard it actually is to get a spot.
            It's not a guarantee for your specific application, but a general sense of what to expect:
          </p>
          <ul className="mt-3 space-y-2">
            {Object.entries(COMPETITIVENESS_INFO).map(([level, info]) => (
              <li key={level} className="flex items-start gap-2">
                <span className={`mt-0.5 shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${info.color}`}>
                  {info.label}
                </span>
                <span>{info.text}</span>
              </li>
            ))}
          </ul>
        </Section>

        <Section title="How we decide">
          <p>This is our own editorial assessment, not a live computed score. We base it on:</p>
          <ul className="mt-2 list-disc space-y-1 ps-5">
            <li>
              <span className="font-medium">The mechanism itself</span> - a lottery with far more applicants than
              spots is rated higher than a first-come-first-served booking with no real cap.
            </li>
            <li>
              <span className="font-medium">Quota size relative to demand</span> - how many spots are actually
              released, and how that compares to how many people are known to want one.
            </li>
            <li>
              <span className="font-medium">Reported outcomes</span> - how fast a booking window has historically
              sold out, waitlist reports, and what the issuing authority itself publishes about demand.
            </li>
            <li>
              <span className="font-medium">Seasonality</span> - the same permit can be far more contested in peak
              season than in the shoulder season.
            </li>
          </ul>
        </Section>

        <Section title="Keeping it current">
          <p>
            We revisit ratings when something material changes - a quota shrinks, a destination gets more popular,
            or new information becomes available. If you think a rating looks off for a destination you know well,{" "}
            <a href="/contact" className="text-amber-700 underline dark:text-amber-400">
              let us know
            </a>
            .
          </p>
        </Section>
      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <section>
      <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">{title}</h2>
      <div className="mt-2 text-sm leading-relaxed">{children}</div>
    </section>
  );
}
