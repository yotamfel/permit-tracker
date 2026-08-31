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
    <header className="border-b border-slate-200 dark:border-slate-800">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
        <Link to="/" className="text-lg font-semibold">
          {t("app_name")}
        </Link>

        <nav className="flex items-center gap-4 text-sm">
          <Link to="/">{t("nav.browse")}</Link>
          <Link to="/contact">Contact</Link>
          {user && <Link to="/account">{t("nav.account")}</Link>}
          <Link to="/admin">{t("nav.admin")}</Link>

          <select
            aria-label="theme"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="rounded border border-slate-300 bg-transparent px-1 py-0.5 dark:border-slate-700"
          >
            <option value="light">{t("theme.light")}</option>
            <option value="dark">{t("theme.dark")}</option>
            <option value="system">{t("theme.system")}</option>
          </select>

          {user ? (
            <button onClick={logout} className="underline">
              {t("nav.logout")}
            </button>
          ) : (
            <>
              <Link to="/login">{t("nav.login")}</Link>
              <Link to="/signup">{t("nav.signup")}</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
