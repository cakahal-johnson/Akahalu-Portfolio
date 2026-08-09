"use client"

import {
  BadgeCheck,
  ShieldCheck,
  UserRound,
} from "lucide-react"

import type {
  AdminUserSummary,
} from "@/types/admin-user"

type AdminUserCardProps = {
  user:
    AdminUserSummary

  selected:
    boolean

  disabled?: boolean

  onSelect: () => void
}

function userDisplayName(
  user:
    AdminUserSummary
): string {
  return (
    user.display_name?.trim() ||
    `${user.first_name} ${user.last_name}`.trim() ||
    user.email
  )
}

function initials(
  user:
    AdminUserSummary
): string {
  const first =
    user.first_name
      .trim()
      .charAt(0)

  const last =
    user.last_name
      .trim()
      .charAt(0)

  const value =
    `${first}${last}`.toUpperCase()

  return value || "U"
}

function formatDate(
  value: string
): string {
  const date =
    new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return value
  }

  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle:
        "medium",
    }
  ).format(date)
}

export function AdminUserCard({
  user,
  selected,
  disabled = false,
  onSelect,
}: AdminUserCardProps) {
  return (
    <button
      type="button"
      disabled={
        disabled
      }
      onClick={
        onSelect
      }
      className={[
        "w-full rounded-2xl border bg-background p-4 text-left transition-colors",
        selected
          ? "border-primary bg-primary/5"
          : "border-border hover:bg-muted/40",
        disabled
          ? "cursor-not-allowed opacity-70"
          : "",
      ].join(" ")}
    >
      <div className="flex gap-3">
        <div className="flex size-11 shrink-0 items-center justify-center rounded-full bg-muted text-sm font-semibold">
          {initials(
            user
          )}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="truncate font-semibold">
                {userDisplayName(
                  user
                )}
              </p>

              <p className="mt-1 truncate text-sm text-muted-foreground">
                {user.email}
              </p>
            </div>

            {user.is_superuser ? (
              <ShieldCheck
                className="size-5 shrink-0 text-primary"
                aria-label="Superuser"
              />
            ) : (
              <UserRound
                className="size-5 shrink-0 text-muted-foreground"
                aria-label="Standard user"
              />
            )}
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            <span
              className={[
                "rounded-full px-2.5 py-1 text-xs font-medium",
                user.is_active
                  ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
                  : "bg-muted text-muted-foreground",
              ].join(" ")}
            >
              {user.is_active
                ? "Active"
                : "Inactive"}
            </span>

            {user.is_verified ? (
              <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                <BadgeCheck
                  className="size-3.5"
                  aria-hidden="true"
                />

                Verified
              </span>
            ) : (
              <span className="rounded-full bg-amber-500/10 px-2.5 py-1 text-xs font-medium text-amber-700 dark:text-amber-300">
                Unverified
              </span>
            )}

            {user.is_superuser ? (
              <span className="rounded-full bg-violet-500/10 px-2.5 py-1 text-xs font-medium text-violet-700 dark:text-violet-300">
                Superuser
              </span>
            ) : null}

            {user.is_deleted ? (
              <span className="rounded-full bg-destructive/10 px-2.5 py-1 text-xs font-medium text-destructive">
                Deleted
              </span>
            ) : null}
          </div>

          {user.roles.length >
          0 ? (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {user.roles
                .slice(
                  0,
                  3
                )
                .map(
                  (
                    role
                  ) => (
                    <span
                      key={
                        role.id
                      }
                      className="rounded-md border border-border px-2 py-1 text-xs text-muted-foreground"
                    >
                      {
                        role.display_name
                      }
                    </span>
                  )
                )}

              {user.roles.length >
              3 ? (
                <span className="rounded-md border border-border px-2 py-1 text-xs text-muted-foreground">
                  +
                  {user.roles.length -
                    3}
                </span>
              ) : null}
            </div>
          ) : (
            <p className="mt-3 text-xs text-muted-foreground">
              No assigned roles
            </p>
          )}

          <p className="mt-3 text-xs text-muted-foreground">
            Created{" "}
            {formatDate(
              user.created_at
            )}
          </p>
        </div>
      </div>
    </button>
  )
}