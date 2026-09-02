import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center px-4 py-24 text-center">
      <span className="text-5xl" aria-hidden="true">
        🧭
      </span>
      <h1 className="mt-4 text-2xl font-bold text-stone-900 dark:text-stone-100">Page not found</h1>
      <p className="mt-2 text-stone-500 dark:text-stone-400">
        The page you're looking for doesn't exist or may have moved.
      </p>
      <div className="mt-6 flex gap-3">
        <Link to="/" className="rounded-full bg-amber-600 px-5 py-2 text-sm font-semibold text-white hover:bg-amber-700">
          Go home
        </Link>
        <Link
          to="/catalog"
          className="rounded-full border border-stone-300 px-5 py-2 text-sm font-semibold text-stone-700 hover:bg-stone-100 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
        >
          Browse catalog
        </Link>
      </div>
    </div>
  );
}
