import { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api";
import { useAuth } from "./AuthContext";

const ThemeContext = createContext(null);

function applyTheme(theme) {
  const isDark =
    theme === "dark" || (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.classList.toggle("dark", isDark);
}

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(() => localStorage.getItem("theme") || "system");
  const { user, refreshMe } = useAuth() || {};

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  useEffect(() => {
    if (user?.theme_preference && user.theme_preference !== theme) {
      setThemeState(user.theme_preference);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const setTheme = async (next) => {
    setThemeState(next);
    localStorage.setItem("theme", next);
    if (user) {
      try {
        await api.patch("/api/me", { theme_preference: next });
        refreshMe?.();
      } catch {
        // best-effort sync; localStorage already updated
      }
    }
  };

  return <ThemeContext.Provider value={{ theme, setTheme }}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  return useContext(ThemeContext);
}
