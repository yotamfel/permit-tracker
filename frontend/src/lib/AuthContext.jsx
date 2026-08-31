import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshMe = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const res = await api.get("/api/me");
      setUser(res.data);
    } catch {
      localStorage.removeItem("token");
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshMe();
  }, [refreshMe]);

  const login = async (email, password) => {
    const res = await api.post("/api/auth/login", { email, password });
    localStorage.setItem("token", res.data.access_token);
    await refreshMe();
  };

  const signup = async (email, password) => {
    const res = await api.post("/api/auth/signup", { email, password });
    localStorage.setItem("token", res.data.access_token);
    await refreshMe();
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, refreshMe }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
