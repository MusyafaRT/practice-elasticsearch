import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import type { TransactionsTableItem } from "@/models/transactionsType";
import { Badge } from "../ui/badge";
import { formatCurrency } from "@/lib/utils";
import GeneralPagination from "../ui/generalPagination";
import { useState } from "react";
import { Skeleton } from "../ui/skeleton";
import useTransactionsTable from "@/hooks/useTransactionsTable";

interface TransactionsTableProps {
  search_query?: string;
  min_date?: Date;
  max_date?: Date;
  page_size?: number;
}

const TransactionTableRowSkeleton = () => {
  return (
    <TableRow>
      <TableCell>
        <Skeleton className="h-4 w-full" />
      </TableCell>
      <TableCell>
        <Skeleton className="h-4 w-full" />
      </TableCell>
      <TableCell>
        <Skeleton className="h-4 w-full" />
      </TableCell>
      <TableCell>
        <Skeleton className="h-4 w-full" />
      </TableCell>
      <TableCell>
        <Skeleton className="h-4 w-full" />
      </TableCell>
      <TableCell>
        <Skeleton className="h-4 w-full" />
      </TableCell>
      <TableCell>
        <Skeleton className="h-4 w-full" />
      </TableCell>
    </TableRow>
  );
};

const TransactionTable = (props: TransactionsTableProps) => {
  const { search_query, min_date, max_date, page_size = 5 } = props;
  const [currentPage, setCurrentPage] = useState(1);

  const { getTransactionData, isPending } = useTransactionsTable({
    page: currentPage,
    page_size: page_size,
    search_query: search_query,
    min_date: min_date,
    max_date: max_date,
  });

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  if (isPending) {
    return (
      <Table className="w-full">
        <TableHeader>
          <TableRow>
            <TableHead>Transaction ID</TableHead>
            <TableHead>Date</TableHead>
            <TableHead>Customer</TableHead>
            <TableHead>Products</TableHead>
            <TableHead>Gender</TableHead>
            <TableHead>Age</TableHead>
            <TableHead className="text-right">Amount</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.from({ length: page_size }).map((_, index) => (
            <TransactionTableRowSkeleton key={index} />
          ))}
        </TableBody>
      </Table>
    );
  }

  const transactionsData = getTransactionData?.data.items;
  console.log(transactionsData);
  const totalPages = getTransactionData?.data.metadata?.total_pages ?? 1;

  return (
    <>
      <Table className="w-full">
        <TableHeader>
          <TableRow>
            <TableHead>Transaction ID</TableHead>
            <TableHead>Date</TableHead>
            <TableHead>Customer</TableHead>
            <TableHead>Products</TableHead>
            <TableHead>Gender</TableHead>
            <TableHead>Age</TableHead>
            <TableHead className="text-right">Amount</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {transactionsData?.map((transaction: TransactionsTableItem) => (
            <TableRow
              key={transaction.transaction_id}
              className="hover:bg-muted/50"
            >
              <TableCell className="font-mono text-sm">
                {transaction.transaction_id}
              </TableCell>
              <TableCell className="text-sm">
                {new Date(transaction.transaction_date).toLocaleDateString()}
              </TableCell>
              <TableCell className="text-sm">
                {transaction.customer_name}
              </TableCell>
              <TableCell>
                <Badge variant="secondary" className="text-xs">
                  {transaction.products_name}
                </Badge>
              </TableCell>
              <TableCell className="text-sm">{transaction.gender}</TableCell>
              <TableCell className="text-sm">{transaction.age}</TableCell>
              <TableCell className="text-right font-semibold">
                {formatCurrency(transaction.total_amount)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <GeneralPagination
        currentPage={currentPage}
        totalPages={totalPages ?? 1}
        onPageChange={handlePageChange}
      />
    </>
  );
};

export default TransactionTable;
