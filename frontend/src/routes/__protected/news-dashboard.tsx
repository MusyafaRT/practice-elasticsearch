import NewsDashboardPage from "@/features/newsDashboard/NewsDashboardPage";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/__protected/news-dashboard")({
  component: NewsDashboardPage,
});
