import { FaMoneyBill } from "react-icons/fa";
import SalesCard from "../../components/dashboard/SalesCard";
import DemographicsTab from "../../components/dashboard/DemographicsTab";
import TransactionsTab from "../../components/dashboard/TransactionsTab";
import type { EChartColors, ResponseWrapper } from "@/models/globalTypes";
import SalesTrendTab from "@/components/dashboard/SalesTrendTab";
import { DateRangePicker } from "@/components/ui/dateRangePicker";
import { Skeleton } from "@/components/ui/skeleton";
import { useState } from "react";
import type { DateRange } from "react-day-picker";
import { dateOnly, formatCurrency, formatCurrencyShort } from "@/lib/utils";
import { addDays } from "date-fns";
import ProductSection from "@/components/dashboard/ProductSection";
import { useFetchApi } from "@/hooks/useCallApi";
import type { ReqSalesTrendPgsql, SummaryData } from "@/models/analyticsTypes";

const DashboardPage = () => {
  const [dateRange, setDateRange] = useState<DateRange | undefined>();

  const min_date = dateRange?.from
    ? dateOnly(dateRange.from)
    : dateOnly(addDays(new Date(), -30));
  const max_date = dateRange?.to
    ? dateOnly(dateRange.to)
    : dateOnly(new Date());

  const { data: summaryData, isLoading } = useFetchApi<
    ResponseWrapper<SummaryData>,
    ReqSalesTrendPgsql
  >("salesTrend", {
    url: "/analytics/summary",
    method: "GET",
    params: {
      start_date: min_date,
      end_date: max_date,
    },
  });
  const colors: EChartColors = {
    primary: "#0ea5e9",
    chart1: "#0ea5e9",
    chart2: "#8b5cf6",
    chart3: "#10b981",
    chart4: "#f59e0b",
    chart5: "#ef4444",
    border: "#e2e8f0",
    muted: "#64748b",
    background: "#ffffff",
    popover: "#ffffff",
    foreground: "#0f172a",
  };

  const summaryArray = [
    {
      title: "Products Sold",
      amount: summaryData?.data?.sales_summary?.current_period ?? 0,
      ...summaryData?.data?.sales_summary,
      icon: <FaMoneyBill />,
    },
    {
      title: "Orders",
      amount: summaryData?.data?.orders_summary?.current_period ?? 0,
      ...summaryData?.data?.orders_summary,
      icon: <FaMoneyBill />,
    },
    {
      title: "Revenue",
      amount: formatCurrency(
        summaryData?.data?.revenue_summary?.current_period ?? 0.0
      ),
      ...summaryData?.data?.revenue_summary,
      icon: <FaMoneyBill />,
    },
    {
      title: "AOV",
      amount: formatCurrency(
        summaryData?.data?.aov_summary?.current_period ?? 0.0
      ),
      ...summaryData?.data?.aov_summary,
      icon: <FaMoneyBill />,
    },
  ];

  const handleDateChange = (newDate: DateRange | undefined) => {
    setDateRange(newDate);
  };

  return (
    <section className="mx-auto px-6">
      <div className="flex justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p>Welcome to your dashboard!</p>
        </div>
        <DateRangePicker
          date={dateRange}
          onDateChange={handleDateChange}
          disabledFutureDays={true}
          side="bottom"
          alignContent="end"
          className="flex items-center"
        />
      </div>
      <article className="grid grid-cols-4 gap-3 mt-6">
        {isLoading
          ? Array.from({ length: 4 }).map((_, index) => (
              <SalesCard
                key={index}
                title={<Skeleton className="h-4 w-24" />}
                amount={<Skeleton className="h-6 w-32" />}
                subtitle={<Skeleton className="h-3 w-48" />}
                icon={<Skeleton className="h-8 w-8" />}
              />
            ))
          : summaryArray.map((sum, index) => (
              <SalesCard
                key={index}
                title={sum.title}
                amount={sum.current_period ?? 0}
                subtitle={`${sum.growth}% change from ${formatCurrencyShort(
                  sum.previous_period ?? 0.0
                )}`}
                subtitleColors={
                  (sum.growth ?? 0) > 0 ? "text-green-500" : "text-red-500"
                }
                icon={sum.icon}
              />
            ))}
      </article>
      <div className="flex flex-col gap-4 my-4">
        <SalesTrendTab
          colors={colors}
          start_date={dateRange?.from}
          end_date={dateRange?.to}
        />
        <ProductSection
          colors={colors}
          start_date={min_date}
          end_date={max_date}
        />
        <DemographicsTab
          colors={colors}
          start_date={min_date}
          end_date={max_date}
        />
        <TransactionsTab start_date={min_date} end_date={max_date} />
      </div>
    </section>
  );
};

export default DashboardPage;
