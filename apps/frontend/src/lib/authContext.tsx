"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User } from "@/types";
import { authApi, getAuthToken, setAuthToken } from "@/lib/api";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<boolean>;
  register: (data: any) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  loginDemo: (role: "borrower" | "owner" | "skills") => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  isLoading: true,
  login: async () => false,
  register: async () => false,
  logout: async () => {},
  refreshUser: async () => {},
  loginDemo: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const refreshUser = async () => {
    const existingToken = getAuthToken();
    if (!existingToken) {
      setUser(null);
      setToken(null);
      setIsLoading(false);
      return;
    }

    try {
      const me = await authApi.getMe();
      setUser(me);
      setToken(existingToken);
    } catch (err) {
      console.warn("Session restore failed, clearing token", err);
      setAuthToken(null);
      setUser(null);
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (email: string, pass: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      const res = await authApi.login({ email, password: pass });
      setUser(res.user);
      setToken(res.access_token);
      toast.success(`Welcome back, ${res.user.full_name}!`);
      return true;
    } catch (err: any) {
      toast.error(err.message || "Login failed. Please check credentials.");
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: any): Promise<boolean> => {
    try {
      setIsLoading(true);
      const res = await authApi.register(data);
      setUser(res.user);
      setToken(res.access_token);
      toast.success("Account created successfully! Welcome to NeighbourNode.");
      return true;
    } catch (err: any) {
      toast.error(err.message || "Registration failed.");
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
    setToken(null);
    toast.info("Signed out.");
    router.push("/");
  };

  const loginDemo = async (role: "borrower" | "owner" | "skills") => {
    const email =
      role === "owner"
        ? "owner@neighbournode.local"
        : role === "skills"
        ? "skills@neighbournode.local"
        : "demo@neighbournode.local";

    const ok = await login(email, "Password123!");
    if (ok) {
      router.push("/dashboard");
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        register,
        logout,
        refreshUser,
        loginDemo,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

