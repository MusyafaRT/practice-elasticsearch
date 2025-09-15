import { AiOutlineBarChart, AiOutlinePieChart } from "react-icons/ai";
import DetailSalesCard, { type DetailSalesCardProps } from "./DetailSalesCard";
import * as echarts from "echarts";
import EChartsComponent from "./EChartComponent";
import type { EChartColors, ResponseWrapper } from "@/models/globalTypes";
import type {
  ProductAnalyticsItems,
  ReqSalesTrendPgsql,
} from "@/models/analyticsTypes";
import { formatCurrency } from "@/lib/utils";
import { Skeleton } from "../ui/skeleton";
import { useFetchApi } from "@/hooks/useCallApi";

interface CategoriesTabProps {
  colors: EChartColors;
  start_date?: Date;
  end_date?: Date;
}

const ProductSection = ({
  colors: colors,
  start_date,
  end_date,
}: CategoriesTabProps) => {
  const { data: productsData, isLoading } = useFetchApi<
    ResponseWrapper<ProductAnalyticsItems>,
    ReqSalesTrendPgsql
  >("productSales", {
    url: "/analytics/products",
    method: "GET",
    params: {
      start_date: start_date,
      end_date: end_date,
    },
  });

  if (isLoading) {
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
      </section>
    );
  }

  const categoriesDatum = productsData?.data.category_sales;
  const productsDatum = productsData?.data.top_sold_products;

  const categoryPieChartOption: echarts.EChartsOption = {
    tooltip: {
      trigger: "item",
      formatter: (params: any) => {
        return `${params.seriesName} <br/>${params.name}: ${formatCurrency(params.value)} (${params.percent}%)`;
      },
      backgroundColor: colors.popover,
      borderColor: colors.border,
      textStyle: { color: colors.foreground },
    },
    legend: {
      orient: "vertical",
      left: "left",
      textStyle: { color: colors.muted },
    },
    series: [
      {
        name: "Categories",
        type: "pie",
        radius: "80%",
        label: { show: false },
        labelLine: { show: false },
        data: categoriesDatum?.map((item, index) => ({
          value: item.total_sales,
          name: item.category_name,
          itemStyle: {
            color: [
              colors.chart1,
              colors.chart2,
              colors.chart3,
              colors.chart4,
              colors.chart5,
              colors.foreground,
            ][index],
          },
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: "rgba(0, 0, 0, 0.5)",
          },
        },
      },
    ],
  };

  const topSoldProductCombinedOption: echarts.EChartsOption = {
    tooltip: {
      trigger: "axis",
      formatter: (params: any) => {
        const quantity = params[0].value;
        const sales = params[1] ? params[1].value : 0;
        return `
                ${params[0].name}<br/>
                Quantity Sold: ${quantity.toLocaleString()}<br/>
                Total Sales: ${sales.toLocaleString()}
            `;
      },
      backgroundColor: colors.popover,
      borderColor: colors.border,
      textStyle: { color: colors.foreground },
    },
    grid: { left: "6%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: {
      type: "category",
      data: productsDatum?.map((d) => d.product_name),
      axisLine: { lineStyle: { color: colors.border } },
      axisLabel: { color: colors.muted },
    },
    yAxis: [
      {
        type: "value",
        name: "Quantity Sold",
        nameLocation: "middle",
        nameGap: 50,
        nameTextStyle: { color: colors.muted },
        axisLine: { lineStyle: { color: colors.border } },
        axisLabel: { color: colors.muted },
        splitLine: { lineStyle: { color: colors.border } },
      },
      {
        type: "value",
        name: "Total Sales",
        nameLocation: "middle",
        nameGap: 90,
        nameRotate: 270,
        position: "right",
        nameTextStyle: { color: colors.muted },
        axisLine: { lineStyle: { color: colors.border } },
        axisLabel: { color: colors.muted },
        splitLine: { lineStyle: { color: colors.border } },
      },
    ],
    series: [
      {
        name: "Total Quantity Sold",
        type: "bar",
        yAxisIndex: 0,
        data: productsDatum?.map((d) => ({
          value: d.total_quantity,
          name: d.product_name,
        })),
        itemStyle: {
          color: colors.chart1,
        },
        label: {
          show: true,
          position: "top",
          formatter: (params: any) => params.value.toLocaleString(),
        },
      },
      {
        name: "Total Sales",
        type: "line",
        yAxisIndex: 1,
        data: productsDatum?.map((d) => d.total_sales),
        smooth: true,
        lineStyle: { color: colors.chart2 },
        itemStyle: { color: colors.chart2 },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: colors.chart2 + "4D" },
              { offset: 1, color: colors.chart2 + "0D" },
            ],
          },
        },
      },
    ],
  };

  const detailCards: DetailSalesCardProps[] = [
    {
      title: "Sales by Category",
      chart: <EChartsComponent option={categoryPieChartOption} height={300} />,
      subtitle: "Distribution of sales across categories",
      icon: <AiOutlinePieChart />,
    },
    {
      title: "Product Performance",
      chart: (
        <EChartsComponent option={topSoldProductCombinedOption} height={300} />
      ),
      subtitle: "Top 5 products sold",
      icon: <AiOutlineBarChart />,
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

export default ProductSection;
