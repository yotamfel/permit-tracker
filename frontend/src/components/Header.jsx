import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../lib/AuthContext";
import { useTheme } from "../lib/ThemeContext";
import { useOnboarding } from "../lib/OnboardingContext";

// Language switcher is hidden for now - English-only launch, i18n plumbing stays
// in place (locales/, i18n.js, translations table) for when content translation
// work resumes. See README.md.
export default function Header() {
  const { t } = useTranslation();
  const { user, loading, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const { openGuide } = useOnboarding();
  const [menuOpen, setMenuOpen] = useState(false);

  const themeSelect = (
    <select
      aria-label="theme"
      value={theme}
      onChange={(e) => setTheme(e.target.value)}
      className="rounded-lg border border-stone-300 bg-white px-1 py-0.5 text-stone-900 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-100"
    >
      <option value="light">{t("theme.light")}</option>
      <option value="dark">{t("theme.dark")}</option>
    </select>
  );

  const navLinks = (
    <>
      <Link to="/catalog" className="hover:text-amber-700 dark:hover:text-amber-400" onClick={() => setMenuOpen(false)}>
        {t("nav.browse")}
      </Link>
      <Link to="/contact" className="hover:text-amber-700 dark:hover:text-amber-400" onClick={() => setMenuOpen(false)}>
        Contact
      </Link>
      {user && (
        <Link to="/account" className="hover:text-amber-700 dark:hover:text-amber-400" onClick={() => setMenuOpen(false)}>
          {t("nav.account")}
        </Link>
      )}
      <button
        onClick={() => {
          setMenuOpen(false);
          openGuide();
        }}
        className="text-left hover:text-amber-700 dark:hover:text-amber-400"
      >
        How it works
      </button>
      {user?.is_admin && (
        <>
          <Link to="/admin" className="hover:text-amber-700 dark:hover:text-amber-400" onClick={() => setMenuOpen(false)}>
            {t("nav.admin")}
          </Link>
          <span
            title="You're viewing as an admin - every destination shows as unlocked for you regardless of purchase."
            className="w-fit rounded-full border border-amber-300 bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300"
          >
            Admin view
          </span>
        </>
      )}

      {loading ? (
        <span className="h-4 w-16 animate-pulse rounded bg-stone-200 dark:bg-stone-800" aria-hidden="true" />
      ) : user ? (
        <button
          onClick={() => {
            setMenuOpen(false);
            logout();
          }}
          className="text-left underline hover:text-amber-700 dark:hover:text-amber-400"
        >
          {t("nav.logout")}
        </button>
      ) : (
        <>
          <Link to="/login" className="hover:text-amber-700 dark:hover:text-amber-400" onClick={() => setMenuOpen(false)}>
            {t("nav.login")}
          </Link>
          <Link
            to="/signup"
            className="w-fit rounded-full bg-amber-700 px-3 py-1.5 font-medium text-white hover:bg-amber-800"
            onClick={() => setMenuOpen(false)}
          >
            {t("nav.signup")}
          </Link>
        </>
      )}
    </>
  );

  return (
    <header className="border-b border-stone-200 bg-white/80 backdrop-blur dark:border-stone-800 dark:bg-stone-950/80">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
        <Link to="/" className="flex items-center gap-1.5 text-lg font-bold text-stone-900 dark:text-stone-50">
          <span aria-hidden="true">🧭</span>
          {t("app_name")}
        </Link>

        <nav className="hidden items-center gap-4 text-sm text-stone-800 dark:text-stone-300 md:flex">
          {navLinks}
          {themeSelect}
        </nav>

        <div className="flex items-center gap-2 md:hidden">
          {themeSelect}
          <button
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
            className="rounded-lg border border-stone-300 p-1.5 text-stone-800 dark:border-stone-700 dark:text-stone-200"
          >
            {menuOpen ? (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {menuOpen && (
        <nav className="flex flex-col gap-3 border-t border-stone-200 px-4 py-4 text-sm text-stone-800 dark:border-stone-800 dark:text-stone-300 md:hidden">
          {navLinks}
        </nav>
      )}
    </header>
  );
}
