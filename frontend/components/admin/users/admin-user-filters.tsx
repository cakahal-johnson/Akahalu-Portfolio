"use client"

import {
  RotateCcw,
  Search,
  SlidersHorizontal,
} from "lucide-react"

import {
  Button,
} from "@/components/ui/button"

import type {
  AdminUserFilterState,
} from "./user-admin-filters"

type AdminUserFiltersProps = {
  filters:
    AdminUserFilterState

  disabled?: boolean

  onChange: (
    filters:
      AdminUserFilterState
  ) => void

  onReset: () => void
}

export function AdminUserFilters({
  filters,
  disabled = false,
  onChange,
  onReset,
}: AdminUserFiltersProps) {
  function update<
    TKey extends keyof AdminUserFilterState,
  >(
    key: TKey,
    value:
      AdminUserFilterState[TKey]
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
              disabled={
                disabled
              }
              onChange={(
                event
              ) =>
                update(
                  "search",
                  event.target.value
                )
              }
              placeholder="Search name, display name or email"
              className="h-10 w-full rounded-lg border border-input bg-background pl-9 pr-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-60"
            />
          </div>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-muted-foreground">
            Account status
          </span>

          <select
            value={
              filters.status
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) =>
              update(
                "status",
                event.target
                  .value as AdminUserFilterState["status"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
          >
            <option value="all">
              Active + inactive
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
            Verification
          </span>

          <select
            value={
              filters.verified
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) =>
              update(
                "verified",
                event.target
                  .value as AdminUserFilterState["verified"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
          >
            <option value="all">
              All users
            </option>

            <option value="yes">
              Verified
            </option>

            <option value="no">
              Unverified
            </option>
          </select>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-muted-foreground">
            Account type
          </span>

          <select
            value={
              filters.superuser
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) =>
              update(
                "superuser",
                event.target
                  .value as AdminUserFilterState["superuser"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
          >
            <option value="all">
              All account types
            </option>

            <option value="yes">
              Superusers
            </option>

            <option value="no">
              Standard users
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
            disabled={
              disabled
            }
            onChange={(
              event
            ) =>
              update(
                "sortBy",
                event.target
                  .value as AdminUserFilterState["sortBy"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
          >
            <option value="created_at">
              Created
            </option>

            <option value="email">
              Email
            </option>

            <option value="first_name">
              First name
            </option>

            <option value="last_name">
              Last name
            </option>

            <option value="display_name">
              Display name
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
            disabled={
              disabled
            }
            onChange={(
              event
            ) =>
              update(
                "sortDirection",
                event.target
                  .value as AdminUserFilterState["sortDirection"]
              )
            }
            className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
          >
            <option value="desc">
              Descending
            </option>

            <option value="asc">
              Ascending
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
            disabled={
              disabled
            }
            onChange={(
              event
            ) =>
              update(
                "includeDeleted",
                event.target.checked
              )
            }
            className="size-4 rounded border-input"
          />

          Include deleted accounts
        </label>

        <Button
          type="button"
          variant="outline"
          disabled={
            disabled
          }
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