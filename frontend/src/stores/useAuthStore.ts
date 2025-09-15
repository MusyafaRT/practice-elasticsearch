import type { UserData } from "@/models/userTypes";
import { create } from "zustand";
import { persist } from "zustand/middleware";

type AuthState = {
  token: string | null;
  refreshToken: string | null;
  user: UserData | null;
  isAuthenticated: boolean;
  login: (token: string, refreshToken: string, user: UserData | null) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      login: (token, refreshToken, user) =>
        set({ token, user, refreshToken, isAuthenticated: true }),
      logout: () => set({ token: null, user: null, isAuthenticated: false }),
    }),
    { name: "auth-storage" } // Simpan di localStorage
  )
);
