import { cn } from "@/lib/utils";
import { PackageX } from "lucide-react";

interface NoDataWrapperProps {
  children: React.ReactNode;
  show: boolean;
  message?: string;
  className?: string;
}

const NoDataWrapper = ({
  children,
  show,
  message = "No data available.",
  className,
}: NoDataWrapperProps) => {
  if (show) {
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center py-8 text-muted-foreground",
          className
        )}
      >
        <PackageX className="h-12 w-12 mb-4" />
        <p className="text-lg font-medium">{message}</p>
      </div>
    );
  }
  return <>{children}</>;
};

export default NoDataWrapper;
