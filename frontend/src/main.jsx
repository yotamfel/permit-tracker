import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import "./lib/i18n";
import "./index.css";
import App from "./App.jsx";
import { AuthProvider } from "./lib/AuthContext.jsx";
import { ThemeProvider } from "./lib/ThemeContext.jsx";
import { OnboardingProvider } from "./lib/OnboardingContext.jsx";
import { initAnalytics } from "./lib/analytics.js";
import { initPaddle } from "./lib/paddle.js";

initAnalytics();
initPaddle();

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <HelmetProvider>
      <BrowserRouter>
        <AuthProvider>
          <ThemeProvider>
            <OnboardingProvider>
              <App />
            </OnboardingProvider>
          </ThemeProvider>
        </AuthProvider>
      </BrowserRouter>
    </HelmetProvider>
  </StrictMode>
);
