import { AiOutlineStock } from "react-icons/ai";
import * as echarts from "echarts";
import type { DetailSalesCardProps } from "./DetailSalesCard";
import EChartsComponent from "./EChartComponent";
import DetailSalesCard from "./DetailSalesCard";
import type { EChartColors, ResponseWrapper } from "@/models/globalTypes";
import type {
  ReqSalesTrendPgsql,
  SalesTrendPgsqlItem,
} from "@/models/analyticsTypes";
import { dateOnly } from "@/lib/utils";
import { addDays } from "date-fns";
import { Skeleton } from "../ui/skeleton";
import { useFetchApi } from "@/hooks/useCallApi";

interface SalesTrendTabProps {
  colors: EChartColors;
  start_date?: Date;
  end_date?: Date;
}

const SalesTrendTab = ({
  colors,
  start_date,
  end_date,
}: SalesTrendTabProps) => {
  const min_date = start_date
    ? dateOnly(start_date)
    : dateOnly(addDays(new Date(), -30));
  const max_date = end_date ? dateOnly(end_date) : dateOnly(new Date());

  const { data: salesTrendData, isLoading } = useFetchApi<
    ResponseWrapper<SalesTrendPgsqlItem[]>,
    ReqSalesTrendPgsql
  >("salesTrend", {
    url: "/analytics/sales-pgsql",
    method: "GET",
    params: {
      start_date: min_date,
      end_date: max_date,
    },
  });

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
  const salesTrendDatum = salesTrendData?.data;
  const maxTransactionsWithBuffer =
    Math.max(...(salesTrendDatum?.map((d) => d.total_transactions) ?? [])) + 10;

  const combinedChartOption: echarts.EChartsOption = {
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
            26;
            val = p.value[1]; // ambil y value kalau array
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
      data: salesTrendDatum!.map((d) => {
        const date = new Date(d.transaction_date);
        return date.toLocaleString("id-ID", {
          day: "numeric",
          month: "short",
          year: "numeric",
        });
      }),
      axisLine: { lineStyle: { color: colors.border } },
      axisLabel: { color: colors.muted, rotate: 45 },
    },
    yAxis: [
      {
        type: "value",
        name: "Total Transactions",
        nameLocation: "middle",
        position: "left",
        nameGap: 30,
        nameRotate: 90,
        max: maxTransactionsWithBuffer,
        nameTextStyle: { color: colors.muted },
        axisLine: { lineStyle: { color: colors.border } },
        axisLabel: { color: colors.muted },
        splitLine: { lineStyle: { color: colors.border } },
      },
      {
        type: "value",
        name: "Total Sales",
        nameLocation: "middle",
        max: 1000000000,
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
        name: "Total Transactions",
        type: "bar",
        yAxisIndex: 0,
        data: salesTrendDatum?.map((d) => d.total_transactions),
        itemStyle: {
          color: "#095b94",
        },
      },
      {
        name: "Total Sales",
        type: "line",
        yAxisIndex: 1,
        data: salesTrendDatum!.map((d) => d.total_sales),
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
  };

  const detailCards: DetailSalesCardProps[] = [
    {
      title: "Sales Over Time",
      chart: <EChartsComponent option={combinedChartOption} height={300} />,
      subtitle: "Monthly sales Performance",
      icon: <AiOutlineStock />,
    },
  ];

  return (
    <article className="grid grid-cols-1 h-full">
      {/* {isLoading && <Skeleton className="h-full flex" />} */}
      {detailCards.map((card, index) => (
        <DetailSalesCard key={index} {...card} />
      ))}
    </article>
  );
};

export default SalesTrendTab;
