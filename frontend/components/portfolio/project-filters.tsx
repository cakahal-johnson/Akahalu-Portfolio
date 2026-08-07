import {
  Search,
  SlidersHorizontal,
  X,
} from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"

import type {
  ProjectCategoryRead,
  ProjectTechnologyRead,
} from "@/types/portfolio"

type ProjectFiltersProps = {
  search: string
  categorySlug: string
  technologySlug: string

  categories: ProjectCategoryRead[]
  technologies: ProjectTechnologyRead[]
}

function ProjectFilters({
  search,
  categorySlug,
  technologySlug,
  categories,
  technologies,
}: ProjectFiltersProps) {
  const hasFilters =
    Boolean(search) ||
    Boolean(categorySlug) ||
    Boolean(technologySlug)

  return (
    <form
      action="/projects"
      method="get"
      className="rounded-2xl border border-border/70 bg-card p-4 sm:p-6"
    >
      <div className="flex items-center gap-2">
        <SlidersHorizontal
          className="size-4 text-primary"
          aria-hidden="true"
        />

        <h2 className="font-semibold">
          Find projects
        </h2>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[1.5fr_1fr_1fr_auto]">
        <label className="relative">
          <span className="sr-only">
            Search projects
          </span>

          <Search
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden="true"
          />

          <input
            type="search"
            name="search"
            defaultValue={search}
            placeholder="Search projects..."
            className="h-10 w-full rounded-lg border border-input bg-background pl-10 pr-3 text-sm outline-none transition-shadow placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          />
        </label>

        <label>
          <span className="sr-only">
            Project category
          </span>

          <select
            name="category"
            defaultValue={categorySlug}
            className="h-10 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            <option value="">
              All categories
            </option>

            {categories.map(
              (category) => (
                <option
                  key={category.id}
                  value={category.slug}
                >
                  {category.name}
                </option>
              )
            )}
          </select>
        </label>

        <label>
          <span className="sr-only">
            Technology
          </span>

          <select
            name="technology"
            defaultValue={technologySlug}
            className="h-10 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            <option value="">
              All technologies
            </option>

            {technologies.map(
              (technology) => (
                <option
                  key={technology.id}
                  value={technology.slug}
                >
                  {technology.name}
                </option>
              )
            )}
          </select>
        </label>

        <Button type="submit">
          Search
        </Button>
      </div>

      {hasFilters ? (
        <div className="mt-4">
          <Button
            asChild
            variant="ghost"
            size="sm"
          >
            <Link href="/projects">
              <X />

              Clear filters
            </Link>
          </Button>
        </div>
      ) : null}
    </form>
  )
}

export { ProjectFilters }