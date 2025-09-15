import type { Metadata } from "./globalTypes";

export interface ReqTransactionsTable {
  page: number;
  page_size: number;
  search_query?: string;
  min_date?: Date;
  max_date?: Date;
}

export interface ResTransactionsTable {
  items: TransactionsTableItem[];
  metadata: Metadata;
}

export type Gender = "FEMALE" | "MALE";

export interface TransactionsTableItem {
  transaction_id: string;
  transaction_date: Date;
  products_name: string;
  customer_name: string;
  gender: Gender;
  age: number;
  total_amount: number;
}
