import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { getCurrentUser, login as loginService, logout as logoutService } from "../services/auth";
import {
  getHasSshKey,
  getStoredUser,
  getToken,
  setHasSshKey as persistHasSshKey,
  setStoredUser,
} from "../services/session";
import type { User } from "../services/types";

const ADMIN_IDS = (import.meta.env.VITE_ADMIN_LDAP_IDS || "")
  .split(",")
  .map((value: string) => value.trim())
  .filter(Boolean);

type AuthStatus = "loading" | "ready";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  status: AuthStatus;
  isAdmin: boolean;
  hasSshKey: boolean;
  login: (ldapId: string, password: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
  markSshKey: (value: boolean) => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(getStoredUser());
  const [token, setToken] = useState<string | null>(getToken());
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [hasSshKey, setHasSshKey] = useState<boolean>(getHasSshKey());

  useEffect(() => {
    const existingToken = getToken();
    if (!existingToken) {
      setStatus("ready");
      return;
    }

    getCurrentUser()
      .then((currentUser) => {
        setUser(currentUser);
        setStoredUser(currentUser);
        setToken(existingToken);
        setStatus("ready");
      })
      .catch(() => {
        logoutService();
        setUser(null);
        setToken(null);
        setHasSshKey(false);
        setStatus("ready");
      });
  }, []);

  const login = async (ldapId: string, password: string) => {
    setStatus("loading");
    try {
      const nextUser = await loginService(ldapId, password);
      setUser(nextUser);
      setToken(getToken());
    } finally {
      setStatus("ready");
    }
  };

  const logout = () => {
    logoutService();
    setUser(null);
    setToken(null);
    setHasSshKey(false);
  };

  const refresh = async () => {
    const nextUser = await getCurrentUser();
    setUser(nextUser);
    setStoredUser(nextUser);
  };

  const markSshKey = (value: boolean) => {
    setHasSshKey(value);
    persistHasSshKey(value);
  };

  const isAdmin = useMemo(() => {
    if (!user) {
      return false;
    }
    return ADMIN_IDS.includes(user.ldap_id);
  }, [user]);

  const value = useMemo(
    () => ({
      user,
      token,
      status,
      isAdmin,
      hasSshKey,
      login,
      logout,
      refresh,
      markSshKey,
    }),
    [user, token, status, isAdmin, hasSshKey, login, logout, refresh, markSshKey]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
