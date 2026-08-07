import {
  ArrowLeft,
  ArrowRight,
} from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"

type ProjectPaginationProps = {
  page: number
  totalPages: number

  search?: string
  categorySlug?: string
  technologySlug?: string
}

function createPageHref({
  page,
  search,
  categorySlug,
  technologySlug,
}: {
  page: number
  search?: string
  categorySlug?: string
  technologySlug?: string
}): string {
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

  if (categorySlug) {
    params.set(
      "category",
      categorySlug
    )
  }

  if (technologySlug) {
    params.set(
      "technology",
      technologySlug
    )
  }

  const query =
    params.toString()

  return query
    ? `/projects?${query}`
    : "/projects"
}

function ProjectPagination({
  page,
  totalPages,
  search,
  categorySlug,
  technologySlug,
}: ProjectPaginationProps) {
  if (totalPages <= 1) {
    return null
  }

  const previousHref =
    createPageHref({
      page: page - 1,
      search,
      categorySlug,
      technologySlug,
    })

  const nextHref =
    createPageHref({
      page: page + 1,
      search,
      categorySlug,
      technologySlug,
    })

  return (
    <nav
      className="mt-12 flex items-center justify-between gap-4"
      aria-label="Project pagination"
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
          href={previousHref}
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
          href={nextHref}
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

export { ProjectPagination }