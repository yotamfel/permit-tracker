import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("idle");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("sending");
    try {
      await api.post("/api/auth/forgot-password", { email });
      setStatus("sent");
    } catch {
      setStatus("error");
    }
  };

  return (
    <div className="mx-auto max-w-sm px-4 py-8">
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">Reset your password</h1>
      <p className="mt-1 text-sm text-stone-500 dark:text-stone-400">
        Enter your account email and we'll send you a link to choose a new password.
      </p>

      {status === "sent" ? (
        <p className="mt-6 rounded-xl bg-emerald-100 p-3 text-sm text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
          If that email has an account, a reset link is on its way. Check your inbox.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="mt-4 space-y-3">
          <input
            type="email"
            required
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="block w-full rounded-lg border border-stone-300 bg-transparent px-2 py-1.5 dark:border-stone-700"
          />
          {status === "error" && <p className="text-sm text-red-600">Something went wrong. Try again.</p>}
          <button
            type="submit"
            disabled={status === "sending"}
            className="rounded-full bg-amber-600 px-5 py-2 text-sm font-semibold text-white hover:bg-amber-700 disabled:opacity-50"
          >
            {status === "sending" ? "Sending..." : "Send reset link"}
          </button>
        </form>
      )}

      <Link to="/login" className="mt-3 block text-sm text-amber-700 underline dark:text-amber-400">
        Back to log in
      </Link>
    </div>
  );
}
