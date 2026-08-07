import {
  ArrowLeft,
  ArrowRight,
} from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"

type ExperiencePaginationProps = {
  page: number
  totalPages: number
  search?: string
  employmentType?: string
  locationType?: string
  current?: string
}

function createHref({
  page,
  search,
  employmentType,
  locationType,
  current,
}: ExperiencePaginationProps): string {
  const params =
    new URLSearchParams()

  if (page > 1) {
    params.set(
      "page",
      String(page)
    )
  }

  if (search) {
    params.set(
      "search",
      search
    )
  }

  if (employmentType) {
    params.set(
      "employment",
      employmentType
    )
  }

  if (locationType) {
    params.set(
      "location",
      locationType
    )
  }

  if (current) {
    params.set(
      "current",
      current
    )
  }

  const query =
    params.toString()

  return query
    ? `/experience?${query}`
    : "/experience"
}

function ExperiencePagination(
  props: ExperiencePaginationProps
) {
  const {
    page,
    totalPages,
  } = props

  if (totalPages <= 1) {
    return null
  }

  return (
    <nav
      aria-label="Experience pagination"
      className="mt-12 flex items-center justify-between gap-4"
    >
      <Button
        asChild
        variant="outline"
        className={
          page <= 1
            ? "pointer-events-none opacity-50"
            : undefined
        }
      >
        <Link
          href={createHref({
            ...props,
            page: page - 1,
          })}
          aria-disabled={
            page <= 1
          }
        >
          <ArrowLeft />

          Previous
        </Link>
      </Button>

      <p className="text-sm text-muted-foreground">
        Page{" "}
        <span className="font-medium text-foreground">
          {page}
        </span>{" "}
        of{" "}
        <span className="font-medium text-foreground">
          {totalPages}
        </span>
      </p>

      <Button
        asChild
        variant="outline"
        className={
          page >= totalPages
            ? "pointer-events-none opacity-50"
            : undefined
        }
      >
        <Link
          href={createHref({
            ...props,
            page: page + 1,
          })}
          aria-disabled={
            page >= totalPages
          }
        >
          Next

          <ArrowRight />
        </Link>
      </Button>
    </nav>
  )
}

export { ExperiencePagination }