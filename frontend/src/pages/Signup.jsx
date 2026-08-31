import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../lib/AuthContext";

export default function Signup() {
  const { t } = useTranslation();
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await signup(email, password);
      navigate("/");
    } catch {
      setError(t("auth.error"));
    }
  };

  return (
    <div className="mx-auto max-w-sm px-4 py-8">
      <h1 className="text-xl font-bold">{t("auth.signup_title")}</h1>
      <form onSubmit={handleSubmit} className="mt-4 space-y-3">
        <input
          type="email"
          required
          placeholder={t("auth.email")}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1.5 dark:border-slate-700"
        />
        <input
          type="password"
          required
          minLength={8}
          placeholder={t("auth.password")}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1.5 dark:border-slate-700"
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button type="submit" className="rounded bg-slate-900 px-4 py-2 text-sm text-white dark:bg-slate-100 dark:text-slate-900">
          {t("auth.submit_signup")}
        </button>
      </form>
      <Link to="/login" className="mt-3 block text-sm underline">
        {t("auth.switch_to_login")}
      </Link>
    </div>
  );
}
