import { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api";
import { useAuth } from "./AuthContext";

const ThemeContext = createContext(null);

// "system" used to be a third option here - it's been removed (light/dark
// only now), but old localStorage values / user.theme_preference rows from
// before that change may still say "system", so normalize it to "light".
function normalizeTheme(theme) {
  return theme === "dark" ? "dark" : "light";
}

function applyTheme(theme) {
  document.documentElement.classList.toggle("dark", theme === "dark");
}

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(() => normalizeTheme(localStorage.getItem("theme")));
  const { user, refreshMe } = useAuth() || {};

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  useEffect(() => {
    const preferred = user?.theme_preference && normalizeTheme(user.theme_preference);
    if (preferred && preferred !== theme) {
      setThemeState(preferred);
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
