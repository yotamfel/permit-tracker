import { useEffect, useRef } from "react";
import { useAuth } from "../lib/AuthContext";

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;
// hl=en forces English regardless of browser locale, to match the site's English-only launch.
const GIS_SCRIPT_SRC = "https://accounts.google.com/gsi/client?hl=en";

// Loaded on demand (only when this button actually renders, i.e. only on
// Login/Signup) rather than globally from index.html - it's ~97KB and every
// other page was paying for it unused. Safe to call more than once (e.g.
// navigating between Login and Signup); the existing <script> is reused.
function loadGisScript() {
  if (document.querySelector(`script[src="${GIS_SCRIPT_SRC}"]`)) return;
  const script = document.createElement("script");
  script.src = GIS_SCRIPT_SRC;
  script.async = true;
  script.defer = true;
  document.head.appendChild(script);
}

export default function GoogleSignInButton({ onSuccess, onError, termsAccepted = false }) {
  const { loginWithGoogle } = useAuth();
  const buttonRef = useRef(null);

  useEffect(() => {
    if (!CLIENT_ID) return;

    loadGisScript();
    let cancelled = false;

    const render = () => {
      if (cancelled || !window.google?.accounts?.id || !buttonRef.current) return;
      window.google.accounts.id.initialize({
        client_id: CLIENT_ID,
        callback: async (response) => {
          try {
            await loginWithGoogle(response.credential, termsAccepted);
            onSuccess?.();
          } catch {
            onError?.();
          }
        },
      });
      window.google.accounts.id.renderButton(buttonRef.current, {
        theme: "outline",
        size: "large",
        width: 320,
      });
    };

    // The GIS script loads async - poll briefly until it's ready.
    if (window.google?.accounts?.id) {
      render();
    } else {
      const interval = setInterval(() => {
        if (window.google?.accounts?.id) {
          clearInterval(interval);
          render();
        }
      }, 100);
      return () => {
        cancelled = true;
        clearInterval(interval);
      };
    }
    return () => {
      cancelled = true;
    };
  }, [loginWithGoogle, onSuccess, onError, termsAccepted]);

  if (!CLIENT_ID) return null;

  return <div ref={buttonRef} />;
}
