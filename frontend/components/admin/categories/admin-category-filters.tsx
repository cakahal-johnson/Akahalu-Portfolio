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
  type CategoryAdminFilterState,
} from "@/components/admin/categories/category-admin-filters"

type AdminCategoryFiltersProps = {
  filters:
    CategoryAdminFilterState

  onChange: (
    filters:
      CategoryAdminFilterState
  ) => void

  onReset: () => void
}

export function AdminCategoryFilters({
  filters,
  onChange,
  onReset,
}: AdminCategoryFiltersProps) {
  function update<
    TKey extends keyof CategoryAdminFilterState,
  >(
    key:
      TKey,
    value:
      CategoryAdminFilterState[TKey]
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

      <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,2fr)_1fr_1fr_1fr_auto]">
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
              placeholder="Search name, slug or description"
              className="h-10 w-full rounded-lg border border-input bg-background pl-9 pr-3 text-sm outline-none transition-shadow focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </div>
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
                  .value as CategoryAdminFilterState["status"]
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
                  .value as CategoryAdminFilterState["sortBy"]
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
                  .value as CategoryAdminFilterState["sortDirection"]
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
            className="w-full lg:w-auto"
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
          Include deleted categories
        </span>
      </label>
    </section>
  )
}