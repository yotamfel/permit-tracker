import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../lib/AuthContext";
import GoogleSignInButton from "../components/GoogleSignInButton";

export default function Login() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      navigate("/");
    } catch {
      setError(t("auth.error"));
    }
  };

  return (
    <div className="mx-auto max-w-sm px-4 py-8">
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">{t("auth.login_title")}</h1>
      <p className="mt-1 text-sm text-stone-500 dark:text-stone-400">
        Log in to unlock full prep checklists and set alerts for hard-to-get permits worldwide.
      </p>

      <div className="mt-4">
        <GoogleSignInButton onSuccess={() => navigate("/")} onError={() => setError(t("auth.error"))} />
      </div>
      <div className="my-4 flex items-center gap-2 text-xs text-stone-400">
        <div className="h-px flex-1 bg-stone-200 dark:bg-stone-800" />
        or
        <div className="h-px flex-1 bg-stone-200 dark:bg-stone-800" />
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          type="email"
          required
          placeholder={t("auth.email")}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1.5 dark:border-stone-700"
        />
        <input
          type="password"
          required
          placeholder={t("auth.password")}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1.5 dark:border-stone-700"
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button type="submit" className="rounded-full bg-amber-600 px-5 py-2 text-sm font-semibold text-white hover:bg-amber-700">
          {t("auth.submit_login")}
        </button>
      </form>
      <Link to="/signup" className="mt-3 block text-sm text-amber-700 underline dark:text-amber-400">
        {t("auth.switch_to_signup")}
      </Link>
    </div>
  );
}
