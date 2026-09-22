// Paddle.js (loaded via a <script> tag in index.html) needs to be initialized
// once so it can detect a "?_ptxn=<transaction id>" query param - appended by
// the backend's checkout_url (see app/services/paddle_service.py) - and open
// the payment overlay on top of whatever page the browser lands on. No other
// wiring is needed: the existing `window.location.href = checkout_url`
// redirect in DestinationDetail.jsx already lands on a URL Paddle.js will
// recognize once this has run.
export function initPaddle() {
  const token = import.meta.env.VITE_PADDLE_CLIENT_TOKEN;
  if (!token || !window.Paddle) return;

  // Paddle.js defaults to sandbox unless explicitly told otherwise - set this
  // either way rather than only handling the sandbox case, or a missing/blank
  // VITE_PADDLE_ENVIRONMENT silently sends real production transactions to
  // Paddle's sandbox checkout service (which 403s, since they don't exist
  // there).
  window.Paddle.Environment.set(import.meta.env.VITE_PADDLE_ENVIRONMENT === "sandbox" ? "sandbox" : "production");
  window.Paddle.Initialize({ token });
}
