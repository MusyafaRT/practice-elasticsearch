import { useInfiniteFetchApi } from "@/hooks/useCallApi";
import { format } from "date-fns";
import { useCallback, useRef } from "react";

interface RecentNewsArticleProps {
  start_date?: Date;
  end_date?: Date;
  search_query?: string;
}

interface RecentNewsRowsProps {
  date: Date;
  count: number;
  title: string;
  url: string;
}

const RecentNewsRows = ({ date, count, title, url }: RecentNewsRowsProps) => {
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center justify-between p-4 rounded-lg border border-gray-200 hover:shadow-lg transition-shadow duration-300 bg-white"
    >
      <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-blue-100 text-blue-700 font-semibold rounded-full">
        {count}
      </div>

      <div className="flex-1 px-4 flex flex-col gap-1">
        <div className="text-gray-900 font-medium text-base hover:text-blue-600 transition-colors">
          {title}
        </div>
        <div className="text-gray-500 text-xs">
          {format(new Date(date), "MMM dd, yyyy")}
        </div>
      </div>

      <div className="flex-shrink-0 text-gray-400 hover:text-blue-500 transition-colors">
        🔗
      </div>
    </a>
  );
};

const RecentNewsArticle = ({
  start_date,
  end_date,
  search_query,
}: RecentNewsArticleProps) => {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
    error,
  } = useInfiniteFetchApi(
    "recent-news",
    {
      url: "/analytics/news/recent",
      params: (pageParam) => ({
        size: 10,
        search_after: pageParam || undefined,
        start_date: start_date,
        end_date: end_date,
        // search_query: search_query,
      }),
    },
    {
      getNextPageParam: (lastPage) => {
        return lastPage.data?.next_search_after || undefined;
      },
      initialPageParam: null,
    }
  );

  const newsList = data?.pages.flatMap((page) => page.data.items) ?? [];

  const observer = useRef<IntersectionObserver | null>(null);
  const lastNewsRef = useCallback(
    (node: HTMLDivElement | null) => {
      if (isLoading || isFetchingNextPage) return;
      if (observer.current) observer.current.disconnect();

      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasNextPage) {
          fetchNextPage();
        }
      });

      if (node) observer.current.observe(node);
    },
    [isLoading, isFetchingNextPage, hasNextPage, fetchNextPage]
  );

  if (isLoading) {
    return (
      <div className="h-full w-full rounded-xl border p-6 flex flex-col gap-3">
        <h2 className="text-lg font-semibold text-gray-900">Recent News</h2>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="h-full w-full rounded-xl border p-6 flex flex-col gap-3">
        <h2 className="text-lg font-semibold text-gray-900">Recent News</h2>
        <div className="flex items-center justify-center py-8">
          <div className="text-red-600 text-center">
            <p>Failed to load news</p>
            <p className="text-sm text-gray-500 mt-1">
              {error?.message || "Something went wrong"}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (newsList.length === 0) {
    return (
      <div className="h-full w-full rounded-xl border p-6 flex flex-col gap-3">
        <h2 className="text-lg font-semibold text-gray-900">Recent News</h2>
        <div className="flex items-center justify-center py-8">
          <p className="text-gray-500">No news articles found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full rounded-xl border p-6 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Recent News</h2>
        <span className="text-sm text-gray-500">
          {newsList.length} articles
        </span>
      </div>

      {/* News List */}
      <div className="flex flex-col gap-3 flex-1 overflow-y-auto max-h-[1050px]">
        {newsList.map((news, index) => (
          <div key={index} ref={lastNewsRef}>
            <RecentNewsRows
              count={index + 1}
              date={news.publish_date}
              title={news.title}
              url={news.url}
              key={`${news.url}-${index}`} // Better key using unique identifier
            />
          </div>
        ))}
      </div>

      {/* Load More Button */}
      {/* {hasNextPage && (
        <div className="flex justify-center pt-4 border-t">
          <button
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isFetchingNextPage ? (
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Loading...
              </div>
            ) : (
              "Load More"
            )}
          </button>
        </div>
      )} */}
    </div>
  );
};

export default RecentNewsArticle;
