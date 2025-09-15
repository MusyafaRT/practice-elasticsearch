export interface ResponseWrapper<T> {
  status: string;
  message: string;
  data: T;
}

export interface EChartColors {
  primary: string;
  chart1: string;
  chart2: string;
  chart3: string;
  chart4: string;
  chart5: string;
  border: string;
  muted: string;
  background: string;
  popover: string;
  foreground: string;
}

export interface Metadata {
  current_page: number;
  page_size: number;
  total_pages: number;
  total_items: number;
}
