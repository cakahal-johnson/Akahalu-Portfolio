"use client"

import {
  ChevronLeft,
  ChevronRight,
} from "lucide-react"

import { Button } from "@/components/ui/button"

type AdminProjectPaginationProps = {
  page: number
  totalPages: number
  totalItems: number

  hasNextPage: boolean
  hasPreviousPage: boolean

  onPageChange: (
    page: number
  ) => void
}

export function AdminProjectPagination({
  page,
  totalPages,
  totalItems,
  hasNextPage,
  hasPreviousPage,
  onPageChange,
}: AdminProjectPaginationProps) {
  if (
    totalItems === 0
  ) {
    return null
  }

  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-border bg-background p-4 sm:flex-row sm:items-center sm:justify-between">
      <p className="text-sm text-muted-foreground">
        Page{" "}
        <strong className="text-foreground">
          {page}
        </strong>{" "}
        of{" "}
        <strong className="text-foreground">
          {Math.max(
            totalPages,
            1
          )}
        </strong>
        {" · "}
        {totalItems} project
        {totalItems === 1
          ? ""
          : "s"}
      </p>

      <div className="flex gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={
            !hasPreviousPage
          }
          onClick={() =>
            onPageChange(
              page - 1
            )
          }
        >
          <ChevronLeft
            aria-hidden="true"
          />

          Previous
        </Button>

        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={
            !hasNextPage
          }
          onClick={() =>
            onPageChange(
              page + 1
            )
          }
        >
          Next

          <ChevronRight
            aria-hidden="true"
          />
        </Button>
      </div>
    </div>
  )
}