import {
  Search,
  SlidersHorizontal,
  X,
} from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"

type ExperienceFiltersProps = {
  search: string
  employmentType: string
  locationType: string
  current: string
}

function ExperienceFilters({
  search,
  employmentType,
  locationType,
  current,
}: ExperienceFiltersProps) {
  const hasFilters =
    Boolean(search) ||
    Boolean(employmentType) ||
    Boolean(locationType) ||
    Boolean(current)

  return (
    <form
      action="/experience"
      method="get"
      className="rounded-2xl border border-border/70 bg-card p-4 sm:p-6"
    >
      <div className="flex items-center gap-2">
        <SlidersHorizontal
          className="size-4 text-primary"
          aria-hidden="true"
        />

        <h2 className="font-semibold">
          Filter experience
        </h2>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[1.4fr_1fr_1fr_1fr_auto]">
        <label className="relative">
          <span className="sr-only">
            Search experience
          </span>

          <Search
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden="true"
          />

          <input
            type="search"
            name="search"
            defaultValue={search}
            placeholder="Search roles or companies..."
            className="h-10 w-full rounded-lg border border-input bg-background pl-10 pr-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          />
        </label>

        <select
          name="employment"
          defaultValue={employmentType}
          aria-label="Employment type"
          className="h-10 rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
        >
          <option value="">
            All employment
          </option>

          <option value="full_time">
            Full-time
          </option>

          <option value="part_time">
            Part-time
          </option>

          <option value="contract">
            Contract
          </option>

          <option value="freelance">
            Freelance
          </option>

          <option value="internship">
            Internship
          </option>

          <option value="self_employed">
            Self-employed
          </option>

          <option value="volunteer">
            Volunteer
          </option>
        </select>

        <select
          name="location"
          defaultValue={locationType}
          aria-label="Location type"
          className="h-10 rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
        >
          <option value="">
            All locations
          </option>

          <option value="onsite">
            On-site
          </option>

          <option value="remote">
            Remote
          </option>

          <option value="hybrid">
            Hybrid
          </option>
        </select>

        <select
          name="current"
          defaultValue={current}
          aria-label="Current position"
          className="h-10 rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
        >
          <option value="">
            All roles
          </option>

          <option value="true">
            Current
          </option>

          <option value="false">
            Previous
          </option>
        </select>

        <Button type="submit">
          Apply
        </Button>
      </div>

      {hasFilters ? (
        <div className="mt-4">
          <Button
            asChild
            size="sm"
            variant="ghost"
          >
            <Link href="/experience">
              <X />

              Clear filters
            </Link>
          </Button>
        </div>
      ) : null}
    </form>
  )
}

export { ExperienceFilters }