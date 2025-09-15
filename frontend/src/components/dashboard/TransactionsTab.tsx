import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { FaSearch } from "react-icons/fa";
import { Input } from "../ui/input";
import { useDebounce } from "@/hooks/useDebounce";
import TransactionTable from "./TransactionsTable";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "../ui/button";

interface TransactionsTabProps {
  start_date?: Date;
  end_date?: Date;
}

const TransactionsTab = ({ start_date, end_date }: TransactionsTabProps) => {
  const [query, setQuery] = useState("");
  const [pageSize, setPageSize] = useState<number>(5);
  const debouncedQuery = useDebounce(query, 1000);

  useEffect(() => {
    if (debouncedQuery) {
    }
  }, [debouncedQuery]);

  const handleSelectPageSize = (size: number) => {
    setPageSize(size);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-card-foreground">
          Recent Transactions
        </CardTitle>
        <CardDescription>Latest customer transactions</CardDescription>
        <div className="flex items-center justify-between space-x-2">
          <div className="flex gap-2">
            <div className="relative flex-1 max-w-sm">
              <FaSearch className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search transactions..."
                className="pl-8"
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
          </div>
          <div>
            <DropdownMenu>
              <DropdownMenuTrigger>
                <Button
                  className="h-9 rounded-lg font-normal"
                  variant="outline"
                >
                  Page Size
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {[5, 10, 15].map((size) => (
                  <DropdownMenuItem
                    key={size}
                    onClick={() => handleSelectPageSize(size)}
                  >
                    {size}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <TransactionTable
          page_size={pageSize}
          search_query={debouncedQuery}
          min_date={start_date}
          max_date={end_date}
        />
      </CardContent>
    </Card>
  );
};

export default TransactionsTab;
