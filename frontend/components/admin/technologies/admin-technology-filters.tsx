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
  type TechnologyAdminFilterState,
} from "@/components/admin/technologies/technology-admin-filters"

type AdminTechnologyFiltersProps = {
  filters:
    TechnologyAdminFilterState

  onChange: (
    filters:
      TechnologyAdminFilterState
  ) => void

  onReset: () => void
}

export function AdminTechnologyFilters({
  filters,
  onChange,
  onReset,
}: AdminTechnologyFiltersProps) {
  function update<
    TKey extends keyof TechnologyAdminFilterState,
  >(
    key:
      TKey,
    value:
      TechnologyAdminFilterState[TKey]
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

      <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,2fr)_1fr_1fr_1fr_1fr_auto]">
        <label className="block">
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
              placeholder="Search name, slug, description or category"
              className="h-10 w-full rounded-lg border border-input bg-background pl-9 pr-3 text-sm outline-none transition-shadow focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </div>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-muted-foreground">
            Category
          </span>

          <select
            value={
              filters.category
            }
            onChange={(event) =>
              update(
                "category",
                event.target
                  .value as TechnologyAdminFilterState["category"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="all">
              All categories
            </option>

            <option value="language">
              Language
            </option>

            <option value="framework">
              Framework
            </option>

            <option value="library">
              Library
            </option>

            <option value="database">
              Database
            </option>

            <option value="platform">
              Platform
            </option>

            <option value="cloud">
              Cloud
            </option>

            <option value="devops">
              DevOps
            </option>

            <option value="testing">
              Testing
            </option>

            <option value="tool">
              Tool
            </option>

            <option value="service">
              Service
            </option>

            <option value="other">
              Other
            </option>
          </select>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-muted-foreground">
            Status
          </span>

          <select
            value={
              filters.status
            }
            onChange={(event) =>
              update(
                "status",
                event.target
                  .value as TechnologyAdminFilterState["status"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="all">
              All statuses
            </option>

            <option value="active">
              Active
            </option>

            <option value="inactive">
              Inactive
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
                  .value as TechnologyAdminFilterState["sortBy"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="sort_order">
              Sort order
            </option>

            <option value="name">
              Name
            </option>

            <option value="slug">
              Slug
            </option>

            <option value="category">
              Category
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
                  .value as TechnologyAdminFilterState["sortDirection"]
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

        <div className="flex items-end">
          <Button
            type="button"
            variant="outline"
            className="w-full xl:w-auto"
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
      </div>

      <label className="mt-4 flex w-fit cursor-pointer items-center gap-3 text-sm">
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

        <span>
          Include deleted technologies
        </span>
      </label>
    </section>
  )
}