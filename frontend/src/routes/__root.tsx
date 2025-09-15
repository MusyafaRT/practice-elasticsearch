import { Toaster } from "@/components/ui/sonner";
import { Outlet, createRootRoute } from "@tanstack/react-router";

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <Outlet />
      <Toaster />
    </main>
  );
}
