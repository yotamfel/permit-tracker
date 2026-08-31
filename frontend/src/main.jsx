import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./lib/i18n";
import "./index.css";
import App from "./App.jsx";
import { AuthProvider } from "./lib/AuthContext.jsx";
import { ThemeProvider } from "./lib/ThemeContext.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ThemeProvider>
          <App />
        </ThemeProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
