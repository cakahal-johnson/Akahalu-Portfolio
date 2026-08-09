"use client"

import {
  BadgeCheck,
  Ban,
  RotateCcw,
  ShieldCheck,
  Trash2,
  UserRound,
} from "lucide-react"

import {
  Button,
} from "@/components/ui/button"

import type {
  AdminUserDetail as AdminUserDetailType,
} from "@/types/admin-user"

export type AdminUserBusyAction =
  | "status"
  | "delete"
  | "restore-active"
  | "restore-inactive"

type AdminUserDetailProps = {
  user:
    AdminUserDetailType

  currentUserId:
    string

  busyAction:
    AdminUserBusyAction | null

  onStatus: (
    isActive:
      boolean
  ) => Promise<void>

  onDelete:
    () => Promise<void>

  onRestore: (
    activate:
      boolean
  ) => Promise<void>
}

function displayName(
  user:
    AdminUserDetailType
): string {
  return (
    user.display_name?.trim() ||
    `${user.first_name} ${user.last_name}`.trim() ||
    user.email
  )
}

function formatDateTime(
  value:
    string | null
): string {
  if (!value) {
    return "—"
  }

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

      timeStyle:
        "short",
    }
  ).format(date)
}

export function AdminUserDetail({
  user,
  currentUserId,
  busyAction,
  onStatus,
  onDelete,
  onRestore,
}: AdminUserDetailProps) {
  const isSelf =
    user.id ===
    currentUserId

  const isBusy =
    busyAction !== null

  return (
    <section className="rounded-2xl border border-border bg-background shadow-sm">
      <div className="border-b border-border p-5 sm:p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xl font-bold tracking-tight">
                {displayName(
                  user
                )}
              </h2>

              {isSelf ? (
                <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                  Your account
                </span>
              ) : null}

              {user.is_deleted ? (
                <span className="rounded-full bg-destructive/10 px-2.5 py-1 text-xs font-medium text-destructive">
                  Deleted
                </span>
              ) : null}
            </div>

            <p className="mt-2 text-sm text-muted-foreground">
              {user.email}
            </p>
          </div>

          <div
            className={[
              "flex size-12 shrink-0 items-center justify-center rounded-full",
              user.is_superuser
                ? "bg-primary/10 text-primary"
                : "bg-muted text-muted-foreground",
            ].join(" ")}
          >
            {user.is_superuser ? (
              <ShieldCheck
                className="size-6"
                aria-hidden="true"
              />
            ) : (
              <UserRound
                className="size-6"
                aria-hidden="true"
              />
            )}
          </div>
        </div>
      </div>

      <div className="space-y-6 p-5 sm:p-6">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Account
          </p>

          <dl className="mt-4 grid gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-xs text-muted-foreground">
                First name
              </dt>

              <dd className="mt-1 text-sm font-medium">
                {user.first_name}
              </dd>
            </div>

            <div>
              <dt className="text-xs text-muted-foreground">
                Last name
              </dt>

              <dd className="mt-1 text-sm font-medium">
                {user.last_name}
              </dd>
            </div>

            <div>
              <dt className="text-xs text-muted-foreground">
                Display name
              </dt>

              <dd className="mt-1 text-sm font-medium">
                {user.display_name ??
                  "—"}
              </dd>
            </div>

            <div>
              <dt className="text-xs text-muted-foreground">
                Account type
              </dt>

              <dd className="mt-1 text-sm font-medium">
                {user.is_superuser
                  ? "Superuser"
                  : "Standard user"}
              </dd>
            </div>
          </dl>
        </div>

        <div className="border-t border-border pt-5">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Account state
          </p>

          <div className="mt-4 flex flex-wrap gap-2">
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
          </div>

          <dl className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between gap-4">
              <dt className="text-muted-foreground">
                Last login
              </dt>

              <dd className="text-right">
                {formatDateTime(
                  user.last_login_at
                )}
              </dd>
            </div>

            <div className="flex justify-between gap-4">
              <dt className="text-muted-foreground">
                Created
              </dt>

              <dd className="text-right">
                {formatDateTime(
                  user.created_at
                )}
              </dd>
            </div>

            <div className="flex justify-between gap-4">
              <dt className="text-muted-foreground">
                Updated
              </dt>

              <dd className="text-right">
                {formatDateTime(
                  user.updated_at
                )}
              </dd>
            </div>

            <div className="flex justify-between gap-4">
              <dt className="text-muted-foreground">
                Deleted
              </dt>

              <dd className="text-right">
                {formatDateTime(
                  user.deleted_at
                )}
              </dd>
            </div>
          </dl>
        </div>

        <div className="border-t border-border pt-5">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Roles & permissions
          </p>

          {user.roles.length >
          0 ? (
            <div className="mt-4 space-y-3">
              {user.roles.map(
                (
                  role
                ) => (
                  <details
                    key={
                      role.id
                    }
                    className="rounded-xl border border-border p-4"
                  >
                    <summary className="cursor-pointer">
                      <span className="font-medium">
                        {
                          role.display_name
                        }
                      </span>

                      <span className="ml-2 text-xs text-muted-foreground">
                        {role.permissions.length}{" "}
                        permission
                        {role.permissions.length ===
                        1
                          ? ""
                          : "s"}
                      </span>
                    </summary>

                    <div className="mt-3">
                      <p className="text-xs text-muted-foreground">
                        {role.description ??
                          "No role description."}
                      </p>

                      {role.permissions.length >
                      0 ? (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {role.permissions.map(
                            (
                              permission
                            ) => (
                              <span
                                key={
                                  permission.id
                                }
                                className="rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground"
                              >
                                {
                                  permission.code
                                }
                              </span>
                            )
                          )}
                        </div>
                      ) : (
                        <p className="mt-3 text-xs text-muted-foreground">
                          No permissions
                          assigned.
                        </p>
                      )}
                    </div>
                  </details>
                )
              )}
            </div>
          ) : (
            <p className="mt-4 text-sm text-muted-foreground">
              This account has no assigned roles.
            </p>
          )}

          <p className="mt-3 text-xs text-muted-foreground">
            Role and permission assignments are read-only in this administration view.
          </p>
        </div>

        <div className="border-t border-border pt-5">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Lifecycle
          </p>

          {isSelf &&
          !user.is_deleted ? (
            <div className="mt-4 rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 text-sm text-amber-800 dark:text-amber-200">
              Your own account cannot be
              deactivated or deleted from
              User Administration.
            </div>
          ) : null}

          {user.is_deleted ? (
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <Button
                type="button"
                disabled={
                  isBusy
                }
                onClick={() => {
                  void onRestore(
                    true
                  )
                }}
              >
                <RotateCcw
                  aria-hidden="true"
                />

                {busyAction ===
                "restore-active"
                  ? "Restoring..."
                  : "Restore active"}
              </Button>

              <Button
                type="button"
                variant="outline"
                disabled={
                  isBusy
                }
                onClick={() => {
                  void onRestore(
                    false
                  )
                }}
              >
                <RotateCcw
                  aria-hidden="true"
                />

                {busyAction ===
                "restore-inactive"
                  ? "Restoring..."
                  : "Restore inactive"}
              </Button>
            </div>
          ) : (
            <div className="mt-4 space-y-3">
              <Button
                type="button"
                variant={
                  user.is_active
                    ? "outline"
                    : "default"
                }
                disabled={
                  isBusy ||
                  isSelf
                }
                onClick={() => {
                  void onStatus(
                    !user.is_active
                  )
                }}
                className="w-full"
              >
                <Ban
                  aria-hidden="true"
                />

                {busyAction ===
                "status"
                  ? "Updating..."
                  : user.is_active
                    ? "Deactivate account"
                    : "Activate account"}
              </Button>

              <Button
                type="button"
                variant="outline"
                disabled={
                  isBusy ||
                  isSelf
                }
                onClick={() => {
                  void onDelete()
                }}
                className="w-full border-destructive/40 text-destructive hover:bg-destructive/10 hover:text-destructive"
              >
                <Trash2
                  aria-hidden="true"
                />

                {busyAction ===
                "delete"
                  ? "Deleting..."
                  : "Delete account"}
              </Button>
            </div>
          )}

          <p className="mt-3 text-xs leading-5 text-muted-foreground">
            Deactivating or deleting an
            account revokes its active
            sessions and refresh tokens.
            The backend also prevents
            removal of the last active
            administrator.
          </p>
        </div>
      </div>
    </section>
  )
}