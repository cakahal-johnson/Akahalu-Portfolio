import type {
  DefaultOptions,
  QueryClientConfig,
} from "@tanstack/react-query"

import { ApiError } from "@/lib/api/errors"

const defaultQueryOptions: DefaultOptions = {
  queries: {
    staleTime: 60_000,
    gcTime: 5 * 60_000,

    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
    refetchOnMount: false,

    retry(failureCount, error) {
      if (
        error instanceof ApiError &&
        error.status !== null &&
        error.status >= 400 &&
        error.status < 500
      ) {
        return false
      }

      return failureCount < 2
    },
  },

  mutations: {
    retry: false,
  },
}

export const queryClientConfig: QueryClientConfig = {
  defaultOptions: defaultQueryOptions,
}