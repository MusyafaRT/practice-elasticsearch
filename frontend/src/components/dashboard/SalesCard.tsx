import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type React from "react";

interface SalesCardProps {
  title: string | React.ReactNode;
  icon: React.ReactNode;
  amount: React.ReactNode;
  subtitle: string | React.ReactNode;
  subtitleColors?: string;
}

const SalesCard = ({
  title,
  icon,
  amount,
  subtitle,
  subtitleColors,
}: SalesCardProps) => {
  return (
    <Card className="hover:shadow-lg transition-shadow duration-300">
      <CardHeader className="flex items-center justify-between">
        <CardTitle className="text-lg font-medium text-gray-500">
          {title}
        </CardTitle>
        <div className="text-primary text-2xl">{icon}</div>
      </CardHeader>
      <CardContent>
        <p className="text-2xl font-bold text-gray-900">{amount}</p>
        <CardDescription
          className={cn("text-sm text-green-500 mt-1", subtitleColors)}
        >
          {subtitle}
        </CardDescription>
      </CardContent>
    </Card>
  );
};

export default SalesCard;
