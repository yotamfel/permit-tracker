import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";

export default function Contact() {
  const { user } = useAuth();
  const [form, setForm] = useState({ name: "", email: "", message: "" });
  const [status, setStatus] = useState("idle");

  // `user` loads asynchronously after mount, so the initial useState above
  // often misses it - fill the email in once it arrives, without clobbering
  // anything the visitor already typed.
  useEffect(() => {
    if (user?.email) {
      setForm((f) => (f.email ? f : { ...f, email: user.email }));
    }
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("sending");
    try {
      await api.post("/api/contact", form);
      setStatus("sent");
      setForm({ name: "", email: user?.email || "", message: "" });
    } catch {
      setStatus("error");
    }
  };

  return (
    <div className="mx-auto max-w-lg px-4 py-8">
      <h1 className="text-2xl font-bold">Contact us</h1>
      <p className="mt-1 text-slate-500">
        Questions, requests, or something not working right? Send us a message.
      </p>

      {status === "sent" ? (
        <p className="mt-6 rounded bg-green-100 p-3 text-green-800 dark:bg-green-900/40 dark:text-green-300">
          Thanks - we received your message and will get back to you.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="mt-6 space-y-3">
          <input
            required
            placeholder="Your name"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1.5 dark:border-slate-700"
          />
          <input
            required
            type="email"
            placeholder="Your email"
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
            className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1.5 dark:border-slate-700"
          />
          <textarea
            required
            rows={5}
            placeholder="Your message"
            value={form.message}
            onChange={(e) => setForm((f) => ({ ...f, message: e.target.value }))}
            className="block w-full rounded border border-slate-300 bg-transparent px-2 py-1.5 dark:border-slate-700"
          />
          <button
            type="submit"
            disabled={status === "sending"}
            className="rounded bg-slate-900 px-4 py-2 text-sm text-white disabled:opacity-50 dark:bg-slate-100 dark:text-slate-900"
          >
            {status === "sending" ? "Sending..." : "Send message"}
          </button>
          {status === "error" && <p className="text-sm text-red-600">Something went wrong. Try again.</p>}
        </form>
      )}
    </div>
  );
}
