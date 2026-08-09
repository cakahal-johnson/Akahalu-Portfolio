"use client"

import {
  RotateCcw,
  Search,
  SlidersHorizontal,
} from "lucide-react"

import {
  Button,
} from "@/components/ui/button"

import {
  type ExperienceAdminFilterState,
} from "@/components/admin/experiences/experience-admin-filters"

type AdminExperienceFiltersProps = {
  filters:
    ExperienceAdminFilterState

  onChange: (
    filters:
      ExperienceAdminFilterState
  ) => void

  onReset: () => void
}

export function AdminExperienceFilters({
  filters,
  onChange,
  onReset,
}: AdminExperienceFiltersProps) {
  function update<
    TKey extends keyof ExperienceAdminFilterState,
  >(
    key:
      TKey,
    value:
      ExperienceAdminFilterState[TKey]
  ) {
    onChange({
      ...filters,
      [key]:
        value,
    })
  }

  return (
    <section className="rounded-2xl border border-border bg-background p-4 sm:p-5">
      <div className="flex items-center gap-2">
        <SlidersHorizontal
          className="size-4 text-muted-foreground"
          aria-hidden="true"
        />

        <h2 className="font-medium">
          Filters
        </h2>
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-4">
        <label className="block xl:col-span-2">
          <span className="text-xs font-medium text-muted-foreground">
            Search
          </span>

          <div className="relative mt-2">
            <Search
              className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
              aria-hidden="true"
            />

            <input
              type="search"
              value={
                filters.search
              }
              onChange={(event) =>
                update(
                  "search",
                  event.target.value
                )
              }
              placeholder="Search company, title, location or experience content"
              className="h-10 w-full rounded-lg border border-input bg-background pl-9 pr-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </div>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-muted-foreground">
            Employment
          </span>

          <select
            value={
              filters.employmentType
            }
            onChange={(event) =>
              update(
                "employmentType",
                event.target
                  .value as ExperienceAdminFilterState["employmentType"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="all">
              All types
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

            <option value="apprenticeship">
              Apprenticeship
            </option>

            <option value="temporary">
              Temporary
            </option>

            <option value="volunteer">
              Volunteer
            </option>

            <option value="self_employed">
              Self-employed
            </option>

            <option value="other">
              Other
            </option>
          </select>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-muted-foreground">
            Location type
          </span>

          <select
            value={
              filters.locationType
            }
            onChange={(event) =>
              update(
                "locationType",
                event.target
                  .value as ExperienceAdminFilterState["locationType"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="all">
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
        </label>

        <label className="block">
          <span className="text-xs font-medium text-muted-foreground">
            Position
          </span>

          <select
            value={
              filters.current
            }
            onChange={(event) =>
              update(
                "current",
                event.target
                  .value as ExperienceAdminFilterState["current"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="all">
              Current + completed
            </option>

            <option value="yes">
              Current
            </option>

            <option value="no">
              Completed
            </option>
          </select>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-muted-foreground">
            Visibility
          </span>

          <select
            value={
              filters.visibility
            }
            onChange={(event) =>
              update(
                "visibility",
                event.target
                  .value as ExperienceAdminFilterState["visibility"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="all">
              Public + private
            </option>

            <option value="yes">
              Public
            </option>

            <option value="no">
              Private
            </option>
          </select>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-muted-foreground">
            Featured
          </span>

          <select
            value={
              filters.featured
            }
            onChange={(event) =>
              update(
                "featured",
                event.target
                  .value as ExperienceAdminFilterState["featured"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="all">
              All
            </option>

            <option value="yes">
              Featured
            </option>

            <option value="no">
              Not featured
            </option>
          </select>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-muted-foreground">
            Sort by
          </span>

          <select
            value={
              filters.sortBy
            }
            onChange={(event) =>
              update(
                "sortBy",
                event.target
                  .value as ExperienceAdminFilterState["sortBy"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="start_date">
              Start date
            </option>

            <option value="end_date">
              End date
            </option>

            <option value="company_name">
              Company
            </option>

            <option value="job_title">
              Job title
            </option>

            <option value="slug">
              Slug
            </option>

            <option value="employment_type">
              Employment type
            </option>

            <option value="location_type">
              Location type
            </option>

            <option value="is_current">
              Current status
            </option>

            <option value="is_public">
              Visibility
            </option>

            <option value="is_featured">
              Featured
            </option>

            <option value="sort_order">
              Sort order
            </option>

            <option value="created_at">
              Created
            </option>

            <option value="updated_at">
              Updated
            </option>
          </select>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-muted-foreground">
            Direction
          </span>

          <select
            value={
              filters.sortDirection
            }
            onChange={(event) =>
              update(
                "sortDirection",
                event.target
                  .value as ExperienceAdminFilterState["sortDirection"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="asc">
              Ascending
            </option>

            <option value="desc">
              Descending
            </option>
          </select>
        </label>
      </div>

      <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <label className="flex w-fit cursor-pointer items-center gap-3 text-sm">
          <input
            type="checkbox"
            checked={
              filters.includeDeleted
            }
            onChange={(event) =>
              update(
                "includeDeleted",
                event.target.checked
              )
            }
            className="size-4 rounded border-input"
          />

          Include deleted experiences
        </label>

        <Button
          type="button"
          variant="outline"
          onClick={
            onReset
          }
        >
          <RotateCcw
            aria-hidden="true"
          />

          Reset
        </Button>
      </div>
    </section>
  )
}