// Sidebar.tsx
import type React from "react";
import { GiHamburgerMenu } from "react-icons/gi";
import { IoHome, IoNewspaper } from "react-icons/io5";
import { Link, useLocation } from "@tanstack/react-router";
import { useSidebarStore } from "@/stores/useSidebarStore";
import { Button } from "@/components/ui/button";

interface SidebarProps {
  defaultValue?: string;
}

export function Sidebar({ defaultValue }: SidebarProps) {
  const location = useLocation();
  const { isOpen, toggleSidebar } = useSidebarStore();

  const getActiveTab = () => {
    const path = location.pathname;
    if (path === "/dashboard") return "dashboard";
    else if (path === "/news-dashboard") return "news-dashboard";
    return defaultValue;
  };

  const activeTab = getActiveTab();

  return (
    <>
      {isOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 bg-opacity-50 z-20 "
          onClick={toggleSidebar}
        />
      )}

      <div
        className={`
            fixed top-0 left-0 h-screen
            ${isOpen ? "w-64 translate-x-0" : "w-20 -translate-x-full md:translate-x-0"}
            bg-background md:shadow-md z-40
            transition-all duration-300 ease-in-out
        `}
      >
        <div className="p-4">
          <div
            className={`flex items-center mb-8 ${isOpen ? "justify-between" : "justify-center"}`}
          >
            <h1
              className={`
                text-2xl font-bold text-[#253a4a]
                transition-all duration-300
                ${isOpen ? "opacity-100 max-w-full" : "opacity-0 max-w-0"}
                overflow-hidden whitespace-nowrap
            `}
            >
              Retail Sales
            </h1>

            <Button
              className="text-[#253a4a] hover:bg-gray/20 rounded-full p-2 bg-white shadow-accent"
              onClick={toggleSidebar}
              size={"icon"}
            >
              <GiHamburgerMenu className="w-5 h-5" />
            </Button>
          </div>

          <nav className="space-y-2">
            <NavItem
              value="dashboard"
              href="/dashboard"
              icon={<IoHome className="w-5 h-5" />}
              text="Dashboard"
              activeTab={activeTab}
              isOpen={isOpen}
            />
            <NavItem
              value="news-dashboard"
              href="/news-dashboard"
              icon={<IoNewspaper className="w-5 h-5" />}
              text="News Dashboard"
              activeTab={activeTab}
              isOpen={isOpen}
            />
          </nav>
        </div>
      </div>
    </>
  );
}

function NavItem({
  href,
  icon,
  text,
  value,
  activeTab,
  isOpen,
}: {
  value: string;
  href: string;
  icon: React.ReactNode;
  text: string;
  activeTab: string | undefined;
  isOpen: boolean;
}) {
  const isActive = activeTab === value;

  return (
    <Link
      to={href}
      className={`flex items-center px-4 py-2 rounded-lg transition-all duration-300 ${
        isActive
          ? "bg-gray-200 text-[#253a4a]"
          : "text-[#718ebf] hover:bg-primary/50"
      } ${isOpen ? "space-x-3" : "space-x-0 md:justify-center"}`}
      title={!isOpen ? text : undefined}
    >
      <div className="flex-shrink-0">{icon}</div>
      <span
        className={`transition-opacity duration-300 ${
          isOpen ? "opacity-100" : "opacity-100 md:opacity-0 md:hidden"
        }`}
      >
        {text}
      </span>
    </Link>
  );
}
