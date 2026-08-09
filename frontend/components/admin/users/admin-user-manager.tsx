"use client"

import {
  AlertCircle,
  Loader2, UserRound,
  Users,
} from "lucide-react"

import {
  useEffect,
  useState,
} from "react"

import {
  AdminUserCard,
} from "./admin-user-card"

import {
  AdminUserDetail,
  type AdminUserBusyAction,
} from "./admin-user-detail"

import {
  AdminUserFilters,
} from "./admin-user-filters"

import {
  defaultAdminUserFilters,
  type AdminUserBooleanFilter,
  type AdminUserFilterState,
} from "./user-admin-filters"

import {
  Button,
} from "@/components/ui/button"

import {
  useAdminSession,
} from "@/components/admin/auth/admin-session-context"

import {
  AdminApiError,
  adminUserService,
} from "@/services/admin"

import type {
  AdminUserDetail as AdminUserDetailType,
  AdminUserListResponse,
} from "@/types/admin-user"

const PAGE_SIZE =
  20

const SEARCH_DEBOUNCE_MS =
  750

function booleanFilterValue(
  value:
    AdminUserBooleanFilter
): boolean | undefined {
  if (
    value ===
    "yes"
  ) {
    return true
  }

  if (
    value ===
    "no"
  ) {
    return false
  }

  return undefined
}

function errorMessage(
  error: unknown,
  fallback: string
): string {
  if (
    error instanceof
    AdminApiError
  ) {
    return error.message
  }

  if (
    error instanceof Error
  ) {
    return error.message
  }

  return fallback
}

export function AdminUserManager() {
  const {
    user:
      currentUser,
  } =
    useAdminSession()

  const [
    filters,
    setFilters,
  ] =
    useState<AdminUserFilterState>(
      defaultAdminUserFilters
    )

  const [
    debouncedSearch,
    setDebouncedSearch,
  ] =
    useState(
      defaultAdminUserFilters.search
    )

  const [
    page,
    setPage,
  ] =
    useState(1)

  const [
    response,
    setResponse,
  ] =
    useState<AdminUserListResponse | null>(
      null
    )

  const [
    selectedUserId,
    setSelectedUserId,
  ] =
    useState<string | null>(
      null
    )

  const [
    selectedUser,
    setSelectedUser,
  ] =
    useState<AdminUserDetailType | null>(
      null
    )

  const [
    loadedListRequestKey,
    setLoadedListRequestKey,
  ] =
    useState<string | null>(
      null
    )

  const [
    loadedDetailRequestKey,
    setLoadedDetailRequestKey,
  ] =
    useState<string | null>(
      null
    )

  const [
    busyAction,
    setBusyAction,
  ] =
    useState<AdminUserBusyAction | null>(
      null
    )

  const [
    reloadVersion,
    setReloadVersion,
  ] =
    useState(0)

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null
    )

  const {
    search:
      filterSearch,

    status:
      filterStatus,

    verified:
      filterVerified,

    superuser:
      filterSuperuser,

    includeDeleted:
      filterIncludeDeleted,

    sortBy:
      filterSortBy,

    sortDirection:
      filterSortDirection,
  } =
    filters

  const listRequestKey =
    [
      page,
      debouncedSearch,
      filterStatus,
      filterVerified,
      filterSuperuser,
      filterIncludeDeleted,
      filterSortBy,
      filterSortDirection,
      reloadVersion,
    ].join("|")

  const detailRequestKey =
    selectedUserId
      ? `${selectedUserId}:${reloadVersion}`
      : null

  const loadingList =
    loadedListRequestKey !==
    listRequestKey

  const loadingDetail =
    detailRequestKey !==
      null &&
    loadedDetailRequestKey !==
      detailRequestKey

  useEffect(() => {
    if (
      filterSearch ===
      debouncedSearch
    ) {
      return
    }

    const timeoutId =
      window.setTimeout(
        () => {
          setPage(
            1
          )

          setDebouncedSearch(
            filterSearch
          )
        },
        SEARCH_DEBOUNCE_MS
      )

    return () => {
      window.clearTimeout(
        timeoutId
      )
    }
  }, [
    filterSearch,
    debouncedSearch,
  ])

  useEffect(() => {
    let cancelled =
      false

    const currentRequestKey =
      listRequestKey

    void adminUserService
      .getUsers({
        page,

        page_size:
          PAGE_SIZE,

        search:
          debouncedSearch.trim() ||
          undefined,

        status:
          filterStatus ===
          "all"
            ? undefined
            : filterStatus,

        is_verified:
          booleanFilterValue(
            filterVerified
          ),

        is_superuser:
          booleanFilterValue(
            filterSuperuser
          ),

        include_deleted:
          filterIncludeDeleted,

        sort_by:
          filterSortBy,

        sort_direction:
          filterSortDirection,
      })
      .then(
        (
          result
        ) => {
          if (
            cancelled
          ) {
            return
          }

          setResponse(
            result
          )

          setLoadedListRequestKey(
            currentRequestKey
          )

          setError(
            null
          )

          if (
            result.items.length ===
            0
          ) {
            setSelectedUser(
              null
            )
          }

          setSelectedUserId(
            (
              current
            ) => {
              if (
                current &&
                result.items.some(
                  (
                    candidate
                  ) =>
                    candidate.id ===
                    current
                )
              ) {
                return current
              }

              return (
                result.items[0]
                  ?.id ??
                null
              )
            }
          )
        }
      )
      .catch(
        (
          caughtError:
            unknown
        ) => {
          if (
            cancelled
          ) {
            return
          }

          setLoadedListRequestKey(
            currentRequestKey
          )

          setError(
            errorMessage(
              caughtError,
              "Users could not be loaded."
            )
          )
        }
      )

    return () => {
      cancelled =
        true
    }
  }, [
    page,
    debouncedSearch,
    filterStatus,
    filterVerified,
    filterSuperuser,
    filterIncludeDeleted,
    filterSortBy,
    filterSortDirection,
    reloadVersion,
    listRequestKey,
  ])

  useEffect(() => {
    if (
      !selectedUserId ||
      !detailRequestKey
    ) {
      return
    }

    let cancelled =
      false

    const currentRequestKey =
      detailRequestKey

    void adminUserService
      .getUser(
        selectedUserId,
        {
          includeDeleted:
            true,
        }
      )
      .then(
        (
          result
        ) => {
          if (
            cancelled
          ) {
            return
          }

          setSelectedUser(
            result
          )

          setLoadedDetailRequestKey(
            currentRequestKey
          )
        }
      )
      .catch(
        (
          caughtError:
            unknown
        ) => {
          if (
            cancelled
          ) {
            return
          }

          setSelectedUser(
            null
          )

          setLoadedDetailRequestKey(
            currentRequestKey
          )

          setError(
            errorMessage(
              caughtError,
              "The selected user could not be loaded."
            )
          )
        }
      )

    return () => {
      cancelled =
        true
    }
  }, [
    selectedUserId,
    detailRequestKey,
  ])

  function changeFilters(
    nextFilters:
      AdminUserFilterState
  ) {
    setError(
      null
    )

    setPage(
      1
    )

    setFilters(
      nextFilters
    )
  }

  function resetFilters() {
    setError(
      null
    )

    setPage(
      1
    )

    setDebouncedSearch(
      defaultAdminUserFilters.search
    )

    setFilters(
      defaultAdminUserFilters
    )
  }

  function changePage(
    nextPage:
      number
  ) {
    if (
      nextPage ===
      page
    ) {
      return
    }

    setError(
      null
    )

    setPage(
      nextPage
    )
  }

  async function runAction(
    action:
      AdminUserBusyAction,

    operation:
      () =>
        Promise<AdminUserDetailType>
  ) {
    if (
      busyAction
    ) {
      return
    }

    setBusyAction(
      action
    )

    setError(
      null
    )

    try {
      const updated =
        await operation()

      setSelectedUser(
        updated
      )

      setReloadVersion(
        (
          current
        ) =>
          current + 1
      )
    } catch (
      caughtError
    ) {
      setError(
        errorMessage(
          caughtError,
          "The user account could not be updated."
        )
      )
    } finally {
      setBusyAction(
        null
      )
    }
  }

  async function updateStatus(
    isActive:
      boolean
  ) {
    if (
      !selectedUserId ||
      selectedUserId ===
        currentUser.id
    ) {
      return
    }

    const verb =
      isActive
        ? "activate"
        : "deactivate"

    const confirmed =
      window.confirm(
        `Are you sure you want to ${verb} this user account?`
      )

    if (
      !confirmed
    ) {
      return
    }

    await runAction(
      "status",
      () =>
        adminUserService.updateStatus(
          selectedUserId,
          {
            is_active:
              isActive,

            reason:
              isActive
                ? "Account activated from User Administration."
                : "Account deactivated from User Administration.",
          }
        )
    )
  }

  async function deleteUser() {
    if (
      !selectedUserId ||
      selectedUserId ===
        currentUser.id
    ) {
      return
    }

    const confirmed =
      window.confirm(
        "Delete this user account?\n\nThe account will be soft-deleted and its active sessions will be revoked. It can be restored later."
      )

    if (
      !confirmed
    ) {
      return
    }

    await runAction(
      "delete",
      () =>
        adminUserService.deleteUser(
          selectedUserId,
          {
            reason:
              "Account deleted from User Administration.",
          }
        )
    )

    setPage(
      1
    )

    setFilters(
      (
        current
      ) => ({
        ...current,

        includeDeleted:
          true,
      })
    )
  }

  async function restoreUser(
    activate:
      boolean
  ) {
    if (
      !selectedUserId
    ) {
      return
    }

    await runAction(
      activate
        ? "restore-active"
        : "restore-inactive",
      () =>
        adminUserService.restoreUser(
          selectedUserId,
          {
            activate,

            reason:
              activate
                ? "Account restored as active from User Administration."
                : "Account restored as inactive from User Administration.",
          }
        )
    )
  }

  const items =
    response?.items ??
    []

  const selectedUserIsCurrent =
    selectedUser !==
      null &&
    selectedUser.id ===
      selectedUserId

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
          Account administration
        </p>

        <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
          Manage users
        </h1>

        <p className="mt-4 max-w-3xl leading-7 text-muted-foreground">
          Review administrator and user
          accounts, inspect assigned roles
          and permissions, manage account
          status, and safely restore or
          remove access.
        </p>
      </div>

      <AdminUserFilters
        filters={
          filters
        }
        disabled={
          Boolean(
            busyAction
          )
        }
        onChange={
          changeFilters
        }
        onReset={
          resetFilters
        }
      />

      {error ? (
        <div
          role="alert"
          className="flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive"
        >
          <AlertCircle
            className="mt-0.5 size-4 shrink-0"
            aria-hidden="true"
          />

          {error}
        </div>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[390px_minmax(0,1fr)]">
        <section className="space-y-4">
          <div className="flex items-end justify-between gap-3">
            <div>
              <h2 className="font-semibold">
                Accounts
              </h2>

              <p className="mt-1 text-sm text-muted-foreground">
                {response
                  ? `${response.total_items} matching account${response.total_items === 1 ? "" : "s"}`
                  : "Loading accounts..."}
              </p>
            </div>

            {loadingList ? (
              <span className="inline-flex items-center gap-2 text-xs text-muted-foreground">
                <Loader2
                  className="size-3.5 animate-spin"
                  aria-hidden="true"
                />

                Refreshing
              </span>
            ) : null}
          </div>

          {items.length >
          0 ? (
            <div className="space-y-3">
              {items.map(
                (
                  user
                ) => (
                  <AdminUserCard
                    key={
                      user.id
                    }
                    user={
                      user
                    }
                    selected={
                      user.id ===
                      selectedUserId
                    }
                    disabled={
                      Boolean(
                        busyAction
                      )
                    }
                    onSelect={() => {
                      setError(
                        null
                      )

                      setSelectedUserId(
                        user.id
                      )
                    }}
                  />
                )
              )}
            </div>
          ) : loadingList ? (
            <div className="flex min-h-56 items-center justify-center rounded-2xl border border-border bg-background">
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Loader2
                  className="size-5 animate-spin"
                  aria-hidden="true"
                />

                Loading users...
              </div>
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border bg-background p-10 text-center">
              <Users
                className="mx-auto size-8 text-muted-foreground"
                aria-hidden="true"
              />

              <h2 className="mt-4 font-semibold">
                No users found
              </h2>

              <p className="mt-2 text-sm text-muted-foreground">
                Try changing the current
                search or filters.
              </p>
            </div>
          )}

          {response &&
          response.total_pages >
            0 ? (
            <div className="flex flex-col gap-3 rounded-xl border border-border bg-background p-4 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-muted-foreground">
                Page{" "}
                {
                  response.page
                }{" "}
                of{" "}
                {
                  response.total_pages
                }
              </p>

              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={
                    !response.has_previous_page ||
                    loadingList
                  }
                  onClick={() =>
                    changePage(
                      page - 1
                    )
                  }
                >
                  Previous
                </Button>

                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={
                    !response.has_next_page ||
                    loadingList
                  }
                  onClick={() =>
                    changePage(
                      page + 1
                    )
                  }
                >
                  Next
                </Button>
              </div>
            </div>
          ) : null}
        </section>

        <div className="min-w-0 xl:sticky xl:top-6 xl:self-start">
          {loadingDetail ? (
            <div className="flex min-h-72 items-center justify-center rounded-2xl border border-border bg-background">
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Loader2
                  className="size-5 animate-spin"
                  aria-hidden="true"
                />

                Loading account...
              </div>
            </div>
          ) : selectedUserIsCurrent &&
            selectedUser ? (
            <AdminUserDetail
              key={`${selectedUser.id}:${selectedUser.updated_at}:${selectedUser.deleted_at ?? ""}:${selectedUser.is_active}`}
              user={
                selectedUser
              }
              currentUserId={
                currentUser.id
              }
              busyAction={
                busyAction
              }
              onStatus={
                updateStatus
              }
              onDelete={
                deleteUser
              }
              onRestore={
                restoreUser
              }
            />
          ) : (
            <div className="rounded-2xl border border-dashed border-border bg-background p-10 text-center">
              <UserRound
                className="mx-auto size-8 text-muted-foreground"
                aria-hidden="true"
              />

              <h2 className="mt-4 font-semibold">
                Select a user
              </h2>

              <p className="mt-2 text-sm text-muted-foreground">
                Choose an account to inspect
                its roles, permissions and
                lifecycle.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}