import * as echarts from "echarts";
import type { NewsTagDistribution } from "@/models/analyticsTypes";
import "echarts-wordcloud";
import type { DetailSalesCardProps } from "../dashboard/DetailSalesCard";
import EChartsComponent from "../dashboard/EChartComponent";
import DetailSalesCard from "../dashboard/DetailSalesCard";
import { AlignVerticalDistributeCenter } from "lucide-react";
import { Skeleton } from "../ui/skeleton";

interface NewsTagDistributionProps {
  tagDistributionData: NewsTagDistribution[];
  isLoading: boolean;
}

const NewsTagDistributionArticle = ({
  tagDistributionData,
  isLoading,
}: NewsTagDistributionProps) => {
  const data = tagDistributionData.map((d) => ({
    name: d.tag,
    value: d.count,
  }));

  const option: echarts.EChartsOption = {
    tooltip: {
      show: true,
    },
    series: [
      {
        type: "wordCloud",
        shape: "circle",
        left: "center",
        top: "center",
        width: "100%",
        height: "100%",
        sizeRange: [30, 80],
        rotationRange: [-45, 45],
        rotationStep: 15,
        gridSize: 8,
        drawOutOfBound: false,
        textStyle: {
          color: () => `rgb(${Math.floor(Math.random() * 160)}, 
                            ${Math.floor(Math.random() * 160)}, 
                            ${Math.floor(Math.random() * 160)})`,
        },
        emphasis: {
          focus: "self",
        },
        data,
      },
    ],
  };

  const newsWordCloud: DetailSalesCardProps[] = [
    {
      title: "News Word Cloud",
      chart: <EChartsComponent option={option} height={550} />,
      subtitle: "News Tag Distribution ",
      icon: <AlignVerticalDistributeCenter />,
    },
  ];
  if (isLoading) {
    return (
      <div className="h-[388px] w-full rounded-xl border p-6 flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <Skeleton className="h-6 w-1/4" />
          <Skeleton className="h-4 w-1/3" />
        </div>
        <div className="flex-1">
          <Skeleton className="h-full w-full" />
        </div>
      </div>
    );
  }

  return (
    <article className="grid grid-cols-1">
      {newsWordCloud.map((card, index) => (
        <DetailSalesCard key={index} {...card} />
      ))}
    </article>
  );
};

export default NewsTagDistributionArticle;
