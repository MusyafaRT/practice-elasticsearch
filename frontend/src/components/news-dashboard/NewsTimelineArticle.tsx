import DetailSalesCard, {
  type DetailSalesCardProps,
} from "../dashboard/DetailSalesCard";
import type { EChartColors } from "@/models/globalTypes";
import type { NewsTimeline } from "@/models/analyticsTypes";
import { Skeleton } from "../ui/skeleton";
import EChartsComponent from "../dashboard/EChartComponent";
import { AiOutlineStock } from "react-icons/ai";
import { useMemo } from "react";
import NoDataWrapper from "../ui/nodata-wrapper";

interface NewsTimelineArticleProps {
  colors: EChartColors;
  newsTimeline?: NewsTimeline[];
  isLoading?: boolean;
}

const NewsTimelineArticle = ({
  colors,
  newsTimeline,
  isLoading,
}: NewsTimelineArticleProps) => {
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

  const combinedChartOption: echarts.EChartsOption = useMemo(
    () => ({
      tooltip: {
        trigger: "axis",
        backgroundColor: colors.popover,
        borderColor: colors.border,
        textStyle: { color: colors.foreground },
        formatter: (params: any) => {
          const list = Array.isArray(params) ? params : [params];
          const date = list[0].name;
          const lines = list.map((p: any) => {
            let val: number | string = "-";
            if (Array.isArray(p.value)) {
              val = p.value[1];
            } else if (typeof p.value === "number") {
              val = p.value;
            }
            return `${p.marker} ${p.seriesName}: ${Number(val).toLocaleString()}`;
          });
          return `Date: ${date}<br/>${lines.join("<br/>")}`;
        },
      },
      grid: { left: "3%", right: "6%", bottom: "4%", containLabel: true },
      xAxis: {
        type: "category",
        data:
          newsTimeline?.map((d) => {
            const date = new Date(d.date);
            return date.toLocaleString("id-ID", {
              day: "numeric",
              month: "short",
              year: "numeric",
            });
          }) || [],
        axisLine: { lineStyle: { color: colors.border } },
        axisLabel: { color: colors.muted, rotate: 90 },
      },
      yAxis: [
        {
          type: "value",
          name: "Total News",
          nameLocation: "middle",
          nameGap: 90,
          nameRotate: 270,
          position: "right",
          nameTextStyle: { color: colors.muted },
          axisLine: { lineStyle: { color: colors.border } },
          axisLabel: { color: colors.muted },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: "Total News",
          type: "line",
          yAxisIndex: 0,
          data: newsTimeline?.map((d) => d.count) || [],
          smooth: true,
          lineStyle: { color: "#eba354" },
          itemStyle: { color: "#eba354" },
          areaStyle: {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: colors.primary + "4D" },
                { offset: 1, color: colors.primary + "0D" },
              ],
            },
          },
        },
      ],
    }),
    [newsTimeline, colors]
  );

  const newsTimelineCard: DetailSalesCardProps[] = [
    {
      title: "News Over Time",
      chart: <EChartsComponent option={combinedChartOption} height={410} />,
      subtitle: "Total News Published Over Time",
      icon: <AiOutlineStock />,
    },
  ];

  return (
    <article className="grid grid-cols-1">
      <NoDataWrapper show={!newsTimeline}>
        {newsTimelineCard.map((card, index) => (
          <DetailSalesCard key={index} {...card} />
        ))}
      </NoDataWrapper>
    </article>
  );
};

export default NewsTimelineArticle;
