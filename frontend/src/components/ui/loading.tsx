import { cn } from "@/lib/utils";
import { AiOutlineLoading, AiOutlineLoading3Quarters } from "react-icons/ai";

const icons = [AiOutlineLoading, AiOutlineLoading3Quarters];

const RandomIcon = ({ className }: { className: string }) => {
  const Icon = icons[Math.floor(Math.random() * icons.length)];
  return <Icon className={className} />;
};

interface LoadingProps {
  text?: string;
  className?: string;
}

const Loading = ({ text = "Loading...", className }: LoadingProps) => {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-2 h-full",
        className
      )}
    >
      <RandomIcon className="h-20 w-20 animate-spin" />
      <span className="text-sm text-muted-foreground">{text}</span>
    </div>
  );
};

export default Loading;
