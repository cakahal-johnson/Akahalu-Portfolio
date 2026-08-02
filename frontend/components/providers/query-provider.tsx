"use client"

import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import {
  type ReactNode,
  useState,
} from "react"

import { queryClientConfig } from "@/lib/query/options"

type QueryProviderProps = {
  children: ReactNode
}

function QueryProvider({
  children,
}: QueryProviderProps) {
  const [queryClient] = useState(
    () => new QueryClient(queryClientConfig)
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

export { QueryProvider }