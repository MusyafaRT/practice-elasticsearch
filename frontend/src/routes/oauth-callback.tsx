import { useAuthStore } from "@/stores/useAuthStore";
import { createFileRoute, useRouter, useSearch } from "@tanstack/react-router";
import { useEffect } from "react";
import { toast } from "sonner"; // or your preferred toast library

interface OAuthCallbackSearch {
  access_token?: string;
  refresh_token?: string;
  error?: string;
}

export const Route = createFileRoute("/oauth-callback")({
  component: OAuthCallback,
  validateSearch: (search: Record<string, unknown>): OAuthCallbackSearch => {
    return {
      access_token:
        typeof search.access_token === "string"
          ? search.access_token
          : undefined,
      refresh_token:
        typeof search.refresh_token === "string"
          ? search.refresh_token
          : undefined,
      error: typeof search.error === "string" ? search.error : undefined,
    };
  },
});

function OAuthCallback() {
  const router = useRouter();
  const search = useSearch({ from: "/oauth-callback" });
  const { login } = useAuthStore();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        if (search.error) {
          toast.error(`OAuth error: ${search.error}`);
          router.navigate({ to: "/auth" });
          return;
        }

        if (search.access_token && search.refresh_token) {
          // Fetch user data with the access token

          // Store tokens and user data
          login(search.access_token, search.refresh_token, null);

          toast.success("Successfully logged in!");
          router.navigate({ to: "/dashboard" }); // or wherever you want to redirect
        } else {
          throw new Error("Missing tokens in callback");
        }
      } catch (error) {
        console.error("OAuth callback error:", error);
        toast.error("Login failed. Please try again.");
        router.navigate({ to: "/auth" });
      }
    };

    handleCallback();
  }, [search, login, router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Processing login...</p>
      </div>
    </div>
  );
}
