import { useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const navigate = useNavigate();
  const { refreshMe } = useAuth();
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const res = await api.post("/api/auth/reset-password", { token, new_password: password });
      localStorage.setItem("token", res.data.access_token);
      await refreshMe();
      navigate("/");
    } catch (e) {
      setError(e.response?.data?.detail || "That reset link is invalid or has expired.");
    } finally {
      setSubmitting(false);
    }
  };

  if (!token) {
    return (
      <div className="mx-auto max-w-sm px-4 py-8">
        <p className="text-sm text-red-600">Missing reset token.</p>
        <Link to="/forgot-password" className="mt-3 block text-sm text-amber-700 underline dark:text-amber-400">
          Request a new reset link
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-sm px-4 py-8">
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">Choose a new password</h1>
      <form onSubmit={handleSubmit} className="mt-4 space-y-3">
        <input
          type="password"
          required
          minLength={8}
          placeholder="New password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1.5 dark:border-stone-700"
        />
        {error && (
          <div>
            <p className="text-sm text-red-600">{error}</p>
            <Link to="/forgot-password" className="text-sm text-amber-700 underline dark:text-amber-400">
              Request a new link
            </Link>
          </div>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="rounded-full bg-amber-600 px-5 py-2 text-sm font-semibold text-white hover:bg-amber-700 disabled:opacity-50"
        >
          Set new password
        </button>
      </form>
    </div>
  );
}
