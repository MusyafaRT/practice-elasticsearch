// src/routes/_protected.tsx
import { useRefreshToken } from "@/hooks/useAuth";
import RootLayout from "@/layouts/Layout";
import type { ResUserToken } from "@/models/auth";
import type { ResponseWrapper } from "@/models/globalTypes";
import { useAuthStore } from "@/stores/useAuthStore";
import { createFileRoute, redirect, Outlet } from "@tanstack/react-router";
import { jwtDecode } from "jwt-decode";

interface JwtPayload {
  exp: number;
}

export const Route = createFileRoute("/__protected")({
  beforeLoad: async () => {
    const { token, logout } = useAuthStore.getState();
    // const { refreshToken, isRefreshTokenPending } = useRefreshToken();

    if (!token) {
      throw redirect({ to: "/auth" });
    }

    try {
      const decoded = jwtDecode<JwtPayload>(token);
      const currentTime = Date.now() / 1000;

      if (decoded.exp < currentTime) {
        // try {
        //   const resp: ResponseWrapper<ResUserToken> = await refreshToken();
        //   if (resp.data) {
        //     const { access_token, refresh_token } = resp.data;
        //     useAuthStore.getState().login(access_token, refresh_token, null);
        //     return;
        //   }
        // } catch (error) {
        //   logout();
        //   throw redirect({ to: "/auth" });
        // }
        throw redirect({ to: "/auth" });
      }
    } catch (err) {
      logout();
      throw redirect({ to: "/auth" });
    }
  },
  component: () => (
    <RootLayout>
      <Outlet />
    </RootLayout>
  ),
});
