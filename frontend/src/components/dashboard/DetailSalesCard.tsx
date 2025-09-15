import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type React from "react";

export interface DetailSalesCardProps {
  title: string;
  icon: React.ReactNode;
  chart: React.ReactNode;
  subtitle: string;
}

const DetailSalesCard = ({
  title,
  icon,
  chart,
  subtitle,
}: DetailSalesCardProps) => {
  return (
    <Card className="h-full flex flex-col hover:shadow-lg transition-shadow duration-300">
      {/* Header */}
      <CardHeader className="flex items-center justify-between pb-2">
        <div className="flex flex-col">
          <CardTitle className="text-lg font-semibold text-gray-900">
            {title}
          </CardTitle>
          <span className="text-sm text-gray-500 mt-1">{subtitle}</span>
        </div>
        <div className="text-primary text-2xl">{icon}</div>
      </CardHeader>

      {/* Chart / Content */}
      <CardContent className="flex-1 flex items-center justify-center">
        <div className="w-full h-full">{chart}</div>
      </CardContent>
    </Card>
  );
};

export default DetailSalesCard;
