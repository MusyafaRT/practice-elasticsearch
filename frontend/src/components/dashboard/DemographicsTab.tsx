import { AiOutlineUser, AiOutlineGlobal } from "react-icons/ai";
import DetailSalesCard, { type DetailSalesCardProps } from "./DetailSalesCard";
import * as echarts from "echarts";
import EChartsComponent from "./EChartComponent";
import type { EChartColors, ResponseWrapper } from "@/models/globalTypes";
import type {
  CustomersTrendData,
  ReqSalesTrendPgsql,
} from "@/models/analyticsTypes";
import { Skeleton } from "../ui/skeleton";
import { formatCurrency, formatCurrencyShort } from "@/lib/utils";
import { useFetchApi } from "@/hooks/useCallApi";

interface DemographicsTabProps {
  colors: EChartColors;
  start_date?: Date;
  end_date?: Date;
}

const DemographicsTab = ({ start_date, end_date }: DemographicsTabProps) => {
  const { data: customersData, isLoading: isCustomersLoading } = useFetchApi<
    ResponseWrapper<CustomersTrendData>,
    ReqSalesTrendPgsql
  >("customersTrend", {
    url: "/analytics/customers",
    method: "GET",
    params: {
      start_date: start_date,
      end_date: end_date,
    },
  });

  const ageSpendingData = customersData?.data.age_spending;
  const ageGroupData = customersData?.data.age_group;
  const categories = Array.from(new Set(ageGroupData?.map((d) => d.category)));
  const ageGroups = Array.from(new Set(ageGroupData?.map((d) => d.age_group)));

  if (isCustomersLoading) {
    return (
      <section className="grid grid-cols-2 gap-4 h-full">
        <div className="h-[388px] w-full rounded-xl border p-6 flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Skeleton className="h-6 w-1/2" />
            <Skeleton className="h-4 w-2/3" />
          </div>
          <div className="flex-1">
            <Skeleton className="h-full w-full" />
          </div>
        </div>
        <div className="h-[388px] w-full rounded-xl border p-6 flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Skeleton className="h-6 w-1/2" />
            <Skeleton className="h-4 w-2/3" />
          </div>
          <div className="flex-1">
            <Skeleton className="h-full w-full" />
          </div>
        </div>
        <Skeleton className="h-full w-full" />
      </section>
    );
  }

  const scatterPlotAgeOption: echarts.EChartsOption = {
    title: {
      text: "Age vs Spending",
      left: "center",
      top: "2%",
      textStyle: {
        fontSize: 18,
        fontWeight: "bold",
        color: "#111827",
        fontFamily: "Poppins, sans-serif",
      },
    },
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(255, 255, 255, 0.95)",
      borderColor: "#ddd",
      borderWidth: 1,
      textStyle: { color: "#111" },
      formatter: (params: any) =>
        `
        <b>Age:</b> ${params.data[0]}<br/>
        <b>Total Spending:</b> ${formatCurrency(params.data[1])}<br/>
        <b>Transactions:</b> ${params.data[2]}
      `,
    },
    xAxis: {
      name: "Age",
      type: "value",
      min: 15,
      max: 70,
      nameTextStyle: { fontWeight: "bold", color: "#374151" },
      axisLine: { lineStyle: { color: "#9CA3AF" } },
      splitLine: { lineStyle: { color: "#E5E7EB" } },
    },
    yAxis: {
      name: "Total Spending",
      type: "value",
      nameTextStyle: { fontWeight: "bold", color: "#374151" },
      axisLine: { lineStyle: { color: "#9CA3AF" } },
      splitLine: { lineStyle: { color: "#E5E7EB" } },
    },
    series: [
      {
        name: "Customers",
        type: "scatter",
        symbol: "circle",
        symbolSize: (data: any) => Math.sqrt(data[2]) * 6,
        itemStyle: {
          color: "#6366F1",
          opacity: 0.75,
          shadowBlur: 8,
          shadowColor: "rgba(99, 102, 241, 0.5)",
        },
        emphasis: {
          itemStyle: {
            borderColor: "#4338CA",
            borderWidth: 2,
            opacity: 1,
          },
        },
        data: ageSpendingData?.map((d) => [
          d.age,
          d.total_spending,
          d.transaction_count,
        ]),
      },
    ],
  };

  const heatmapAgeGroupOption: echarts.EChartsOption = {
    title: {
      text: "Age Group × Product Category",
      top: "2%",
      left: "center",
      textStyle: {
        fontSize: 18,
        fontWeight: "bold",
        color: "#111827",
        fontFamily: "Poppins, sans-serif",
      },
    },
    tooltip: {
      position: "top",
      backgroundColor: "rgba(255, 255, 255, 0.95)",
      borderColor: "#ddd",
      borderWidth: 1,
      textStyle: { color: "#111" },
      formatter: (params: any) =>
        `
        <b>Age Group:</b> ${params.data[1]}<br/>
        <b>Category:</b> ${params.data[0]}<br/>
        <b>Sales:</b> ${formatCurrency(params.data[2])}
      `,
    },
    grid: {
      left: "8%",
      right: "8%",
      bottom: "15%",
      top: "15%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: categories,
      axisLine: { lineStyle: { color: "#9CA3AF" } },
      axisLabel: {
        rotate: 30,
        color: "#374151",
        formatter: (value: string) => {
          return value.length > 5 ? value.slice(0, 5) + "…" : value;
        },
      },
      splitArea: { show: true },
    },
    yAxis: {
      type: "category",
      data: ageGroups,
      axisLine: { lineStyle: { color: "#9CA3AF" } },
      axisLabel: { color: "#374151" },
      splitArea: { show: true },
    },
    visualMap: {
      min: 0,
      max: Math.max(...(ageGroupData?.map((d) => d.total_sales) ?? [])),
      calculable: true,
      orient: "horizontal",
      left: "center",
      bottom: "-3%",
      inRange: {
        color: ["#EEF2FF", "#A5B4FC", "#4338CA"], // soft → medium → bold
      },
      formatter: (val: any) => formatCurrencyShort(val),
    },
    series: [
      {
        name: "Sales",
        type: "heatmap",
        data: ageGroupData?.map((d) => [
          d.category,
          d.age_group,
          d.total_sales,
        ]),
        label: {
          show: true,
          formatter: (params: any) => formatCurrencyShort(params.data[2]),
          color: "#111827",
          fontWeight: "bold",
        },
        emphasis: {
          itemStyle: {
            borderColor: "#1E3A8A",
            borderWidth: 2,
            shadowBlur: 10,
            shadowColor: "rgba(0,0,0,0.5)",
          },
        },
      },
    ],
  };

  const detailCards: DetailSalesCardProps[] = [
    {
      title: "Age Spending Analysis",
      chart: <EChartsComponent option={scatterPlotAgeOption} height={300} />,
      subtitle: "Customer Spending by Age",
      icon: <AiOutlineUser />,
    },
    {
      title: "Age Group Spending Analysis",
      chart: <EChartsComponent option={heatmapAgeGroupOption} height={300} />,
      subtitle: "Customer Spending by Age Group and Product Category",
      icon: <AiOutlineGlobal />,
    },
  ];

  return (
    <article className="grid grid-cols-2 gap-4 h-full">
      {detailCards.map((card, index) => (
        <DetailSalesCard key={index} {...card} />
      ))}
    </article>
  );
};

export default DemographicsTab;
