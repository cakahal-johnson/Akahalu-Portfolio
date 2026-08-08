"use client"

import {
  RotateCcw,
  Search,
} from "lucide-react"

import { Button } from "@/components/ui/button"

import type {
  ProjectAdminFilterState,
} from "@/components/admin/projects/project-admin-filters"

import type {
  ProjectCategoryRead,
  ProjectTechnologyRead,
} from "@/types/portfolio"

type AdminProjectFiltersProps = {
  filters: ProjectAdminFilterState

  categories: ProjectCategoryRead[]
  technologies: ProjectTechnologyRead[]

  onChange: (
    filters: ProjectAdminFilterState
  ) => void

  onReset: () => void
}

export function AdminProjectFilters({
  filters,
  categories,
  technologies,
  onChange,
  onReset,
}: AdminProjectFiltersProps) {
  return (
    <section className="rounded-2xl border border-border bg-background p-4 sm:p-5">
      <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
        <label className="block xl:col-span-2">
          <span className="text-sm font-medium">
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
                onChange({
                  ...filters,
                  search:
                    event.target.value,
                })
              }
              placeholder="Search title, slug or description"
              className="h-11 w-full rounded-lg border border-input bg-background pl-10 pr-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </div>
        </label>

        <label className="block">
          <span className="text-sm font-medium">
            Category
          </span>

          <select
            value={
              filters.categoryId
            }
            onChange={(event) =>
              onChange({
                ...filters,
                categoryId:
                  event.target.value,
              })
            }
            className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="">
              All categories
            </option>

            {categories.map(
              (category) => (
                <option
                  key={
                    category.id
                  }
                  value={
                    category.id
                  }
                >
                  {
                    category.name
                  }
                </option>
              )
            )}
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-medium">
            Technology
          </span>

          <select
            value={
              filters.technologyId
            }
            onChange={(event) =>
              onChange({
                ...filters,
                technologyId:
                  event.target.value,
              })
            }
            className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="">
              All technologies
            </option>

            {technologies.map(
              (technology) => (
                <option
                  key={
                    technology.id
                  }
                  value={
                    technology.id
                  }
                >
                  {
                    technology.name
                  }
                </option>
              )
            )}
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-medium">
            Status
          </span>

          <select
            value={
              filters.status
            }
            onChange={(event) =>
              onChange({
                ...filters,
                status:
                  event.target
                    .value as ProjectAdminFilterState["status"],
              })
            }
            className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="">
              All statuses
            </option>

            <option value="draft">
              Draft
            </option>

            <option value="published">
              Published
            </option>

            <option value="archived">
              Archived
            </option>
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-medium">
            Visibility
          </span>

          <select
            value={
              filters.visibility
            }
            onChange={(event) =>
              onChange({
                ...filters,
                visibility:
                  event.target
                    .value as ProjectAdminFilterState["visibility"],
              })
            }
            className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="">
              All visibility
            </option>

            <option value="public">
              Public
            </option>

            <option value="private">
              Private
            </option>
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-medium">
            Featured
          </span>

          <select
            value={
              filters.featured
            }
            onChange={(event) =>
              onChange({
                ...filters,
                featured:
                  event.target
                    .value as ProjectAdminFilterState["featured"],
              })
            }
            className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="all">
              All projects
            </option>

            <option value="true">
              Featured only
            </option>

            <option value="false">
              Not featured
            </option>
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-medium">
            Sort
          </span>

          <select
            value={
              filters.sortBy
            }
            onChange={(event) =>
              onChange({
                ...filters,
                sortBy:
                  event.target
                    .value as ProjectAdminFilterState["sortBy"],
              })
            }
            className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
          >
            <option value="created_at">
              Created
            </option>

            <option value="updated_at">
              Updated
            </option>

            <option value="title">
              Title
            </option>

            <option value="status">
              Status
            </option>

            <option value="visibility">
              Visibility
            </option>

            <option value="sort_order">
              Display order
            </option>
          </select>
        </label>

        <label className="flex items-end">
          <span className="flex h-11 w-full cursor-pointer items-center gap-3 rounded-lg border border-input px-3 text-sm">
            <input
              type="checkbox"
              checked={
                filters.includeDeleted
              }
              onChange={(event) =>
                onChange({
                  ...filters,
                  includeDeleted:
                    event.target.checked,
                })
              }
              className="size-4"
            />

            Include deleted
          </span>
        </label>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <label className="flex items-center gap-2 text-sm">
          <span className="text-muted-foreground">
            Direction:
          </span>

          <select
            value={
              filters.sortDirection
            }
            onChange={(event) =>
              onChange({
                ...filters,
                sortDirection:
                  event.target
                    .value as ProjectAdminFilterState["sortDirection"],
              })
            }
            className="h-9 rounded-lg border border-input bg-background px-2 text-sm"
          >
            <option value="desc">
              Descending
            </option>

            <option value="asc">
              Ascending
            </option>
          </select>
        </label>

        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={onReset}
        >
          <RotateCcw
            aria-hidden="true"
          />

          Reset filters
        </Button>
      </div>
    </section>
  )
}