// src/services/api.ts
import axiosInstance, { BASE_URL } from "@/api/api";
import {
  useQuery,
  useMutation,
  useInfiniteQuery,
  type UseQueryOptions,
  type UseMutationOptions,
  type UseMutationResult,
  type UseInfiniteQueryOptions,
  type InfiniteData,
} from "@tanstack/react-query";
import {
  type AxiosRequestConfig,
  type AxiosResponse,
  type Method,
} from "axios";
import qs from "qs";

interface APIOptions {
  method: Method;
  isMultipart?: boolean;
  isBlob?: boolean;
  timeout?: number;
  headers?: Record<string, string>;
}

type FetchParams<T = any, P = Record<string, any>> = {
  url: string;
  method?: Method;
  data?: T;
  params?: P;
  options?: APIOptions;
};

async function apiFetcher<
  ResponseType = any,
  RequestType = any,
  ParamsType = Record<string, any>,
>({
  url,
  method = "GET",
  data,
  params,
  options,
}: FetchParams<RequestType, ParamsType>): Promise<ResponseType> {
  try {
    const apiUrl = BASE_URL + url;
    const timeout = options?.timeout || 1000;

    const config: AxiosRequestConfig = {
      url: params ? `${apiUrl}?${qs.stringify(params)}` : apiUrl,
      method,
      data,
      timeout,
      responseType: options?.isBlob ? "blob" : "json",
      headers: {
        ...options?.headers,
      },
    };

    const response: AxiosResponse<ResponseType> = await axiosInstance(config);

    return response.data;
  } catch (error) {
    throw error;
  }
}

export function useFetchApi<
  ResponseType = any,
  RequestType = any,
  ParamsType = Record<string, any>,
>(
  key: string,
  fetchParams: FetchParams<RequestType, ParamsType>,
  queryOptions?: UseQueryOptions<ResponseType, Error, ResponseType>
) {
  return useQuery<ResponseType, Error, ResponseType>({
    queryKey: [key, fetchParams],
    queryFn: () =>
      apiFetcher<ResponseType, RequestType, ParamsType>(fetchParams),
    retry: 2,
    staleTime: 5 * 60 * 1000,
    ...queryOptions,
  });
}

interface PaginationConfig<T = any> {
  getNextPageParam?: (lastPage: T, allPages: T[]) => unknown;
  getPreviousPageParam?: (firstPage: T, allPages: T[]) => unknown;
  initialPageParam?: unknown;
}

export function useInfiniteFetchApi<
  ResponseType = any,
  RequestType = any,
  ParamsType = Record<string, any>,
>(
  key: string,
  fetchParams: Omit<FetchParams<RequestType, ParamsType>, "params"> & {
    params?: (pageParam: unknown) => ParamsType;
  },
  paginationConfig?: PaginationConfig<ResponseType>,
  queryOptions?: Omit<
    UseInfiniteQueryOptions<
      ResponseType,
      Error,
      InfiniteData<ResponseType>,
      string[]
    >,
    | "queryKey"
    | "queryFn"
    | "getNextPageParam"
    | "getPreviousPageParam"
    | "initialPageParam"
  >
) {
  const {
    getNextPageParam = (lastPage: any) => {
      if (lastPage?.data?.next_search_after) {
        return lastPage.data.next_search_after;
      }

      if (lastPage?.nextCursor || lastPage?.next_cursor) {
        return lastPage.nextCursor || lastPage.next_cursor;
      }

      if (lastPage?.hasMore === false || lastPage?.next_page === null) {
        return undefined;
      }
      if (lastPage?.next_page !== undefined) {
        return lastPage.next_page;
      }

      const items = lastPage?.data?.items || lastPage?.items || lastPage?.data;
      if (Array.isArray(items) && items.length === 0) {
        return undefined;
      }

      return undefined;
    },
    getPreviousPageParam = (firstPage: any) => {
      if (firstPage?.previousCursor || firstPage?.prev_cursor) {
        return firstPage.previousCursor || firstPage.prev_cursor;
      }
      return undefined;
    },
    initialPageParam = null,
  } = paginationConfig || {};

  return useInfiniteQuery<
    ResponseType,
    Error,
    InfiniteData<ResponseType>,
    string[]
  >({
    queryKey: [
      key,
      fetchParams.url,
      fetchParams.method || "GET",
      JSON.stringify(fetchParams.data || null),
    ],
    queryFn: ({ pageParam = initialPageParam }) => {
      const params =
        typeof fetchParams.params === "function"
          ? fetchParams.params(pageParam)
          : undefined;

      return apiFetcher<ResponseType, RequestType, ParamsType>({
        ...fetchParams,
        params,
      });
    },
    retry: 2,
    staleTime: 5 * 60 * 1000,
    initialPageParam,
    getNextPageParam,
    getPreviousPageParam,
    ...queryOptions,
  });
}

export function useMutateApi<
  ResponseType = any,
  RequestType = any,
  ParamsType = Record<string, any>,
>(
  mutationOptions?: UseMutationOptions<
    ResponseType,
    Error,
    FetchParams<RequestType, ParamsType>
  >
): UseMutationResult<
  ResponseType,
  Error,
  FetchParams<RequestType, ParamsType>
> {
  return useMutation<ResponseType, Error, FetchParams<RequestType, ParamsType>>(
    {
      mutationFn: (fetchParams) =>
        apiFetcher<ResponseType, RequestType, ParamsType>(fetchParams),
      ...mutationOptions,
    }
  );
}

export const apiService = {
  get: async <ResponseType = any, ParamsType = Record<string, any>>(
    url: string,
    params?: ParamsType,
    options?: Omit<APIOptions, "method">
  ) => {
    return apiFetcher<ResponseType, never, ParamsType>({
      url,
      method: "GET",
      params,
      options: { ...options, method: "GET" },
    });
  },

  post: async <ResponseType = any, RequestType = any>(
    url: string,
    data?: RequestType,
    options?: Omit<APIOptions, "method">
  ) => {
    return apiFetcher<ResponseType, RequestType>({
      url,
      method: "POST",
      data,
      options: { ...options, method: "POST" },
    });
  },

  put: async <ResponseType = any, RequestType = any>(
    url: string,
    data?: RequestType,
    options?: Omit<APIOptions, "method">
  ) => {
    return apiFetcher<ResponseType, RequestType>({
      url,
      method: "PUT",
      data,
      options: { ...options, method: "PUT" },
    });
  },

  delete: async <ResponseType = any, ParamsType = Record<string, any>>(
    url: string,
    params?: ParamsType,
    options?: Omit<APIOptions, "method">
  ) => {
    return apiFetcher<ResponseType, never, ParamsType>({
      url,
      method: "DELETE",
      params,
      options: { ...options, method: "DELETE" },
    });
  },
};
