import type { NewsStatistics } from "@/models/analyticsTypes";
import SalesCard from "../dashboard/SalesCard";
import { GiSummits } from "react-icons/gi";
import { FaCalendarAlt, FaTags, FaUserAlt } from "react-icons/fa";
import NoDataWrapper from "../ui/nodata-wrapper";

interface NewsStatisticProps {
  statistics: NewsStatistics;
  isLoading: boolean;
}

const NewsStatistic = ({ statistics, isLoading }: NewsStatisticProps) => {
  if (isLoading) {
    return <div>Loading statistics...</div>;
  }

  const { total_articles, unique_authors, unique_tags, date_range } =
    statistics;

  return (
    <div className="grid grid-cols-4 gap-2">
      <NoDataWrapper show={!statistics}>
        <SalesCard
          title="Total News"
          amount={total_articles.toLocaleString()}
          subtitle="Total artikel dalam sistem"
          icon={<GiSummits />}
        />
        <SalesCard
          title="Unique Authors"
          amount={unique_authors}
          subtitle="Jumlah penulis berbeda"
          icon={<FaUserAlt />}
        />
        <SalesCard
          title="Unique Tags"
          amount={unique_tags.toLocaleString()}
          subtitle="Jumlah tag berbeda"
          icon={<FaTags />}
        />
        <SalesCard
          title="Date Range"
          amount={
            date_range?.earliest && date_range?.latest
              ? `${new Date(date_range.earliest).toLocaleDateString()} - ${new Date(
                  date_range.latest
                ).toLocaleDateString()}`
              : "No date available"
          }
          subtitle="Rentang waktu data"
          icon={<FaCalendarAlt />}
        />
      </NoDataWrapper>
    </div>
  );
};

export default NewsStatistic;
