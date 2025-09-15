import NewsDashboardSkeleton from "@/components/news-dashboard/DashboardSkeleton";
import NewsStatistic from "@/components/news-dashboard/NewsStatistic";
import NewsTagDistributionArticle from "@/components/news-dashboard/NewsTagDistributionArticle";
import NewsTimelineArticle from "@/components/news-dashboard/NewsTimelineArticle";
import RecentNewsArticle from "@/components/news-dashboard/RecentNewsArticle";
import { DateRangePicker } from "@/components/ui/dateRangePicker";
import { Input } from "@/components/ui/input";
import NoDataWrapper from "@/components/ui/nodata-wrapper";
import { useFetchApi } from "@/hooks/useCallApi";
import { useDebounce } from "@/hooks/useDebounce";
import { dateOnly } from "@/lib/utils";
import { type NewsOverview, type ReqNewsTrend } from "@/models/analyticsTypes";
import type { EChartColors, ResponseWrapper } from "@/models/globalTypes";
import { addDays } from "date-fns";
import { useMemo, useState, useCallback } from "react";
import type { DateRange } from "react-day-picker";
import { FaSearch } from "react-icons/fa";

const NewsDashboardPage = () => {
  const [dateRange, setDateRange] = useState<DateRange>({
    from: new Date("2023-01-01T00:00:00Z"),
    to: new Date("2023-12-10T00:00:59Z"),
  });
  const [query, setQuery] = useState("");

  const min_date = dateRange?.from
    ? dateOnly(dateRange.from)
    : dateOnly(addDays(new Date(), -30));
  const max_date = dateRange?.to
    ? dateOnly(dateRange.to)
    : dateOnly(new Date());

  const debouncedQuery = useDebounce(query, 1000);

  const params: ReqNewsTrend = useMemo(
    () => ({
      search_query: debouncedQuery,
      start_date: min_date,
      end_date: max_date,
    }),
    [debouncedQuery, min_date, max_date]
  );

  const { data: newsDashboardData, isLoading } = useFetchApi<
    ResponseWrapper<NewsOverview>,
    ReqNewsTrend
  >("newsTrend", {
    url: "/analytics/news",
    method: "GET",
    params: params,
  });

  // Memoize the dashboard data to prevent unnecessary re-renders
  const newsDashboardDatum = useMemo(() => {
    return newsDashboardData?.data;
  }, [newsDashboardData]);

  // Memoize colors object to prevent recreation on every render
  const colors: EChartColors = useMemo(
    () => ({
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
    }),
    []
  );

  const handleDateChange = useCallback((newDate: DateRange | undefined) => {
    if (!newDate) return;
    setDateRange(newDate);
  }, []);

  const handleQueryChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setQuery(e.target.value);
    },
    []
  );

  return (
    <section className="mx-auto px-6 flex flex-col gap-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">News Dashboard</h1>
          <p>Welcome to the news dashboard!</p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="relative flex-1 max-w-sm">
            <FaSearch className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search news..."
              className="pl-8"
              onChange={handleQueryChange}
              value={query}
            />
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
      </div>

      {!newsDashboardData ? (
        isLoading ? (
          <NewsDashboardSkeleton />
        ) : (
          <section className="mx-auto px-6 flex flex-col items-center justify-center h-[400px] text-center">
            <h2 className="text-xl font-semibold text-muted-foreground">
              No Data Available
            </h2>
            <p className="text-sm text-muted-foreground">
              Try adjusting your filters or search query.
            </p>
          </section>
        )
      ) : (
        <NoDataWrapper
          show={
            !newsDashboardDatum?.tag_distribution ||
            !newsDashboardDatum?.timeline ||
            !newsDashboardDatum?.statistics
          }
        >
          <div className="grid grid-cols-12 gap-6 my-3">
            <div className="col-span-12">
              <NewsStatistic
                statistics={newsDashboardDatum!.statistics}
                isLoading={isLoading}
              />
            </div>

            <div className="col-span-8">
              <NewsTimelineArticle
                colors={colors}
                newsTimeline={newsDashboardDatum?.timeline}
                isLoading={isLoading}
              />
            </div>

            <div className="col-span-4 row-span-2">
              <RecentNewsArticle
                start_date={min_date}
                end_date={max_date}
                search_query={debouncedQuery}
              />
            </div>

            <div className="col-span-8">
              <NewsTagDistributionArticle
                tagDistributionData={newsDashboardDatum?.tag_distribution ?? []}
                isLoading={isLoading}
              />
            </div>
          </div>
        </NoDataWrapper>
      )}
    </section>
  );
};

export default NewsDashboardPage;
