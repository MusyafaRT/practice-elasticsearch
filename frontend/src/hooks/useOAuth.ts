// hooks/useOAuth.ts
import type { ResponseWrapper } from "@/models/globalTypes";
import type { GoogleOAuthLogin, ReqOAuth } from "@/models/auth";
import { useMutateApi } from "./useCallApi";

export const useOAuth = () => {
  const {
    mutateAsync: googleOAuthMutation,
    isPending: isGoogleOAuthPending,
    error: googleOAuthError,
  } = useMutateApi<ResponseWrapper<GoogleOAuthLogin>, ReqOAuth>();

  const initiateGoogleOAuth = async () => {
    try {
      const googleOAuthRes = await googleOAuthMutation({
        url: "/auth/oauth/google/login",
        method: "GET",
        data: {
          provider: "google",
        },
      });

      if (
        googleOAuthRes.status === "success" ||
        googleOAuthRes.status === "200"
      ) {
        if (googleOAuthRes.data.authorization_url) {
          window.location.href = googleOAuthRes.data.authorization_url;
        }
      }
    } catch (error) {
      console.error("OAuth initiation failed:", error);
    }
  };

  return {
    initiateGoogleOAuth,
    isLoading: isGoogleOAuthPending,
    error: googleOAuthError,
  };
};
