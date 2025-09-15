import { useSidebarStore } from "@/stores/useSidebarStore";
import { Sidebar } from "./SideBar";

interface RootLayoutProps {
  children?: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  const { isOpen } = useSidebarStore();

  return (
    <div className="relative w-full min-h-screen bg-background text-[#253a4a]">
      <Sidebar defaultValue="dashboard" />
      <main
        className={`
          relative z-10
          pt-14 md:pt-6
          px-4
          transition-all duration-300
          bg-background
          ${isOpen ? "md:pl-64" : "md:pl-20"}
           min-h-[calc(100vh-56px)] md:min-h-[calc(100vh-24px)]
        `}
      >
        {children}
      </main>
    </div>
  );
}
