import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="border-t border-stone-200 dark:border-stone-800">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-6 text-sm text-stone-500 dark:text-stone-400">
        <span>© {new Date().getFullYear()} Permit Tracker</span>
        <nav className="flex gap-4">
          <Link to="/terms" className="hover:text-amber-700 dark:hover:text-amber-400">
            Terms of Service
          </Link>
          <Link to="/privacy" className="hover:text-amber-700 dark:hover:text-amber-400">
            Privacy Policy
          </Link>
          <Link to="/contact" className="hover:text-amber-700 dark:hover:text-amber-400">
            Contact
          </Link>
        </nav>
      </div>
    </footer>
  );
}
