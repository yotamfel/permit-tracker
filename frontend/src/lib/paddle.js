// Paddle.js (loaded via a <script> tag in index.html) needs to be initialized,
// then explicitly told to open the checkout overlay for whatever transaction
// the backend's checkout_url (see app/services/paddle_service.py) redirected
// to via a "?_ptxn=<transaction id>" query param.
//
// This used to rely on Paddle.js "auto-detecting" _ptxn from the URL and
// opening the overlay on its own after Initialize() - but confirmed by direct
// testing that Environment.set("production") only reliably takes effect when
// called immediately before Checkout.open(), in the same synchronous tick;
// call it any earlier (even a few seconds earlier, even repeatedly) and
// Paddle's own auto-detected open silently uses its sandbox default instead,
// sending a real transaction ID to sandbox-checkout-service.paddle.com (403,
// since it only exists in production). So instead of trusting the
// auto-detect timing, we read _ptxn ourselves and call Checkout.open()
// directly, with Environment.set() right beside it.
const ENVIRONMENT = import.meta.env.VITE_PADDLE_ENVIRONMENT === "sandbox" ? "sandbox" : "production";

function openCheckoutForCurrentUrl() {
  const transactionId = new URLSearchParams(window.location.search).get("_ptxn");
  if (!transactionId || !window.Paddle) return;
  window.Paddle.Environment.set(ENVIRONMENT);
  window.Paddle.Checkout.open({ transactionId });
}

export function initPaddle() {
  const token = import.meta.env.VITE_PADDLE_CLIENT_TOKEN;
  if (!token || !window.Paddle) return;

  window.Paddle.Environment.set(ENVIRONMENT);
  window.Paddle.Initialize({ token });
  openCheckoutForCurrentUrl();
}
