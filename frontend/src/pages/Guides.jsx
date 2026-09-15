import { Link } from "react-router-dom";
import SeoHead from "../components/SeoHead";
import { GUIDES } from "../data/guides";

export default function Guides() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <SeoHead
        title="Guides"
        description="Practical guides to how permit lotteries, operator quotas, deposits, and remote-travel insurance actually work."
        path="/guides"
      />
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">Guides</h1>
      <p className="mt-1 text-stone-500 dark:text-stone-400">
        How permit systems actually work - independent of any one destination.
      </p>

      <ul className="mt-6 space-y-4">
        {GUIDES.map((g) => (
          <li key={g.slug} className="rounded-2xl border border-stone-200 p-4 dark:border-stone-800">
            <Link
              to={`/guides/${g.slug}`}
              className="text-lg font-semibold text-stone-900 hover:text-amber-700 dark:text-stone-100 dark:hover:text-amber-400"
            >
              {g.title}
            </Link>
            <p className="mt-1 text-sm text-stone-600 dark:text-stone-400">{g.description}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
