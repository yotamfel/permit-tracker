import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../lib/AuthContext";
import { useTheme } from "../lib/ThemeContext";

// Language switcher is hidden for now - English-only launch, i18n plumbing stays
// in place (locales/, i18n.js, translations table) for when content translation
// work resumes. See README.md.
export default function Header() {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();

  return (
    <header className="border-b border-stone-200 bg-white/80 backdrop-blur dark:border-stone-800 dark:bg-stone-950/80">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
        <Link to="/" className="flex items-center gap-1.5 text-lg font-bold text-stone-900 dark:text-stone-50">
          <span aria-hidden="true">🧭</span>
          {t("app_name")}
        </Link>

        <nav className="flex items-center gap-4 text-sm text-stone-700 dark:text-stone-300">
          <Link to="/catalog" className="hover:text-amber-700 dark:hover:text-amber-400">
            {t("nav.browse")}
          </Link>
          <Link to="/contact" className="hover:text-amber-700 dark:hover:text-amber-400">
            Contact
          </Link>
          {user && (
            <Link to="/account" className="hover:text-amber-700 dark:hover:text-amber-400">
              {t("nav.account")}
            </Link>
          )}
          <Link to="/admin" className="hover:text-amber-700 dark:hover:text-amber-400">
            {t("nav.admin")}
          </Link>

          <select
            aria-label="theme"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="rounded-lg border border-stone-300 bg-transparent px-1 py-0.5 dark:border-stone-700"
          >
            <option value="light">{t("theme.light")}</option>
            <option value="dark">{t("theme.dark")}</option>
            <option value="system">{t("theme.system")}</option>
          </select>

          {user ? (
            <button onClick={logout} className="underline hover:text-amber-700 dark:hover:text-amber-400">
              {t("nav.logout")}
            </button>
          ) : (
            <>
              <Link to="/login" className="hover:text-amber-700 dark:hover:text-amber-400">
                {t("nav.login")}
              </Link>
              <Link
                to="/signup"
                className="rounded-full bg-amber-600 px-3 py-1.5 font-medium text-white hover:bg-amber-700"
              >
                {t("nav.signup")}
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
