import type {
  ReqTransactionsTable,
  ResTransactionsTable,
} from "@/models/transactionsType";
import type { ResponseWrapper } from "@/models/globalTypes";
import { useFetchApi } from "./useCallApi";

const useTransactionsTable = ({
  page = 1,
  page_size = 5,
  search_query = "",
  min_date,
  max_date,
}: ReqTransactionsTable) => {
  const { data: getTransactionData, isPending } = useFetchApi<
    ResponseWrapper<ResTransactionsTable>,
    ReqTransactionsTable
  >(`transactionsData-${page}-${page_size}`, {
    url: "/transactions",
    method: "GET",
    params: {
      page: page,
      page_size: page_size,
      search_query: search_query,
      min_date: min_date,
      max_date: max_date,
    },
  });

  return { getTransactionData, isPending };
};

export default useTransactionsTable;
