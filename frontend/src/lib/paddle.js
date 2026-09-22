// Paddle.js (loaded via a <script> tag in index.html) needs to be initialized
// once so it can detect a "?_ptxn=<transaction id>" query param - appended by
// the backend's checkout_url (see app/services/paddle_service.py) - and open
// the payment overlay on top of whatever page the browser lands on. No other
// wiring is needed: the existing `window.location.href = checkout_url`
// redirect in DestinationDetail.jsx already lands on a URL Paddle.js will
// recognize once this has run.
// window.Paddle exists as soon as the <script> tag finishes its own top-level
// execution, but paddle.js does further async internal setup after that -
// calling Environment.set() immediately (synchronously, on the very first
// tick window.Paddle exists) gets silently overridden back to Paddle's own
// sandbox default once that internal setup runs. Re-asserting it for a few
// seconds after window.Paddle first appears sidesteps needing to know
// Paddle's actual internal "ready" signal. Environment.set() is just a
// config flag, safe to call repeatedly; Initialize() is called once, after
// that window, so it isn't racing the same internal setup.
const ENVIRONMENT = import.meta.env.VITE_PADDLE_ENVIRONMENT === "sandbox" ? "sandbox" : "production";

function reassertEnvironment(attemptsLeft = 16) {
  if (!window.Paddle) {
    if (attemptsLeft <= 0) return;
    setTimeout(() => reassertEnvironment(attemptsLeft - 1), 150);
    return;
  }
  window.Paddle.Environment.set(ENVIRONMENT);
  if (attemptsLeft > 0) {
    setTimeout(() => reassertEnvironment(attemptsLeft - 1), 150);
  }
}

export function initPaddle() {
  const token = import.meta.env.VITE_PADDLE_CLIENT_TOKEN;
  if (!token) return;

  reassertEnvironment();
  setTimeout(() => {
    if (!window.Paddle) return;
    window.Paddle.Initialize({ token });
  }, 2500);
}
