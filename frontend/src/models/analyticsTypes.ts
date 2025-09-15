export interface AnalyticsData<T> {
  count: number;
  items: T[];
}

export interface SalesAnalyticsItem {
  month: Date;
  total_sales: number;
  transactions_count: number;
}

export interface SalesTrendPgsqlItem {
  transaction_date: Date;
  total_sales: number;
  total_transactions: number;
}

export interface ReqSalesTrendPgsql {
  start_date: Date;
  end_date: Date;
}

export interface ProductAnalyticsItems {
  category_sales: CategorySale[];
  top_sold_products: TopSoldProduct[];
}

export interface CategorySale {
  category_name: string;
  total_quantity: number;
  total_sales: number;
}

export interface TopSoldProduct {
  product_name: string;
  total_quantity: number;
  total_sales: number;
}

export interface AgeGroupItem {
  age_group: string;
  customers: number;
  sales: number;
}

export interface CustomersTrendData {
  age_spending: AgeSpending[];
  age_group: AgeGroupElement[];
}

export interface AgeGroupElement {
  age_group: string;
  category: string;
  total_sales: number;
}

export interface AgeSpending {
  age: number;
  total_spending: number;
  transaction_count: number;
}

export interface CustomersGenderItem {
  category: string;
  gender: string;
  customers: number;
  total_items: number;
}

export interface PeriodSummaryData {
  status: string;
  message: string;
  data: SummaryData;
}

export interface SummaryData {
  sales_summary: Summary;
  orders_summary: Summary;
  revenue_summary: Summary;
  aov_summary: Summary;
}

export interface Summary {
  summary_title: string;
  current_period: number;
  previous_period: number;
  growth: number;
}

export interface NewsOverview {
  statistics: NewsStatistics;
  top_title_keywords: NewsTopTitleKeyword[];
  tag_distribution: NewsTagDistribution[];
  timeline: NewsTimeline[];
  top_keywords: NewsTopKeyword[];
}

export interface ReqNewsOverview extends ReqNewsTrend {
  search_after: string;
}

export interface NewsRecentItems {
  title: string;
  author: string;
  url: string;
  main_image?: string;
  tag: string[];
  publish_date: Date;
}

export interface ResRecentNews {
  items: NewsRecentItems[];
  next_search_after: string;
}

export interface NewsStatistics {
  total_articles: number;
  unique_authors: number;
  unique_tags: number;
  date_range: DateRange;
}

export interface DateRange {
  earliest: Date;
  latest: Date;
}

export interface NewsTagDistribution {
  tag: string;
  count: number;
}

export interface NewsTimeline {
  date: Date;
  count: number;
}

export interface NewsTopKeyword {
  keyword: string;
  count: number;
  percent: number;
}

export interface NewsTopTitleKeyword {
  keyword: string;
  count: number;
}

export interface ReqNewsTrend {
  search_query: string;
  start_date: Date;
  end_date: Date;
}
